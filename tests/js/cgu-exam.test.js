'use strict';
const {test}=require('node:test'), assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),{webcrypto}=require('node:crypto');
const fixture=require('../fixtures/cgu-exam.cjs');
const root=path.resolve(__dirname,'../..'),role='synthetic-cgu-ce',start='2026-10-28T12:00:00.000Z';
const plain=x=>JSON.parse(JSON.stringify(x));
function setup(){const s={window:{},crypto:webcrypto,URL,TextEncoder};vm.createContext(s);for(const f of ['assets/js/study.js','data/catalog.js'])vm.runInContext(fs.readFileSync(path.join(root,'docs',f),'utf8'),s);s.data=fixture(s.window.CONCURSOS_CATALOG);return s;}
function active(s){return {...s.Study.empty(),active:s.Study.create(s.data,role,s.Study.empty(),'exam',{now:start,id:'synthetic-cgu-session',random:()=>.4})};}
function counts(s,values){let p=active(s);for(const [index,count] of values.entries())for(const item of p.active.items.filter(i=>i.examBlockId===['basic','complementary','specific'][index]).slice(0,Math.abs(count)))p.active.answers.push({questionId:item.question.id,value:count<0?!item.key.value:item.key.value});return s.Study.finish(p,'2026-10-28T13:00:00.000Z');}

