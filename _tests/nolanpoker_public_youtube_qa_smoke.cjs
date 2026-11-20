'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const html=fs.readFileSync(path.resolve(__dirname,'../downloads/nolanpoker-public-youtube-review.html'),'utf8');
const a=html.indexOf("const ID='qABaiIcvvpU'");
const b=html.indexOf("if(typeof module!=='undefined'",a);
assert.ok(a>0&&b>a,'Validator source found');
const pure=html.slice(a,b).replace("const $=id=>document.getElementById(id);\nconst cards=[...document.querySelectorAll('.checkpoint')];\n",'');
const helpers=new Function(pure+'return {validateSaved,parseTime,SPECS,SCHEMA};')();
assert.equal(helpers.SPECS.length,6);
assert.equal(helpers.parseTime('08:52'),532);
assert.equal(helpers.parseTime('garbage'),null);
assert.equal(helpers.parseTime('00:60'),null);
const fixture={schema:helpers.SCHEMA,video_id:'qABaiIcvvpU',
  public_watch_url:'https://www.youtube.com/watch?v=qABaiIcvvpU',
  reviewer:'Reviewer',overall_notes:'No automatic video verification',
  scenes:helpers.SPECS.map(([id,time,seconds])=>({id,reference_timecode:time,
    reference_seconds:seconds,notes:'Source-specific observations',observed_timecode:'04:21',
    reviewer_decision:'pass',heard_audio:true,inspected_video_frames:true}))};
assert.equal(helpers.validateSaved(fixture).length,6);
function bad(fn){const x=JSON.parse(JSON.stringify(fixture));fn(x);assert.throws(()=>helpers.validateSaved(x));}
bad(x=>x.schema='unsupported');
bad(x=>x.video_id='not-this-video');
bad(x=>x.public_watch_url='https://example.invalid');
bad(x=>x.scenes.pop());
bad(x=>x.scenes.reverse());
bad(x=>x.scenes[0].notes='x'.repeat(1501));
bad(x=>x.scenes[0].observed_timecode='0:99');
bad(x=>x.overall_notes='x'.repeat(2501));
assert.ok(html.includes("c.querySelector('.decision').value='unreviewed'"));
assert.ok(html.includes('public_video_frames_independently_verified_by_tool:false'));
assert.ok(!/(fetch\(|localStorage|sessionStorage|sendBeacon|XMLHttpRequest)/.test(html));
console.log('PASS: six public source checkpoints, import validation, no inherited approvals, no automatic verification.');
