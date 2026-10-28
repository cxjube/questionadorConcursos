'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib'),{webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'../..'),start='2026-10-28T12:00:00.000Z',role='cgu-auditoria',abdi='abdi-comunicacao-marketing';
const plain=x=>JSON.parse(JSON.stringify(x));
function setup(){const s={window:{},URL,TextEncoder,crypto:webcrypto};vm.createContext(s);for(const f of ['assets/js/study.js','data/catalog.js'])vm.runInContext(fs.readFileSync(path.join(root,'docs',f),'utf8'),s);s.data=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-gaps-third-batch-catalog.json.gz'))));s.data.revision='d'.repeat(64);return s;}
test('real expanded roles preserve their independent CE/MC compositions and exact Python capacity audits',()=>{
 const s=setup(),c=s.data,p=s.Study.empty(),ce=s.Study.examAvailability(c,role),mc=s.Study.examAvailability(c,abdi),r=JSON.parse(fs.readFileSync(path.join(root,'data/reviews/abdi-pre-gaps-third-readiness.json')));
 assert.equal(s.Study.pool(c,role,p).length,229);assert.equal(ce.distinct,224);assert.equal(ce.ready,true);assert.deepEqual(plain(ce.blocks.map(b=>b.questions.length)),[62,81,138]);assert.equal(mc.ready,true);assert.equal(mc.missing.length,0);assert.equal(r.quotaCheck.allocatableDistinctMC,60);
 assert.equal(s.Study.pool(c,abdi,p,'all',{block:'institutional',type:'multiple_choice'}).length,21);assert.equal(s.Study.pool(c,abdi,p,'all',{type:'multiple_choice'}).length,r.distinctMC);
 for(const id of [role,abdi,'camara-comunicacao-divulgacao']){const session=s.Study.create(c,id,p,'exam',{now:start,random:()=>.4});assert.equal(new Set(session.items.map(i=>i.question.id)).size,session.items.length);assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup({...p,active:session}),c).active),plain(session));}
});
test('Tesouro source links and annotated-paper metadata survive backup while lookalikes and invalid flags fail',()=>{
 const s=setup(),session=s.Study.create(s.data,role,s.Study.empty(),'all',{paperId:'source-896-tcdf-002-01',now:start}),p={...s.Study.empty(),active:session};assert.equal(session.items.length,23);assert.ok(session.items.every(i=>i.paper.inventory.containsPreliminaryAnswers===true));assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));
 const references=p=>p.active.items.flatMap(i=>i.explanations.flatMap(e=>e.references));assert.ok(references(p).some(r=>r.documentId==='reference-mcasp-11-2025'));
 for(const url of ['https://www.tesourotransparente.gov.br.evil.example/manual','https://user:password@www.tesourotransparente.gov.br/manual']){const bad=plain(p);references(bad).find(r=>r.documentId==='reference-mcasp-11-2025').officialUrl=url;assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(bad),s.data));}
 const bad=plain(p);bad.active.items[0].paper.inventory.containsPreliminaryAnswers='false';assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(bad),s.data));
});
test('pre-reserve sessions keep their original text, keys, thematic snapshots and scores after additive mappings',()=>{
 const s=setup(),old=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-reserve-second-batch-catalog.json.gz'))));old.revision='c'.repeat(64);
 for(const id of [role,abdi,'camara-comunicacao-divulgacao'])for(const mode of ['all','exam']){let p={...s.Study.empty(),active:s.Study.create(old,id,s.Study.empty(),mode,{now:start,random:()=>.4})};p.active=s.Study.choose(p.active,p.active.items[0].key.value,'2026-10-28T12:01:00.000Z');const before=plain(p);assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),before);assert.equal(s.Study.matches(s.data,p.active),true);p=s.Study.finish(p,'2026-10-28T12:02:00.000Z');const points=s.Study.score(p.history[0]);const restored=s.Study.importBackup(s.Study.exportBackup(p),s.data);assert.deepEqual(plain(restored),plain(p));assert.deepEqual(plain(s.Study.score(restored.history[0])),plain(points));}
});
test('the official tautology holds for all eight valuations and new logic CE remain outside the FGV MC pool',()=>{
 const s=setup(),p=s.Study.empty(),q=s.data.questions.find(q=>q.id==='896-tcdf-cb1-01-q032');assert.equal(s.data.answerKeys.find(k=>k.id===q.answerKeyId).value,true);let rows=0;
 for(const a of [false,true])for(const b of [false,true])for(const c of [false,true]){const left=!a||(!b||c),right=!(a&&b)||c;assert.equal(left,right);rows++;}assert.equal(rows,8);
 const ce=s.Study.pool(s.data,abdi,p,'all',{paperId:'source-896-tcdf-cb1-01'});assert.equal(ce.length,2);assert.ok(ce.every(q=>q.type==='true_false'));assert.equal(s.Study.pool(s.data,abdi,p,'all',{paperId:'source-896-tcdf-cb1-01',type:'multiple_choice'}).length,0);
 const question=s.data.questions.find(q=>q.id==='abdi-2008-projetos-biotecnologia-q012');assert.equal(question.options.length,4);assert.equal(s.data.answerKeys.find(k=>k.id===question.answerKeyId).value,'b');
});
