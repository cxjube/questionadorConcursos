'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const {webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'../..'),role='abdi-comunicacao-marketing',camara='camara-comunicacao-divulgacao';
const plain=x=>JSON.parse(JSON.stringify(x)),start='2026-10-27T10:00:00.000Z',end='2026-10-27T11:00:00.000Z';
function setup(){const s={window:{},crypto:webcrypto,URL,TextEncoder};vm.createContext(s);for(const f of ['assets/js/study.js','assets/js/catalog.js','data/catalog.js'])vm.runInContext(fs.readFileSync(path.join(root,'docs',f),'utf8'),s);return {...s,data:s.window.CONCURSOS_CATALOG};}

test('ABDI shares canonical items while keeping role pools, original formats and institutional topics distinct',()=>{
 const s=setup(),p=s.Study.empty();
 assert.equal(s.Catalog.rolesFor(s.data,'abdi-2026')[0].id,role);
 assert.equal(s.Catalog.syllabusFor(s.data,role).length,97);
 const all=s.Study.pool(s.data,role,p);assert.equal(all.length,261);assert.equal(new Set(all.map(q=>q.id)).size,261);
 assert.equal(s.Study.pool(s.data,role,p,'all',{type:'multiple_choice'}).length,101);
 assert.equal(s.Study.pool(s.data,role,p,'all',{type:'true_false'}).length,160);
 assert.equal(s.Study.pool(s.data,role,p,'all',{block:'basic'}).length,113);
 assert.equal(s.Study.pool(s.data,role,p,'all',{block:'institutional'}).length,26);
 assert.equal(s.Study.pool(s.data,role,p,'all',{block:'specific'}).length,140);
 assert.equal(s.Study.pool(s.data,camara,p).length,421);
 assert.throws(()=>s.Study.pool(s.data,role,p,'all',{topicId:'processo-legislativo-regimento-6-1'}));
 assert.throws(()=>s.Study.pool(s.data,role,p,'all',{block:'unconfirmed-block'}));
});

test('new FGV criteria remain independent of the CE exam and custom practice',()=>{
 const s=setup(),rule=s.Catalog.rulesFor(s.data,role)[0];
 assert.equal(rule.durationMinutes,210);assert.equal(rule.minimumCorrectCount,30);assert.equal(rule.minimumTotalScore,null);
 assert.deepEqual(plain(rule.blocks.map(b=>[b.questionCount,b.correct,b.minimumScoreExclusive])),[[20,.3,true],[20,.3,true],[20,.65,true]]);
 const availability=s.Study.examAvailability(s.data,role);assert.equal(availability.ready,true);
 assert.equal(s.Study.create(s.data,role,s.Study.empty(),'exam',{now:start}).items.length,60);
 const practice=s.Study.create(s.data,role,s.Study.empty(),'all',{limit:2,now:start});assert.equal(practice.scoringProfile,null);
 assert.equal(s.Study.examAvailability(s.data,camara).ready,true);
});

test('every previous Camara study snapshot and the old 180-question exam survive ABDI registration unchanged',()=>{
 const s=setup(),old=JSON.parse(require('node:zlib').gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-abdi-catalog.json.gz'))).toString());old.revision='f'.repeat(64);
 for(const mode of ['all','exam']){
  let p={...s.Study.empty(),active:s.Study.create(old,camara,s.Study.empty(),mode,{now:start,random:()=>.4})};
  assert.equal(p.active.items.length,mode==='all'?395:180);
  assert.equal(s.Study.matches(s.data,p.active),!p.active.items.some(i=>i.question.id==='camara-2014-cb2-03-q084'));
  assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));
  if(mode==='all'){
   const current=s.Study.create(s.data,camara,s.Study.empty(),'all',{now:start});
   const priorIds=new Set(p.active.items.map(i=>i.question.id));assert.deepEqual(plain(current.items.slice(0,p.active.items.length).filter(i=>i.question.id!=='camara-2014-cb2-03-q084')),plain(p.active.items.filter(i=>i.question.id!=='camara-2014-cb2-03-q084')));const revised=current.items.find(i=>i.question.id==='camara-2014-cb2-03-q084');assert.equal(revised.question.revision,2);assert.equal(revised.key.value,p.active.items.find(i=>i.question.id===revised.question.id).key.value);assert.equal(priorIds.size,p.active.items.length);assert.deepEqual(plain(current.items.slice(p.active.items.length).map(i=>i.question.id)),['128-tcemg-008-01-q044','fiocruz-2024-te15-q002','539-alce-016-01-q050','senado-2022-processo-tipo1-q054',...JSON.parse(fs.readFileSync(path.join(root,'data/reviews/gaps-fourth-batch.json'))).items.filter(r=>r.syllabusItemIds.some(id=>id.startsWith('camara-2026-'))).map(r=>r.questionId),...JSON.parse(fs.readFileSync(path.join(root,'data/reviews/norms-gap-fifth.json'))).items.filter(r=>r.syllabusItemIds.some(id=>id.startsWith('camara-2026-'))).map(r=>r.questionId),...JSON.parse(fs.readFileSync(path.join(root,'data/reviews/continuation-seventh.json'))).items.filter(r=>r.syllabusItemIds.some(id=>id.startsWith('camara-2026-'))).map(r=>r.questionId),...JSON.parse(fs.readFileSync(path.join(root,'data/reviews/expansion-eighth.json'))).items.filter(r=>r.syllabusItemIds.some(id=>id.startsWith('camara-2026-'))).map(r=>r.questionId)]);
  }
  p=s.Study.finish(p,end);assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));
 }
});

test('answering a shared question for Camara does not create an ABDI attempt or reclassify old performance',()=>{
 const s=setup(),filters={disciplineId:'lingua-portuguesa',limit:1,now:start};
 const a=s.Study.create(s.data,camara,s.Study.empty(),'all',filters);a.answers.push({questionId:a.items[0].question.id,value:a.items[0].key.value});
 const p=s.Study.finish({...s.Study.empty(),active:a},end);
 assert.equal(s.Study.performance(p.history,role).attempts,0);
 assert.equal(s.Study.pool(s.data,role,p,'unanswered').length,261);
 const b=s.Study.create(s.data,role,p,'all',filters);assert.equal(b.items[0].question.id,a.items[0].question.id);
 assert.ok(b.items[0].mappings.every(m=>m.roleId===role));assert.ok(a.items[0].mappings.every(m=>m.roleId===camara));
 assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup({...p,active:b}),s.data)),plain({...p,active:b}));
});

test('institutional block metadata round-trips in a clearly isolated copied-catalog fixture',()=>{
 const s=setup(),data=plain(s.data),item=data.syllabusItems.find(i=>i.roleId===role && i.block==='institutional');
 data.mappings.push({id:'synthetic-institutional-mapping-test-only',questionId:data.questions[0].id,syllabusItemId:item.id,justification:'SYNTHETIC VALIDATION FIXTURE ONLY',status:'confirmed'});
 const session=s.Study.create(data,role,s.Study.empty(),'all',{block:'institutional',limit:1,now:start});
 assert.equal(session.items.length,1);assert.equal(session.selection.block,'institutional');
 assert.ok(session.items[0].mappings.some(m=>m.block==='institutional'));
 const p={...s.Study.empty(),active:session};assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),data)),plain(p));
});
