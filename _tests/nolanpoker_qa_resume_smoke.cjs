'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const source=fs.readFileSync(process.argv[2]||path.resolve(__dirname,'../downloads/nolanpoker-local-video-qa.html'),'utf8');
const start=source.indexOf('  const EXPECTED_SCENES = Object.freeze([');
const end=source.indexOf('  const fmt =',start);
assert.ok(start>0&&end>start,'v3 validator available');
const validate=new Function(source.slice(start,end)+'\nreturn validateSavedReview;')();
const sha='a'.repeat(64),size=12345,duration=575.033;
function example(){return {
 schema:'nolanpoker-local-current-cut-qa-v3',public_video_url:'https://www.youtube.com/watch?v=qABaiIcvvpU',
 public_transcript_audit:'https://nolankido.com/downloads/portland-meadows-public-transcript-audit-2026-11-20.json',
 file:{size_bytes:size,sha256_local:sha,duration_seconds:duration},
 current_video_independently_verified_by_tool:false,no_automatic_audio_visual_assessment:true,
 scenes:[['hand_64o','04:20',260],['hand_77_context','06:27',387],['hand_77_result','07:12',432],['payout_first','08:08',488],['payout_repeat','08:52',532]].map(([id,time,seconds])=>({id,transcript_timecode:time,transcript_seconds:seconds,notes:'Earlier review notes only',listened_to_audio:true,inspected_frames:true,reviewer_decision:'pass',observed_local_time_seconds:260.25})),
 file_equivalence_method:'Reviewed file match',reviewer:'Demo reviewer',global_notes:'Review remains incomplete',review_date:'2026-11-20'
};}
for(const v of ['nolanpoker-local-current-cut-qa-v2','nolanpoker-local-current-cut-qa-v3']) {
 const r=example();r.schema=v;
 assert.equal(validate(r,size,sha,duration).scenes.length,5);
}
function rejects(edit,re){const r=example();edit(r);assert.throws(()=>validate(r,size,sha,duration),re);}
rejects(r=>r.schema='unrecognized',/Unsupported report version/);
rejects(r=>r.public_video_url='https://example.invalid',/different video/);
rejects(r=>r.public_transcript_audit='https://example.invalid',/different video/);
rejects(r=>r.file.sha256_local='0'.repeat(64),/checksum/);
rejects(r=>r.file.size_bytes++,/checksum/);
rejects(r=>r.file.duration_seconds++,/checksum/);
rejects(r=>r.scenes.reverse(),/Invalid or mismatched scene/);
rejects(r=>r.scenes.pop(),/five review checkpoints/);
rejects(r=>r.scenes[0].notes='x'.repeat(1501),/Invalid or mismatched scene/);
rejects(r=>r.scenes[0].observed_local_time_seconds=9999,/Invalid local timestamp/);
rejects(r=>r.scenes[0].listened_to_audio='yes',/Invalid or mismatched scene/);
rejects(r=>r.scenes[0].reviewer_decision='certified',/Invalid or mismatched scene/);
rejects(r=>r.global_notes='x'.repeat(2501),/global_notes/);
rejects(r=>r.reviewer='x'.repeat(101),/reviewer/);
rejects(r=>r.review_date='unknown',/review date/);
rejects(r=>r.current_video_independently_verified_by_tool=true,/compatible unverified/);
assert.ok(source.includes("connect-src 'none'"));
assert.ok(source.includes("c.querySelector('.decision').value='unreviewed'"));
assert.ok(!/(fetch\(|XMLHttpRequest|sendBeacon|localStorage|sessionStorage)/.test(source));
console.log('PASS: resume input validation, v2/v3 compatibility, missing approvals and offline-only boundaries');