test('three-block CE fixture allocates 40/40/90 unique items and preserves complementary filters and backups',()=>{
 const s=setup(),before=JSON.stringify(s.data),a=s.Study.examAvailability(s.data,role),p=active(s),session=p.active;
 assert.equal(a.ready,true);assert.equal(a.distinct,170);assert.equal(JSON.stringify(s.data),before);assert.equal(new Set(session.items.map(i=>i.question.id)).size,170);
 assert.deepEqual(plain(session.scoringProfile.rule),plain(s.data.scoringRules.find(r=>r.roleId===role)));assert.equal(session.timer.durationSeconds,18000);assert.equal(session.timer.deadlineAt,'2026-10-28T17:00:00.000Z');
 for(const [i,b] of session.scoringProfile.rule.blocks.entries()){const offset=i===2?80:i*40;assert.ok(session.items.slice(offset,offset+b.questionCount).every(q=>q.examBlockId===b.id && q.mappings.some(m=>m.block===b.id)));}
 assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));
 const practice=s.Study.create(s.data,role,s.Study.empty(),'all',{block:'complementary',now:start});assert.equal(practice.items.length,40);assert.equal(practice.scoringProfile,null);assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup({...s.Study.empty(),active:practice}),s.data).active),plain(practice));
});
test('CGU fixture weights and four independent inclusive minima do not inherit Camara or ABDI scoring',()=>{
 const s=setup();for(const [values,points,met] of [[[40,40,90],260,true],[[-40,-40,-90],-260,false],[[0,0,0],0,false],[[8,12,27],74,false],[[8,12,28],76,false],[[8,12,29],78,true],[[7,40,90],227,false],[[40,11,90],231,false],[[40,40,26],132,false]]){
  const r=s.Study.score(counts(s,values).history[0]);assert.equal(r.points,points);assert.equal(r.maximum,260);assert.equal(r.minimum,78);assert.equal(r.meetsMinimums,met);assert.deepEqual(plain(r.blocks.map(b=>b.points)),[values[0],values[1],values[2]*2]);assert.deepEqual(plain(r.blocks.map(b=>b.minimum)),[8,12,54]);
 }
});
test('three CE blocks detect joint shortages despite sufficient union and sufficient per-block counts',()=>{
 const s=setup(),q=s.data.questions.filter(q=>q.id.startsWith('synthetic-cgu-question-'));
 s.data.mappings=s.data.mappings.filter(m=>!m.id.startsWith('synthetic-cgu-question-'));
 for(const [block,ids] of [['basic',q.slice(0,50)],['complementary',q.slice(0,50)],['specific',q.slice(50)]])for(const item of ids)s.data.mappings.push({id:item.id+'-'+block,questionId:item.id,syllabusItemId:'synthetic-cgu-'+block,status:'confirmed'});
 const a=s.Study.examAvailability(s.data,role);assert.equal(a.distinct,170);assert.ok(a.blocks.every(b=>b.questions.length>=b.questionCount));assert.equal(a.ready,false);assert.equal(a.missing.reduce((n,b)=>n+b.count,0),30);assert.throws(()=>active(s),/insuficiente/);
});
test('three CE matching remaps shared eligibility without duplication or false insufficiency',()=>{
 const s=setup(),rule=s.data.scoringRules.find(r=>r.roleId===role);for(const b of rule.blocks)b.questionCount=1;
 const ids=['synthetic-cgu-question-1','synthetic-cgu-question-2','synthetic-cgu-question-3'];s.data.mappings=s.data.mappings.filter(m=>!m.id.startsWith('synthetic-cgu-question-'));
 for(const [block,eligible] of [['basic',ids.slice(0,2)],['complementary',[ids[0]]],['specific',ids.slice(1)]])for(const id of eligible)s.data.mappings.push({id:id+'-'+block,questionId:id,syllabusItemId:'synthetic-cgu-'+block,status:'confirmed'});
 const p=active(s);assert.deepEqual(plain(p.active.items.map(i=>i.question.id)),[ids[1],ids[0],ids[2]]);assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));
});
test('three CE imports reject weights, block assignments, duplicate IDs, criteria and deadline tampering',()=>{
 const s=setup(),p=active(s);for(const mutate of [p=>p.active.scoringProfile.rule.blocks[2].correct=1,p=>p.active.scoringProfile.rule.blocks[2].incorrect=-1,p=>p.active.scoringProfile.rule.minimumTotalScore=74,p=>p.active.scoringProfile.rule.blocks[1].minimumScore=8,p=>p.active.items[40].examBlockId='specific',p=>p.active.items[40].mappings[0].block='specific',p=>p.active.items[80]=p.active.items[0],p=>p.active.scoringProfile.rule.blocks[1].id='p2',p=>p.active.timer.durationSeconds=12600]){const bad=plain(p);mutate(bad);assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(bad),s.data));}
 const rule=s.data.scoringRules.find(r=>r.roleId===role);for(const change of [b=>b.correct=0,b=>b.incorrect=0,b=>b.correct=Infinity]){const original=rule.blocks[2].correct;change(rule.blocks[2]);assert.equal(s.Study.examAvailability(s.data,role).ready,false);rule.blocks[2].correct=original;rule.blocks[2].incorrect=-original;}
});
test('three CE deadlines, expiry and older rule versions preserve immutable scores',()=>{
 const s=setup();let p=active(s);p.active=s.Study.choose(p.active,false,'2026-10-28T12:01:00.000Z');p.active=s.Study.move(p.active,80);p=s.Study.importBackup(s.Study.exportBackup(p),s.data);assert.equal(p.active.position,80);assert.equal(p.active.answers[0].value,false);assert.equal(s.Study.remaining(p.active,'2026-10-28T16:59:59.000Z'),1);assert.throws(()=>s.Study.choose(p.active,true,'2026-10-28T17:00:00.000Z'),/terminou/);p=s.Study.finish(p,'2026-10-28T18:00:00.000Z');assert.equal(p.history[0].finishedAt,'2026-10-28T17:00:00.000Z');assert.deepEqual(plain(s.Study.finish(p)),plain(p));
 p=counts(s,[8,12,29]);const raw=s.Study.exportBackup(p),rule=s.data.scoringRules.find(r=>r.roleId===role);rule.version++;rule.minimumTotalScore=100;const restored=s.Study.importBackup(raw,s.data);assert.equal(s.Study.score(restored.history[0]).points,78);assert.equal(s.Study.score(restored.history[0]).meetsMinimums,true);
 for(const settings of [{limit:20},{durationMinutes:210},{block:'complementary'},{scoringMode:'net'}])assert.throws(()=>s.Study.create(s.data,role,s.Study.empty(),'exam',settings),/fixados/);
});
test('production CGU profile is enabled by real capacity and contains no synthetic study content',()=>{
 const s=setup(),native=JSON.parse(fs.readFileSync(path.join(root,'data/catalog.json'))),availability=s.Study.examAvailability(native,'cgu-auditoria');assert.equal(availability.ready,true);assert.equal(availability.rule.id,'cgu-2026-auditoria-objetivas');assert.equal(availability.distinct,224);assert.equal(availability.missing.reduce((n,b)=>n+b.count,0),0);assert.equal(native.questions.length,608);assert.equal(native.scoringRules.length,3);assert.equal(native.questions.filter(q=>q.id.startsWith('synthetic')).length,0);assert.equal(native.syllabusItems.some(i=>i.block==='complementary'),true);
});
