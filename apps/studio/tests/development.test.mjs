import test from 'node:test';
import assert from 'node:assert/strict';
import {blankIdea,blankStory,blankChapter,copyStory} from '../src/developmentTypes.ts';

test('copying a story creates a separate editable tree with preserved evidence and no applied marker',()=>{
 const story=blankStory();story.chapters=[blankChapter()];story.chapters[0].sections[0].fact_ids=['fact_a'];story.applied_hash='already-applied';
 const copy=copyStory(story);
 assert.notEqual(copy.id,story.id);assert.notEqual(copy.chapters[0].id,story.chapters[0].id);assert.notEqual(copy.chapters[0].sections[0].id,story.chapters[0].sections[0].id);
 assert.equal(copy.applied_hash,'');assert.deepEqual(copy.chapters[0].sections[0].fact_ids,['fact_a']);
 copy.chapters[0].sections[0].fact_ids.push('fact_b');copy.scores.hook=90;
 assert.deepEqual(story.chapters[0].sections[0].fact_ids,['fact_a']);assert.equal(story.scores.hook,50);
});

test('new ideas do not silently include or select a story and copied names stay within schema limits',()=>{
 assert.deepEqual(blankIdea().stories,[]);const story=blankStory();story.title='a'.repeat(200);
 assert.ok(copyStory(story).title.length<=200);
});
