"""Actual frame review, explicit authorship and stale approval/export protection."""
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw
from studio_api.app import create_app
from studio_core.models import Clip
from studio_core import paper_theatre_review as review
from studio_core.quality import check_project

HEADERS = {'X-Docos-Request': '1'}


class PaperReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = create_app(Path(self.temp.name), seed_demo=False)
        self.client = TestClient(self.app)
        p = self.client.post('/api/projects', json={'title': 'Review'}, headers=HEADERS).json()
        self.pid = p['id']; self.base = '/api/projects/' + self.pid
        def image(name, alpha=False):
            im = Image.new('RGBA' if alpha else 'RGB', (320,180), (0,0,0,0) if alpha else '#ab956c')
            if alpha: ImageDraw.Draw(im).rectangle((140,80,180,140), fill='#bb3300')
            data = io.BytesIO(); im.save(data, format='PNG')
            return self.client.post(self.base+'/media', files={'file':(name+'.png',data.getvalue(),'image/png')},headers=HEADERS).json()['asset']['id']
        self.bg = image('background'); self.cloud = image('cloud', True)
        p = self.get()
        p = self.post('/paper-theatre/scenes', {'expected_revision':p['revision']}).json()
        self.sid = p['scenes'][0]['id']; self.route = '/paper-theatre/' + self.sid
        self.manifest = {'brief':'Reference', 'style':'Paper', 'mode':'reference-guided',
            'reference_asset_id':self.bg,'reference_approved':True, 'objects':[
                {'id':'cloud','name':'Cloud','group':'sky','description':'Cloud','x':.5,'y':.4,'width':.15,'z':0,'asset_id':self.cloud}]}
        self.post(self.route+'/asset-first/assemble', {'expected_revision':p['revision'],
            'background_id':self.bg,'manifest':{**self.manifest,'mode':'asset-first'}})
        # Separate reference from background to follow reference-guided validation.
        self.app.state.store.mutate(self.pid, self.get()['revision'], lambda p: p.scenes[0].generation['paper_theatre_asset_first'].update(reference_asset_id=self.bg))

    def tearDown(self):
        self.app.state.jobs.close(); self.client.close(); self.temp.cleanup()

    def get(self): return self.client.get(self.base).json()
    def post(self, path, body): return self.client.post(self.base+path,json=body,headers=HEADERS)
    def preview(self):
        result = self.post(self.route+'/review/preview', {'expected_revision':self.get()['revision']})
        self.assertEqual(result.status_code,200,result.text)
        return self.client.get(self.base+self.route+'/review').json()
    def approve(self, state=None):
        state = state or self.preview()
        return self.post(self.route+'/review/decision', {'expected_revision':self.get()['revision'],
            'decision':'approve','signature':state['signature'],'image_sha256':state['preview']['image_sha256'],
            'checks':['proportions','placement','contacts']})
    def timeline(self):
        return self.post('/scenes/'+self.sid+'/to-timeline',{'expected_revision':self.get()['revision']})

    def test_reference_acceptance_is_not_layout_approval_and_draft_cannot_bypass(self):
        self.assertEqual(self.timeline().status_code,422)
        p = self.app.state.store.get(self.pid); scene = p.scenes[0]
        def add(current):
            current.sequence.clips.append(Clip(track_id='v1',scene_id=scene.id,template='paper-theatre',asset_id=scene.asset_id,asset_ids=scene.asset_ids,parameters=scene.parameters,duration=scene.duration))
        self.app.state.store.mutate(self.pid,p.revision,add)
        for quality in ('preview','final'):
            blocked = self.post('/render',{'expected_revision':self.get()['revision'],'quality':quality,'mode':'draft'})
            self.assertEqual(blocked.status_code,422,blocked.text)
            self.assertIn('Scenograf',blocked.text)
        issues = check_project(self.app.state.store,self.app.state.store.get(self.pid))['blocking']
        self.assertTrue(any(i['code'].startswith('paper_review:') for i in issues))

    def test_actual_frame_then_explicit_approval_unlocks_timeline(self):
        state=self.preview()
        self.assertFalse(state['approved'])
        image=self.client.get(state['preview']['url'])
        self.assertEqual(image.status_code,200)
        self.assertEqual(Image.open(io.BytesIO(image.content)).size,(1280,720))
        self.assertEqual(self.approve(state).status_code,200)
        self.assertEqual(self.timeline().status_code,200)
        p=self.app.state.store.get(self.pid)
        review.require_export_approval(self.app.state.store,p)
        # Unrelated text edits do not erase an unchanged visual composition's approval.
        self.app.state.store.mutate(self.pid,p.revision,lambda p:setattr(p,'title','Renamed'))
        self.assertTrue(review.status(self.app.state.store,self.app.state.store.get(self.pid),self.app.state.store.get(self.pid).scenes[0])['approved'])

    def test_pose_reference_and_source_bytes_invalidate_approval(self):
        state=self.preview(); self.assertEqual(self.approve(state).status_code,200)
        p=self.app.state.store.get(self.pid)
        self.app.state.store.mutate(self.pid,p.revision,lambda p:p.scenes[0].parameters['layer_cues'][0].update(layout_width=.2))
        self.assertFalse(self.client.get(self.base+self.route+'/review').json()['approved'])
        self.assertEqual(self.approve(state).status_code,409)
        p=self.app.state.store.get(self.pid)
        path=self.app.state.store.folder(self.pid)/'media'/next(a.filename for a in p.assets if a.id==self.cloud)
        with Image.open(path) as im:
            im.putpixel((0,0),(255,255,255,255)); im.save(path)
        self.assertNotEqual(state['signature'],review.signature(self.app.state.store,p,p.scenes[0]))

    def test_approval_requires_seen_current_image_and_checks(self):
        state=self.preview()
        for extra in ({'checks':[]},{'image_sha256':'fake'},{'checks':[{}]}):
            body={'expected_revision':self.get()['revision'],'decision':'approve','signature':state['signature'],
                'image_sha256':state['preview']['image_sha256'],'checks':['proportions','placement','contacts'],**extra}
            response=self.post(self.route+'/review/decision',body)
            self.assertIn(response.status_code,(409,422),response.text)

    def test_changed_manifest_requires_reassembly(self):
        p=self.get(); data=p['scenes'][0]['generation']['paper_theatre_asset_first'];data['objects'][0]['x']=.7
        self.post(self.route+'/asset-first/save',{'expected_revision':p['revision'],'manifest':data})
        result=self.post(self.route+'/review/preview',{'expected_revision':self.get()['revision']})
        self.assertEqual(result.status_code,422,result.text)

    def test_vision_receives_two_actual_images_and_cannot_approve(self):
        self.preview()
        answer='{"summary":"Waga za duża","verdict":"revise","issues":[{"severity":"critical","object_ids":["cloud"],"problem":"Skala odbiega","correction":"Zmniejsz"}]}'
        with patch('studio_core.assistant.complete_vision',return_value=answer) as model:
            result=self.post(self.route+'/review/vision',{'expected_revision':self.get()['revision']})
        self.assertEqual(result.status_code,200,result.text)
        self.assertEqual(len(model.call_args.args[2]),2)
        self.assertTrue(all(Image.open(io.BytesIO(b)).format=='JPEG' for b in model.call_args.args[2]))
        state=self.client.get(self.base+self.route+'/review').json()
        self.assertFalse(state['approved'])
        self.assertEqual(state['assessment']['issues'][0]['severity'],'critical')
        self.assertEqual(self.approve(state).status_code,422) # critical issues need an author's explanation

    def test_rejection_revokes_current_approval(self):
        self.approve()
        self.post(self.route+'/review/decision',{'expected_revision':self.get()['revision'],'decision':'revise','notes':'Popraw blat'})
        self.assertEqual(self.timeline().status_code,422)
