'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib'),{webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'../..'),plain=x=>JSON.parse(JSON.stringify(x)),date='2026-10-29T12:00:00.000Z',roles=['camara-comunicacao-divulgacao','abdi-comunicacao-marketing','cgu-auditoria'];
function setup(){const s={window:{},URL,TextEncoder,crypto:webcrypto};vm.createContext(s);for(const f of ['assets/js/study.js','data/catalog.js'])vm.runInContext(fs.readFileSync(path.join(root,'docs',f),'utf8'),s);s.c=s.window.CONCURSOS_CATALOG;s.old=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-bank-sweep-catalog.json.gz'))));s.old.revision='b'.repeat(64);return s;}
test('sweep preserves original key but excludes one historical MC from every new study and review mode',()=>{
 const s=setup(),p=s.Study.empty(),retired='cgu-2022-correicao-tarde-tipo1-q045';
 assert.deepEqual(roles.map(r=>s.Study.pool(s.c,r,p).length),[408,250,298]);
 const ids=new Set(roles.flatMap(r=>s.Study.pool(s.c,r,p).map(q=>q.id)));assert.equal(ids.size,685);assert.equal(s.c.questions.length,686);assert.equal(ids.has(retired),false);
 const old=s.Study.create(s.old,roles[2],p,'all',{paperId:'source-cgu-2022-correicao-tarde-tipo1',now:date});assert.ok(old.items.some(i=>i.question.id===retired));old.answers=old.items.map(i=>({questionId:i.question.id,value:i.question.id===retired?'b':i.key.value}));
 const progress=s.Study.finish({...p,active:old},'2026-10-29T12:10:00.000Z');assert.equal(s.Study.pool(s.c,roles[2],progress,'errors').some(q=>q.id===retired),false);
 assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(progress),s.c)),plain(progress));assert.equal(old.items.find(i=>i.question.id===retired).key.value,'a');
});
test('all changed snapshots retain the old question/comment/mapping versions, while new snapshots use revised content',()=>{
 const s=setup(),p=s.Study.empty(),manifest=JSON.parse(fs.readFileSync(path.join(root,'data/reviews/bank-sweep-2026-10-29.json'))),changed=manifest.changes.filter(r=>r.section==='questions').map(r=>r.id);
 for(const role of roles){
  const session=s.Study.create(s.old,role,p,'all',{now:date});const saved={...p,active:session};assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(saved),s.c)),plain(saved));assert.equal(s.Study.matches(s.c,session),false);
  const current=s.Study.create(s.c,role,p,'all',{now:date});for(const item of current.items.filter(i=>changed.includes(i.question.id)))assert.equal(item.question.revision,s.old.questions.find(q=>q.id===item.question.id).revision+1);
 }
 const current=s.Study.create(s.c,roles[0],p,'all',{paperId:'source-fiocruz-2024-te15',now:date});assert.match(current.items[0].question.stem,/As afirmativas I, II e III/);const bad=plain({...p,active:current});bad.active.items[0].question.stem=bad.active.items[0].question.stem.replace('As afirmativas','As afirma vas');assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(bad),s.c));
 for(const id of ['mpo-2024-cg1-01-q056','fiocruz-2024-te58-q025'])assert.equal(s.c.questions.find(q=>q.id===id).review.temporalScope,'historical_question');
});
test('post-sweep native exams retain exact distinct quotas and legacy exam scores remain immutable',()=>{
 const s=setup(),p=s.Study.empty();
 for(const [i,count] of [180,60,170].entries()){
  const role=roles[i],session=s.Study.create(s.c,role,p,'exam',{now:date,random:()=>.4});assert.equal(session.items.length,count);assert.equal(new Set(session.items.map(i=>i.question.id)).size,count);assert.equal(session.scoringProfile.rule.version,1);
  const previous=s.Study.create(s.old,role,p,'exam',{now:date,random:()=>.4});previous.answers=previous.items.map(i=>({questionId:i.question.id,value:i.key.value}));const saved=s.Study.finish({...p,active:previous},'2026-10-29T12:30:00.000Z'),restored=s.Study.importBackup(s.Study.exportBackup(saved),s.c);assert.deepEqual(plain(restored),plain(saved));assert.deepEqual(plain(s.Study.score(restored.history[0])),plain(s.Study.score(saved.history[0])));
 }
 assert.deepEqual(plain(s.Study.examAvailability(s.c,roles[2]).blocks.map(b=>b.questions.length)),[71,90,161]);
});
