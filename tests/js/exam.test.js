'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const {webcrypto} = require('node:crypto');
const root = path.resolve(__dirname,'../..');
const plain = value => JSON.parse(JSON.stringify(value));
const start = '2026-10-23T12:00:00.000Z', end = '2026-10-23T13:00:00.000Z';
function setup() {
  const context = {window:{},crypto:webcrypto,URL,TextEncoder}; vm.createContext(context);
  for (const file of ['assets/js/study.js','data/catalog.js']) vm.runInContext(fs.readFileSync(path.join(root,'docs',file),'utf8'),context);
  return {...context,data:context.window.CONCURSOS_CATALOG,role:context.window.CONCURSOS_CATALOG.roles[0].id};
}
function active(s) {return {...s.Study.empty(),active:s.Study.create(s.data,s.role,s.Study.empty(),'exam',{now:start,id:'exam-test',random:()=>0.4})};}
// Isolated copied-catalog boundary fixture, independent of future bank growth.
function minimumBank(s) {
  const ids=new Set(['basic','specific'].flatMap(block=>s.Study.pool(s.data,s.role,s.Study.empty(),'all',{block,type:'true_false'}).slice(0,90).map(q=>q.id)));
  s.data.questions=s.data.questions.filter(q=>q.type!=='true_false' || ids.has(q.id));
}
function withPoints(s,p1,p2) {
  const progress = active(s);
  for (const [index,points] of [p1,p2].entries()) for (const item of progress.active.items.filter(i=>i.examBlockId===['p1','p2'][index]).slice(0,Math.abs(points)))
    progress.active.answers.push({questionId:item.question.id,value:points<0 ? !item.key.value : item.key.value});
  return s.Study.finish(progress,end);
}
test('exam fixes 90+90 distinct CE, source rules v1, 5h deadline and independent snapshots',()=>{
  const s=setup(), original=JSON.stringify(s.data), p=active(s), session=p.active;
  assert.equal(JSON.stringify(s.data),original);assert.equal(session.mode,'exam');
  assert.equal(session.items.length,180);assert.equal(new Set(session.items.map(i=>i.question.id)).size,180);
  assert.equal(session.timer.durationSeconds,18000);assert.equal(session.timer.deadlineAt,'2026-10-23T17:00:00.000Z');
  assert.equal(session.scoringProfile.kind,'official_rules');assert.equal(session.scoringProfile.rule.version,1);
  assert.deepEqual(plain(session.scoringProfile.rule),plain(s.data.scoringRules[0]));
  for (const [block,offset] of [['p1',0],['p2',90]]) {
    assert.ok(session.items.slice(offset,offset+90).every(i=>i.examBlockId===block && i.question.type==='true_false' && i.key.result==='valid' && i.mappings.some(m=>m.block===(block==='p1'?'basic':'specific'))));
  }
  s.data.scoringRules[0].minimumTotalScore=999;assert.equal(session.scoringProfile.rule.minimumTotalScore,54);
});
test('exam allocation handles overlapping thematic eligibility without starving a block',()=>{
  const s=setup();minimumBank(s); const target=s.data.syllabusItems.find(i=>i.block==='basic' && i.status==='confirmed');
  const specific=s.Study.pool(s.data,s.role,s.Study.empty(),'all',{block:'specific',type:'true_false'});
  for(const [index,q] of specific.slice(0,6).entries()) s.data.mappings.push({id:'synthetic-overlap-'+index,questionId:q.id,syllabusItemId:target.id,status:'confirmed'});
  const availability=s.Study.examAvailability(s.data,s.role);
  assert.equal(availability.ready,true);assert.equal(availability.blocks[0].questions.length,96);
  const session=active(s).active;assert.equal(new Set(session.items.map(i=>i.question.id)).size,180);
  assert.deepEqual(new Set(session.items.filter(i=>i.examBlockId==='p2').map(i=>i.question.id)),new Set(specific.map(q=>q.id)));
  const basicId=session.items.find(i=>i.examBlockId==='p1').question.id;
  s.data.questions=s.data.questions.filter(q=>q.id!==basicId);
  const shortage=s.Study.examAvailability(s.data,s.role);
  assert.ok(shortage.blocks.every(b=>b.questions.length>=90));assert.equal(shortage.distinct,179);assert.equal(shortage.ready,false);
  assert.throws(()=>active(s),/insuficiente/);
});
test('exam blocks unconfirmed rules, missing eligible CE and custom settings without changing practice',()=>{
  const s=setup();minimumBank(s);assert.equal(s.Study.examAvailability(s.data,'abdi-futuro').ready,false);
  for(const settings of [{limit:20},{durationMinutes:5},{scoringMode:'none'},{block:'basic'},{type:'multiple_choice'},{shuffle:false}])
    assert.throws(()=>s.Study.create(s.data,s.role,s.Study.empty(),'exam',settings),/fixados/);
  const rule=s.data.scoringRules[0];rule.status='documented';assert.throws(()=>active(s),/confirmado/);rule.status='confirmed';
  const eligible=s.Study.examAvailability(s.data,s.role).blocks[0].questions[0];
  s.data.answerKeys.find(k=>k.id===eligible.answerKeyId).result='annulled';
  assert.equal(s.Study.examAvailability(s.data,s.role).ready,false);assert.throws(()=>active(s),/insuficiente/);
  const practice=s.Study.create(s.data,s.role,s.Study.empty(),'all',{limit:5,durationMinutes:3,scoringMode:'net'});
  assert.equal(practice.items.length,5);assert.equal(practice.scoringProfile.kind,'custom');assert.equal(practice.timer.durationSeconds,180);
});
test('exam calculates negative scores, false answers, blanks, maximum and no artificial accuracy',()=>{
  const s=setup();let p=withPoints(s,-90,-90),score=s.Study.score(p.history[0]);
  assert.equal(score.points,-180);assert.equal(score.maximum,180);assert.equal(score.meetsMinimums,false);
  assert.equal(s.Study.totals(p.history[0]).incorrect,180);
  p=withPoints(s,90,90);score=s.Study.score(p.history[0]);assert.equal(score.points,180);assert.equal(score.meetsMinimums,true);
  assert.ok(p.history[0].answers.some(a=>a.value===false));assert.equal(s.Study.totals(p.history[0]).correct,180);
  p=withPoints(s,0,0);score=s.Study.score(p.history[0]);assert.equal(score.points,0);assert.equal(s.Study.totals(p.history[0]).blank,180);assert.equal(s.Study.totals(p.history[0]).rate,null);
});
test('the two block minima and total minimum are independent with inclusive boundaries',()=>{
  const s=setup();
  for(const [p1,p2,first,second,total,all] of [[18,36,true,true,true,true],[17,90,false,true,true,false],[90,26,true,false,true,false],[18,27,true,true,false,false],[18,35,true,true,false,false],[18,0,true,false,false,false]]) {
    const score=s.Study.score(withPoints(s,p1,p2).history[0]);
    assert.equal(score.blocks[0].met,first);assert.equal(score.blocks[1].met,second);assert.equal(score.totalMet,total);assert.equal(score.meetsMinimums,all);assert.equal(score.points,p1+p2);
  }
});
test('exam deadline survives backup and a closed page, rejects late choices and finishes once',()=>{
  const s=setup();let p=active(s);
  p.active=s.Study.choose(p.active,false,'2026-10-23T12:01:00.000Z');p.active=s.Study.move(p.active,90);
  p=s.Study.importBackup(s.Study.exportBackup(p),s.data);assert.equal(p.active.position,90);
  assert.equal(p.active.answers[0].value,false);assert.equal(s.Study.remaining(p.active,'2026-10-23T16:59:59.000Z'),1);
  assert.throws(()=>s.Study.choose(p.active,true,'2026-10-23T17:00:00.000Z'),/terminou/);
  p=s.Study.finish(p,'2026-10-23T18:00:00.000Z');assert.equal(p.history[0].finishedAt,'2026-10-23T17:00:00.000Z');assert.equal(p.history[0].finishReason,'time_limit');
  assert.deepEqual(plain(s.Study.finish(p)),plain(p));assert.ok(s.Study.validate(p,s.data));
});
test('backup rejects altered current rules, assignments, timers, duplicates and exam disguise',()=>{
  const s=setup(), original=active(s), before=JSON.stringify(original);
  for(const mutate of [
    p=>p.active.scoringProfile.rule.minimumTotalScore=0,
    p=>p.active.scoringProfile.rule.version=2,
    p=>p.active.scoringProfile.version=2,
    p=>p.active.scoringProfile.rule.blocks[0].minimumScore=0,
    p=>p.active.scoringProfile.officialUrl='https://www.cebraspe.org.br/incorrect-reference',
    p=>p.active.items[0].examBlockId='p2',
    p=>p.active.items[0].mappings[0].block='specific',
    p=>p.active.items[90]=p.active.items[0],
    p=>p.active.items.pop(),
    p=>p.active.timer=null,
    p=>p.active.scoringProfile=null,
    p=>p.active.mode='all',
    p=>p.active.contestId='abdi-futuro',
    p=>p.active.selection.block='basic',
    p=>p.active.selection.shuffle=false,
    p=>p.active.items[0].key.result='annulled',
  ]) {const broken=plain(original);mutate(broken);assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(broken),s.data));}
  assert.equal(JSON.stringify(original),before);
  const roundtrip=s.Study.importBackup(s.Study.exportBackup(original),s.data);assert.deepEqual(plain(roundtrip),plain(original));
});
test('later catalog rule versions preserve the original exam score and source snapshot',()=>{
  const s=setup(), original=withPoints(s,18,36), before=JSON.stringify(original);
  s.data.scoringRules[0].version=2;s.data.scoringRules[0].minimumTotalScore=100;
  const restored=s.Study.importBackup(s.Study.exportBackup(original),s.data);
  assert.equal(JSON.stringify(restored),before);assert.equal(s.Study.score(restored.history[0]).meetsMinimums,true);
  const fresh=active(s);assert.equal(fresh.active.scoringProfile.rule.version,2);assert.equal(fresh.active.scoringProfile.rule.minimumTotalScore,100);
});
test('the larger reserve varies sampled questions while keeping 90+90 and older exams intact',()=>{
  const s=setup(),available=s.Study.examAvailability(s.data,s.role);
  assert.deepEqual(plain(available.blocks.map(b=>b.questions.length)),[140,147]);assert.equal(available.distinct,287);
  const draw=random=>s.Study.create(s.data,s.role,s.Study.empty(),'exam',{now:start,random});
  const first=draw(()=>0.01),second=draw(()=>0.99);
  const ids=session=>new Set(session.items.map(i=>i.question.id));
  assert.notDeepEqual(ids(first),ids(second));assert.equal(ids(first).size,180);assert.equal(ids(second).size,180);
  const old=plain(s.data);
  const audit=JSON.parse(fs.readFileSync(path.join(root,'data/reviews/content-audit-2026-10-26.json'),'utf8'));
  for(const change of audit.mappingCorrections) old.mappings[old.mappings.findIndex(m=>m.id===change.after.id)]=change.before;
  old.revision='0'.repeat(64); // Synthetic revision only inside this test.
  const added=new Set(old.questions.filter(q=>q.review.decisionReference==='documentation/eleventh-batch-release.md').map(q=>q.id));
  old.questions=old.questions.filter(q=>!added.has(q.id));old.mappings=old.mappings.filter(m=>!added.has(m.questionId));
  let p={...s.Study.empty(),active:s.Study.create(old,s.role,s.Study.empty(),'exam',{now:start,id:'older-exam'})};
  p.active=s.Study.choose(p.active,false,'2026-10-23T12:01:00.000Z');p=s.Study.finish(p,end);
  const restored=s.Study.importBackup(s.Study.exportBackup(p),s.data);
  assert.deepEqual(plain(restored),plain(p));assert.deepEqual(plain(s.Study.score(restored.history[0])),plain(s.Study.score(p.history[0])));
});

