import io
from pathlib import Path
import shutil
import tempfile
import unittest

from fastapi.testclient import TestClient
from studio_api.app import create_app
from studio_core.models import Project, Fact, Beat
from studio_core.development import FilmIdea, StoryOption, Chapter, Subchapter
from studio_core.media import import_media
from studio_core.bundles import export_bundle, import_bundle
from studio_core.exports import workbook, read_workbook
from studio_core.store import Conflict

H = {'X-Docos-Request': '1'}


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.app = create_app(self.root, seed_demo=False)
        self.client = TestClient(self.app)
        self.store = self.app.state.store
        self.w = self.app.state.workspace

    def tearDown(self):
        self.app.state.jobs.close()
        self.client.close()
        self.temp.cleanup()

    def new(self, **body):
        response = self.client.post('/api/projects', json=body, headers=H)
        self.assertEqual(response.status_code, 200, response.text)
        return Project.model_validate(response.json())

    def source_project(self):
        p = self.store.create(Project(title='Źródłowy film', development={}))
        path = self.root / 'test.txt'
        path.write_text('Kontrolowany materiał testowy. Strona źródłowa.', encoding='utf-8')
        asset, source = import_media(self.store, p.id, path, 'test.txt')
        p = self.store.get(p.id)
        fact = Fact(claim='Kontrolowane twierdzenie', source='Źródło testowe', source_id=source.id, status='VERIFIED', page='1', quote='Kontrolowany materiał testowy.')
        p = self.store.patch(p.id, p.revision, {'facts': [fact.model_dump()]})
        return p, fact, source, asset

    def test_new_film_is_empty_and_rejects_content_in_creation_body(self):
        old, *_ = self.source_project()
        p = self.new(title='Nowy film')
        self.assertFalse(p.facts or p.sources or p.assets or p.beats or p.scenes or p.sequence.clips or p.development.ideas or p.resource_links)
        self.assertEqual(self.store.get(old.id).facts, old.facts)
        bad = self.client.post('/api/projects', json={'title': 'Nie kopiuj', 'facts': [old.facts[0].model_dump()]}, headers=H)
        self.assertEqual(bad.status_code, 422)

    def test_settings_precedence_and_independent_snapshots(self):
        self.w.save_defaults({'revision': 0, 'preset': {'target_minutes': 10, 'font': 'courier', 'audience': 'Widz pracowni'}})
        channel = self.store.save_channel({'name': 'Kanał', 'language': 'en', 'font': 'montserrat'})
        category = self.w.save_category({'name': 'Psychologia', 'channel_id': channel['id'], 'defaults': {'target_minutes': 12}})
        template = self.w.save({'title': 'Struktura', 'kind': 'template', 'payload': {'preset': {'target_minutes': 15}, 'chapters': [Chapter(title='Pytanie', sections=[Subchapter(title='Obietnica')]).model_dump()]}})
        p = self.new(title='Odcinek', channel_id=channel['id'], category_id=category.id, template_id=template.id, language='pl')
        self.assertEqual(p.language, 'pl'); self.assertEqual(p.development.target_minutes, 15); self.assertEqual(p.channel_profile['font'], 'montserrat')
        self.assertFalse(p.facts or p.sources or p.assets or p.scenes or p.beats)
        self.assertEqual(len(p.development.ideas[0].stories[0].chapters), 1)
        another = self.new(title='Drugi', channel_id=channel['id'], category_id=category.id, template_id=template.id)
        self.assertNotEqual(p.development.ideas[0].stories[0].chapters[0].id, another.development.ideas[0].stories[0].chapters[0].id)
        category.defaults.target_minutes = 30
        self.w.save_category(category.model_dump())
        self.assertEqual(self.store.get(p.id).category_profile['defaults']['target_minutes'], 12)
        self.assertEqual(self.store.get(p.id).development.target_minutes, 15)

    def test_import_fact_copies_dependencies_and_preserves_bank_review_as_provenance(self):
        original, fact, source, asset = self.source_project()
        resource = self.w.publish(original.id, {'expected_revision': original.revision, 'kind': 'fact', 'item_id': fact.id, 'title': 'Wiedza'})
        p = self.new(title='Nowy')
        p = self.w.import_resource(p.id, resource.id, {'expected_revision': p.revision})
        self.assertNotEqual(p.facts[0].id, fact.id)
        self.assertEqual(p.facts[0].source_id, p.sources[0].id)
        self.assertEqual(p.sources[0].asset_id, p.assets[0].id)
        self.assertEqual(p.facts[0].status, 'UNVERIFIED')
        self.assertEqual(p.facts[0].provenance['bank_status'], 'VERIFIED')
        self.assertTrue(p.facts[0].provenance['review_required'])
        self.assertTrue((self.store.folder(p.id) / 'media' / asset.filename).is_file())
        p = self.w.import_resource(p.id, resource.id, {'expected_revision': p.revision})
        self.assertEqual((len(p.facts), len(p.sources), len(p.assets)), (1, 1, 1))
        values = p.facts[0].model_dump() | {'status': 'VERIFIED'}
        p = self.store.patch(p.id, p.revision, {'facts': [values]})
        self.assertFalse(p.facts[0].provenance['review_required'])
        self.assertEqual(self.w.get(resource.id).payload['facts'][0]['status'], 'VERIFIED')

    def test_bank_update_is_explicit_version_checked_and_never_retroactive(self):
        original, fact, *_ = self.source_project()
        resource = self.w.publish(original.id, {'expected_revision': original.revision, 'kind': 'fact', 'item_id': fact.id, 'title': 'Wiedza'})
        p = self.new(title='Nowy'); p = self.w.import_resource(p.id, resource.id, {'expected_revision': p.revision})
        old_local = p.facts[0].id
        change = resource.model_dump(); change['payload']['facts'][0]['claim'] = 'Zmienione twierdzenie'
        updated = self.w.save(change)
        self.assertEqual(updated.payload['facts'][0]['status'], 'UNVERIFIED')
        self.assertEqual(self.store.get(p.id).facts[0].claim, fact.claim)
        self.assertTrue(self.w.links(p.id)[0]['update_available'])
        with self.assertRaises(ValueError): self.w.import_resource(p.id, resource.id, {'expected_revision': p.revision})
        p = self.w.import_resource(p.id, resource.id, {'expected_revision': p.revision, 'update': True})
        self.assertEqual(p.facts[0].id, old_local); self.assertEqual(p.facts[0].claim, 'Zmienione twierdzenie')
        self.assertEqual(self.w.get(resource.id, 1).payload['facts'][0]['claim'], fact.claim)
        with self.assertRaises(Conflict): self.w.save(change)
        with self.assertRaises(Conflict): self.w.import_resource(p.id, resource.id, {'expected_revision': 1})

    def test_bank_and_other_films_survive_source_project_deletion_and_local_edits(self):
        original, fact, *_ = self.source_project()
        r = self.w.publish(original.id, {'expected_revision': original.revision, 'kind': 'fact', 'item_id': fact.id, 'title': 'Wiedza'})
        shutil.rmtree(self.store.folder(original.id))
        first, second = self.new(title='Pierwszy'), self.new(title='Drugi')
        first = self.w.import_resource(first.id, r.id, {'expected_revision': first.revision})
        second = self.w.import_resource(second.id, r.id, {'expected_revision': second.revision})
        self.store.patch(first.id, first.revision, {'facts': [first.facts[0].model_dump() | {'claim': 'Lokalna redakcja'}]})
        self.assertEqual(self.store.get(second.id).facts[0].claim, fact.claim)
        self.assertEqual(self.w.get(r.id).payload['facts'][0]['claim'], fact.claim)
        self.assertTrue((self.store.folder(second.id) / 'media' / second.assets[0].filename).exists())

    def test_bank_project_export_roundtrip_without_original_bank(self):
        original, fact, *_ = self.source_project()
        r = self.w.publish(original.id, {'expected_revision': original.revision, 'kind': 'fact', 'item_id': fact.id, 'title': 'Wiedza'})
        p = self.new(title='Film'); p = self.w.import_resource(p.id, r.id, {'expected_revision': p.revision})
        package = export_bundle(self.store, p)
        other_store = type(self.store)(self.root / 'another-workspace')
        restored = import_bundle(other_store, package)
        self.assertEqual(restored.resource_links, p.resource_links); self.assertEqual(restored.facts, p.facts)
        self.assertEqual(read_workbook(workbook(p)).resource_links, p.resource_links)
        self.assertTrue((other_store.folder(restored.id) / 'media' / restored.assets[0].filename).exists())

    def test_archive_is_recoverable_and_does_not_remove_film_snapshots(self):
        r = self.w.save({'title': 'Notatka', 'kind': 'note', 'payload': {'text': 'Research'}})
        p = self.new(); p = self.w.import_resource(p.id, r.id, {'expected_revision': p.revision})
        archived = self.w.save(r.model_dump() | {'archived': True})
        self.assertFalse(self.w.resources()); self.assertEqual(self.store.get(p.id).sources[0].text, 'Research')
        self.assertTrue(self.w.links(p.id)[0]['archived'])
        with self.assertRaises(ValueError): self.w.import_resource(p.id, r.id, {'expected_revision': p.revision})
        self.w.save(archived.model_dump() | {'archived': False}); self.assertEqual(len(self.w.resources()), 1)

    def test_reusable_template_excludes_actual_story_facts_and_ratings(self):
        p = self.new(title='Film')
        story = StoryOption(title='Konkretny tytuł', synopsis='Prywatna fabuła', chapters=[Chapter(title='Konkretne odkrycie', sections=[Subchapter(title='Konkretny dowód', purpose='Opis epizodu', seconds=90)])])
        p = self.store.patch(p.id, p.revision, {'development': {'ideas': [FilmIdea(title='Pomysł', stories=[story]).model_dump()]}})
        r = self.w.publish(p.id, {'expected_revision': p.revision, 'kind': 'template', 'item_id': story.id, 'title': 'Układ'})
        self.assertNotIn('Prywatna fabuła', str(r.payload)); self.assertNotIn('Konkretny', str(r.payload)); self.assertNotIn('scores', r.payload)
        self.assertEqual(r.payload['chapters'][0]['sections'][0]['seconds'], 90)
        with self.assertRaises(ValueError): self.w.save({'title': 'Zły szablon', 'kind': 'template', 'payload': {'narration': 'Nie kopiuj'}})
        with self.assertRaises(ValueError): self.w.save({'title': 'Zły szablon', 'kind': 'template', 'payload': {'chapters': [Chapter(sections=[Subchapter(fact_ids=['fact_hidden'])]).model_dump()]}})

    def test_template_application_requires_explicit_scope_and_preserves_other_content(self):
        p = self.new(title='Film'); p = self.store.patch(p.id, p.revision, {'beats': [Beat(narration='Zachowaj tekst').model_dump()]})
        r = self.w.save({'title': 'Profil', 'kind': 'template', 'payload': {'preset': {'target_minutes': 22}}})
        with self.assertRaises(ValueError): self.w.import_resource(p.id, r.id, {'expected_revision': p.revision})
        p = self.w.import_resource(p.id, r.id, {'expected_revision': p.revision, 'apply_settings': True})
        self.assertEqual(p.beats[0].narration, 'Zachowaj tekst'); self.assertEqual(p.development.target_minutes, 22)

    def test_bank_datasets_reject_forecast_fields_and_are_snapshot_based(self):
        with self.assertRaises(ValueError): self.w.save({'title': 'Błędne dane', 'kind': 'baseline', 'payload': {'views_30d': {'low': 1000, 'base': 2000}, 'confidence': 'scenario_only'}})
        r = self.w.save({'title': 'Wyniki', 'kind': 'baseline', 'payload': {'views_30d': [100, 200, 300], 'evidence': 'Wyniki testowe'}})
        p = self.new(); p = self.w.import_resource(p.id, r.id, {'expected_revision': p.revision})
        change = r.model_dump(); change['payload']['views_30d'].append(400); self.w.save(change)
        self.assertEqual(self.store.get(p.id).development.baseline.views_30d, [100, 200, 300])

    def test_global_bank_upload_creates_no_visible_staging_film(self):
        r = self.client.post('/api/workspace/media', files={'file': ('reference.txt', io.BytesIO(b'Controlled reference'), 'text/plain')}, headers=H)
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()['kind'], 'source'); self.assertEqual(self.store.list(), [])
        p = self.new(); r2 = self.client.post(f'/api/projects/{p.id}/workspace/import/{r.json()["id"]}', json={'expected_revision': p.revision}, headers=H)
        self.assertEqual(r2.status_code, 200, r2.text); self.assertEqual(r2.json()['sources'][0]['text'], 'Controlled reference')

    def test_overview_is_global_and_does_not_leak_full_document_text_in_cards(self):
        self.w.save({'title': 'Notatka', 'kind': 'note', 'payload': {'text': 'Długi tekst'}})
        result = self.client.get('/api/workspace')
        self.assertEqual(result.status_code, 200); self.assertNotIn('payload', result.json()['resources'][0])
        with self.assertRaises(ValueError): self.w.save({'title': 'Błędny zakres', 'kind': 'note', 'scope': 'category', 'payload': {'text': 'x'}})
        category = self.w.save_category({'name': 'Nauka'})
        self.w.save_category(category.model_dump() | {'description': 'Zmieniony'})
        with self.assertRaises(Conflict): self.w.save_category(category.model_dump())

    def test_two_bank_facts_share_one_dependency_in_the_target_film(self):
        original, fact, source, asset = self.source_project()
        second_fact = Fact(claim='Drugie kontrolowane twierdzenie', source=source.title, source_id=source.id)
        original = self.store.patch(original.id, original.revision, {'facts': [fact.model_dump(), second_fact.model_dump()]})
        resources = [self.w.publish(original.id, {'expected_revision': original.revision, 'kind': 'fact', 'item_id': f.id, 'title': f.claim}) for f in (fact, second_fact)]
        p = self.new()
        for resource in resources: p = self.w.import_resource(p.id, resource.id, {'expected_revision': p.revision})
        self.assertEqual((len(p.facts), len(p.sources), len(p.assets)), (2, 1, 1))
        self.assertEqual(p.facts[0].source_id, p.facts[1].source_id)
        self.assertTrue(all(self.w.usages()[r.id][0]['project_id'] == p.id for r in resources))

    def test_bank_import_is_undoable_and_saved_versions_keep_resource_provenance(self):
        p = self.new(); resource = self.w.save({'kind': 'note', 'title': 'Research', 'payload': {'text': 'Notatka'}})
        imported = self.w.import_resource(p.id, resource.id, {'expected_revision': p.revision})
        saved = self.store.save_version(p.id, 'Z researchu')
        undone = self.store.restore(p.id, imported.revision, 'undo')
        self.assertFalse(undone.sources or undone.resource_links)
        restored = self.store.restore_version(p.id, undone.revision, saved['id'])
        self.assertEqual(restored.resource_links, imported.resource_links)
        self.assertEqual(restored.sources, imported.sources)

    def test_private_files_do_not_enter_shared_bank(self):
        p, fact, source, asset = self.source_project()
        def make_private(current): current.assets[0].private = True
        p = self.store.mutate(p.id, p.revision, make_private)
        with self.assertRaises(ValueError): self.w.publish(p.id, {'expected_revision': p.revision, 'kind': 'media', 'item_id': asset.id, 'title': 'Prywatny'})
        with self.assertRaises(ValueError): self.w.publish(p.id, {'expected_revision': p.revision, 'kind': 'fact', 'item_id': fact.id, 'title': 'Z prywatnym źródłem'})
        self.assertFalse(self.w.resources())


if __name__ == '__main__': unittest.main()
