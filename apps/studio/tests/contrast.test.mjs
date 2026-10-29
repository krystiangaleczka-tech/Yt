import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const css=readFileSync(new URL('../src/studio.css',import.meta.url),'utf8');
function variables(block){return Object.fromEntries([...block.matchAll(/(--[\w-]+):\s*(#[0-9a-f]{6})/gi)].map(m=>[m[1],m[2]]))}
function luminance(hex){const rgb=hex.slice(1).match(/../g).map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722}
function ratio(a,b){const values=[luminance(a),luminance(b)].sort((a,b)=>b-a);return (values[0]+.05)/(values[1]+.05)}
test('dark and light reading/focus palette meets WCAG contrast thresholds',()=>{
 const dark=variables(css.match(/:root\s*\{([^}]+)\}/)[1]),light={...dark,...variables(css.match(/\[data-theme="light"\]\s*\{([^}]+)\}/)[1])};
 for(const [theme,colors] of [['dark',dark],['light',light]]){
  for(const [fg,bg] of [['--text','--panel'],['--muted','--panel'],['--accent','--accent-soft']])assert.ok(ratio(colors[fg],colors[bg])>=4.5,`${theme} ${fg}/${bg}`);
  assert.ok(ratio(colors['--accent'],colors['--bg'])>=3,`${theme} focus indicator`);
 }
});