test('pre-audit 180-item exams retain their allocation, context versions and scores',()=>{
  const s=setup(),old=plain(s.data);
  const audit=JSON.parse(fs.readFileSync(path.join(root,'data/reviews/content-audit-2026-10-26.json'),'utf8'));
  for(const [section,changes] of [['mappings',audit.mappingCorrections],['contexts',audit.contextCorrections],['questions',audit.questionRevisions]])
    for(const change of changes) old[section][old[section].findIndex(row=>row.id===change.after.id)]=change.before;
  old.revision='e'.repeat(64);
  let progress={...s.Study.empty(),active:s.Study.create(old,s.role,s.Study.empty(),'exam',{now:start,random:()=>0.4})};
  const draft=plain(progress);
  assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(progress),s.data)),draft);
  progress=s.Study.finish(progress,end);
  const restored=s.Study.importBackup(s.Study.exportBackup(progress),s.data);
  assert.deepEqual(plain(restored),plain(progress));
  assert.deepEqual(plain(s.Study.score(restored.history[0])),plain(s.Study.score(progress.history[0])));
});

test('later batches preserve real previous-catalog sessions while adding new distinct choices',()=>{
  const s=setup();
  for(const [snapshot,count,added] of [['content-audit-catalog-2026-10-26.json.gz',224,75],['pre-thirteenth-catalog.json.gz',254,45],['pre-fourteenth-catalog.json.gz',266,33]]) {
  const old=JSON.parse(require('node:zlib').gunzipSync(fs.readFileSync(path.join(root,'data/reviews',snapshot))).toString());
  old.revision='d'.repeat(64); // Synthetic revision; all question/key/rule rows are the frozen real catalog.
  assert.equal(old.questions.length,count);
  const before=s.Study.create(old,s.role,s.Study.empty(),'exam',{now:start,random:()=>0.4});
  let progress={...s.Study.empty(),active:before};
  const restored=s.Study.importBackup(s.Study.exportBackup(progress),s.data);
  assert.deepEqual(plain(restored),plain(progress));
  assert.equal(restored.active.items.length,180);
  const oldIds=new Set(old.questions.map(q=>q.id));
  assert.ok(restored.active.items.every(i=>oldIds.has(i.question.id)));
  progress=s.Study.finish(restored,end);
  assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(progress),s.data)),plain(progress));
  const current=s.Study.examAvailability(s.data,s.role);
  assert.deepEqual(plain(current.blocks.map(b=>b.questions.length)),[140,147]);
  const all=s.Study.pool(s.data,s.role,s.Study.empty(),'all',{type:'true_false'});
  assert.equal(all.filter(q=>!oldIds.has(q.id)).length,added);
  }
});
