'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib'),{webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'../..'),plain=x=>JSON.parse(JSON.stringify(x)),date='2026-10-28T12:00:00.000Z';
function setup(){const s={window:{},URL,TextEncoder,crypto:webcrypto};vm.createContext(s);for(const f of ['assets/js/study.js','data/catalog.js'])vm.runInContext(fs.readFileSync(path.join(root,'docs',f),'utf8'),s);s.c=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-bank-sweep-catalog.json.gz'))));s.c.revision='b'.repeat(64);return s;}
test('42 real additions preserve original CE and MC formats, new historical-item notices and backups',()=>{
 const s=setup(),p=s.Study.empty(),manifest=JSON.parse(fs.readFileSync(path.join(root,'data/reviews/gaps-fourth-batch.json'))),seen=new Set();
 for(const role of ['camara-comunicacao-divulgacao','abdi-comunicacao-marketing','cgu-auditoria']){
  const session=s.Study.create(s.c,role,p,'all',{now:date});const added=session.items.filter(i=>manifest.items.some(r=>r.questionId===i.question.id));for(const i of added)seen.add(i.question.id);
  const saved={...p,active:session};assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(saved),s.c)),plain(saved));
  for(const i of added.filter(i=>i.question.review.temporalScope==='historical_question')){assert.ok(i.question.review.temporalNote);const tampered=plain(saved);tampered.active.items.find(v=>v.question.id===i.question.id).question.review.temporalScope='invented';assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(tampered),s.c));}
 }
 assert.equal(seen.size,42);const abdi=s.Study.pool(s.c,'abdi-comunicacao-marketing',p,'all',{paperId:'source-abdi-2008-iniciante-licitacoes-contratos'}).find(q=>q.origin.number===20);assert.equal(abdi.options.length,4);assert.equal(abdi.review.temporalScope,'historical_question');
});
test('all three native engines retain exact distinct-ID composition and original rule versions',()=>{
 const s=setup(),p=s.Study.empty();assert.equal(s.c.questions.length,686);
 for(const [role,count,type] of [['camara-comunicacao-divulgacao',180,'true_false'],['abdi-comunicacao-marketing',60,'multiple_choice'],['cgu-auditoria',170,'true_false']]){const session=s.Study.create(s.c,role,p,'exam',{now:date,random:()=>.4});assert.equal(session.items.length,count);assert.equal(new Set(session.items.map(i=>i.question.id)).size,count);assert.ok(session.items.every(i=>i.question.type===type));assert.equal(session.scoringProfile.rule.version,1);}
 const cgu=s.Study.examAvailability(s.c,'cgu-auditoria');assert.equal(cgu.distinct,262);assert.deepEqual(plain(cgu.blocks.map(b=>b.questions.length)),[71,90,162]);
 const ethics=s.Study.pool(s.c,'abdi-comunicacao-marketing',p,'all',{disciplineId:'abdi-etica-missao',type:'multiple_choice'});assert.equal(ethics.length,9);for(const q of ethics){const withdrawn=plain(s.c);const k=withdrawn.answerKeys.find(k=>k.id===q.answerKeyId);k.result='withdrawn';k.value=null;assert.equal(s.Study.create(withdrawn,'abdi-comunicacao-marketing',p,'exam',{now:date}).items.length,60);}
});
test('old 644-item session snapshots remain unchanged and match after the additive lot',()=>{
 const s=setup(),p=s.Study.empty(),old=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-gaps-fourth-batch-catalog.json.gz'))));old.revision='a'.repeat(64);
 for(const role of ['camara-comunicacao-divulgacao','abdi-comunicacao-marketing','cgu-auditoria']){const saved={...p,active:s.Study.create(old,role,p,'exam',{now:date,random:()=>.4})};assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(saved),s.c)),plain(saved));assert.equal(s.Study.matches(s.c,saved.active),true);}
});
