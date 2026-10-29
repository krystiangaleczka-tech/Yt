import test from 'node:test';
import assert from 'node:assert/strict';
import {syncMedia,pauseMedia,audioFrame,primaryAudioClip} from '../src/playback.ts';

class Media {
  position=0; rate=1; paused=true; ended=false; seeking=false; readyState=4;
  seeks=[]; rateChanges=[]; plays=0; pauses=0;
  get currentTime(){return this.position}
  set currentTime(value){this.seeks.push(value);this.position=value;this.ended=false}
  get playbackRate(){return this.rate}
  set playbackRate(value){this.rateChanges.push(value);this.rate=value}
  play(){this.plays++;this.paused=false;return Promise.resolve()}
  pause(){this.pauses++;this.paused=true}
}
const noError=error=>assert.fail(String(error));

test('continuous playback never seeks to chase a delayed browser audio clock',async()=>{
 const media=new Media();
 syncMedia(media,2,true,1,'clip',noError);await Promise.resolve();
 for(let frame=1;frame<=600;frame++){
  // Simulate delayed media.currentTime reports and duplicate canvas redraws.
  media.position=2+frame/60-.25;
  syncMedia(media,2+frame/60,true,1,'clip',noError);
  syncMedia(media,2+frame/60,true,1,'clip',noError);
 }
 assert.deepEqual(media.seeks,[2]);assert.equal(media.plays,1);assert.deepEqual(media.rateChanges,[]);
});

test('pause, scrub, resume and a changed source offset seek only at those boundaries',async()=>{
 const media=new Media();syncMedia(media,0,true,1,'source-a',noError);await Promise.resolve();
 media.position=3;pauseMedia(media);
 syncMedia(media,5,false,1,'source-a',noError);syncMedia(media,5,false,1,'source-a',noError);
 syncMedia(media,5,true,1,'source-a',noError);await Promise.resolve();
 syncMedia(media,7,true,1.5,'source-b',noError);
 assert.deepEqual(media.seeks,[5,7]);assert.deepEqual(media.rateChanges,[1.5]);assert.equal(media.plays,2);
});

test('one pending play request is reused and a late resolution cannot undo Pause',async()=>{
 const media=new Media();let finish;
 media.play=()=>{media.plays++;return new Promise(resolve=>{finish=()=>{media.paused=false;resolve()}})};
 for(let frame=0;frame<60;frame++)syncMedia(media,frame/30,true,1,'voice',noError);
 assert.equal(media.plays,1);assert.equal(media.seeks.length,0);
 pauseMedia(media);finish();await Promise.resolve();assert.equal(media.paused,true);
});

test('rejected playback is reported once until the user stops and retries',async()=>{
 const media=new Media();let errors=0;
 media.play=()=>{media.plays++;return Promise.reject(new Error('blocked'))};
 syncMedia(media,0,true,1,'voice',()=>errors++);await Promise.resolve();
 for(let frame=0;frame<30;frame++)syncMedia(media,frame/30,true,1,'voice',()=>errors++);
 assert.equal(media.plays,1);assert.equal(errors,1);
 pauseMedia(media);syncMedia(media,0,true,1,'voice',()=>errors++);await Promise.resolve();assert.equal(errors,2);
});

test('rapid Pause and Play ignore the aborted earlier request',async()=>{
 const media=new Media();const requests=[];let errors=0;
 media.play=()=>{media.plays++;return new Promise((resolve,reject)=>requests.push({resolve,reject}))};
 syncMedia(media,0,true,1,'voice',()=>errors++);pauseMedia(media);
 syncMedia(media,0,true,1,'voice',()=>errors++);
 requests[0].reject(new Error('AbortError'));await Promise.resolve();
 assert.equal(errors,0);assert.equal(media.plays,2);
 media.paused=false;requests[1].resolve();await Promise.resolve();
 syncMedia(media,.1,true,1,'voice',()=>errors++);assert.equal(media.plays,2);
});

test('picture follows measured audio time, holds on buffering and advances at the clip end',()=>{
 const clip={start:30,duration:300,source_in:60,speed:2};const media=new Media();
 media.paused=false;media.position=4;
 assert.equal(audioFrame(clip,media,30,30),60);
 media.readyState=1;media.position=5;assert.equal(audioFrame(clip,media,30,60),60);
 media.readyState=4;media.seeking=true;assert.equal(audioFrame(clip,media,30,60),60);
 media.seeking=false;assert.equal(audioFrame(clip,media,30,60),75);
 media.position=4.9;assert.equal(audioFrame(clip,media,30,75),75);
 media.ended=true;assert.equal(audioFrame(clip,media,30,75),330);
});

test('narration is the primary clock and mute/solo decide which audio is active',()=>{
 const project={sequence:{tracks:[{id:'music',kind:'audio',role:'music'},{id:'voice',kind:'audio',role:'narration'},{id:'picture',kind:'video',role:'picture'}],clips:[{id:'music',track_id:'music',asset_id:'a',start:0,duration:300},{id:'voice',track_id:'voice',asset_id:'b',start:30,duration:60}]}};
 assert.equal(primaryAudioClip(project,0).id,'music');assert.equal(primaryAudioClip(project,45).id,'voice');
 project.sequence.tracks[1].muted=true;assert.equal(primaryAudioClip(project,45).id,'music');
 project.sequence.tracks[2].solo=true;assert.equal(primaryAudioClip(project,45),undefined);
});
