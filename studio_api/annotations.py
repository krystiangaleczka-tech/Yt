from fractions import Fraction

from studio_core.annotations import FrameAnnotation
from studio_core.store import now


def register_annotations(app, store):
    @app.post('/api/projects/{pid}/frame-annotations')
    def add_annotation(pid: str, body: dict):
        def change(project):
            raw = {key: value for key, value in body.items() if key != 'expected_revision'}
            annotation = FrameAnnotation.model_validate({
                'fps_num': project.sequence.fps_num, 'fps_den': project.sequence.fps_den,
                **raw, 'created_at': now(), 'updated_at': now(),
            })
            scene = next((s for s in [*project.scenes, *project.stage_scenes] if s.id == annotation.scene_id), None)
            if scene is None:
                raise ValueError('Nie ma takiego ujęcia')
            duration = (Fraction(scene.duration * project.sequence.fps_den, project.sequence.fps_num)
                        if hasattr(scene, 'duration') else Fraction(str(scene.seconds)))
            if Fraction(annotation.frame * annotation.fps_den, annotation.fps_num) >= duration:
                raise ValueError('Uwaga musi wskazywać klatkę wewnątrz ujęcia')
            existing = next((a for a in project.frame_annotations if a.id == annotation.id), None)
            if existing:
                if (existing.scene_id, existing.frame, existing.fps_num, existing.fps_den) != (
                        annotation.scene_id, annotation.frame, annotation.fps_num, annotation.fps_den):
                    raise ValueError('Identyfikator uwagi wskazuje inną klatkę')
                # Retrying after a lost response must not duplicate the marker.
                existing.text, existing.strokes = annotation.text, annotation.strokes
                existing.updated_at = now()
            else:
                project.frame_annotations.append(annotation)
        return store.mutate(pid, int(body['expected_revision']), change)

    @app.patch('/api/projects/{pid}/frame-annotations/{annotation_id}')
    def edit_annotation(pid: str, annotation_id: str, body: dict):
        changes = body.get('changes', {})
        if not isinstance(changes, dict) or not changes or not set(changes) <= {'text', 'strokes'}:
            raise ValueError('Zmieniaj tekst lub zaznaczenie uwagi')
        def change(project):
            existing = next((a for a in project.frame_annotations if a.id == annotation_id), None)
            if existing is None:
                raise ValueError('Nie ma takiej uwagi w tym filmie')
            replacement = FrameAnnotation.model_validate(existing.model_dump() | changes | {'updated_at': now()})
            project.frame_annotations = [replacement if a.id == annotation_id else a for a in project.frame_annotations]
        return store.mutate(pid, int(body['expected_revision']), change)

    @app.delete('/api/projects/{pid}/frame-annotations/{annotation_id}')
    def remove_annotation(pid: str, annotation_id: str, body: dict):
        def change(project):
            if not any(a.id == annotation_id for a in project.frame_annotations):
                raise ValueError('Nie ma takiej uwagi w tym filmie')
            project.frame_annotations = [a for a in project.frame_annotations if a.id != annotation_id]
        return store.mutate(pid, int(body['expected_revision']), change)
