'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib'),{webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'../..'),plain=x=>JSON.parse(JSON.stringify(x)),now='2026-10-29T14:00:00.000Z',roles=['camara-comunicacao-divulgacao','abdi-comunicacao-marketing','cgu-auditoria'];
function setup(){const s={window:{},URL,TextEncoder,crypto:webcrypto};vm.createContext(s);for(const f of ['assets/js/study.js','data/catalog.js'])vm.runInContext(fs.readFileSync(path.join(root,'docs',f),'utf8'),s);s.c=s.window.CONCURSOS_CATALOG;s.old=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-norms-gap-fifth-catalog.json.gz'))));s.old.revision='a'.repeat(64);return s;}
test('new questions and restored PAR preserve original formats, quotas, keys and previous snapshots',()=>{
 const s=setup(),p=s.Study.empty(),qid='cgu-2022-correicao-tarde-tipo1-q045';
 assert.equal(s.c.questions.length,694);assert.deepEqual(roles.map(r=>s.Study.pool(s.c,r,p).length),[409,251,305]);assert.equal(new Set(roles.flatMap(r=>s.Study.pool(s.c,r,p).map(q=>q.id))).size,694);
 const current=s.Study.create(s.c,roles[2],p,'all',{paperId:'source-cgu-2022-correicao-tarde-tipo1',now}),item=current.items.find(i=>i.question.id===qid);assert.ok(item);assert.equal(item.question.revision,3);assert.equal(item.key.value,'a');assert.equal(item.question.review.temporalScope,'historical_question');assert.match(item.explanations[0].text,/concorrente/);assert.match(item.explanations[0].text,/exclusiva/);
 const frozen=plain(s.old);assert.equal(s.Study.pool(frozen,roles[2],p).some(q=>q.id===qid),false);
 for(const [i,count] of [180,60,170].entries()){
  const a=s.Study.create(s.c,roles[i],p,'exam',{now,random:()=>.4});assert.equal(a.items.length,count);assert.equal(new Set(a.items.map(i=>i.question.id)).size,count);assert.equal(a.scoringProfile.rule.version,1);
  if(i!==1)assert.ok(a.items.every(i=>i.question.type==='true_false'));
  const old={...p,active:s.Study.create(s.old,roles[i],p,'exam',{now,random:()=>.4})};assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(old),s.c)),plain(old));
 }
 assert.deepEqual(plain(s.Study.examAvailability(s.c,roles[2]).blocks.map(b=>b.questions.length)),[71,90,166]);
 const logic=s.Study.pool(s.c,roles[1],p,'all',{syllabusItemId:'abdi-2026-raciocinio-logico-4'});assert.ok(logic.some(q=>q.id==='232funprespexe-cb1-01-q050'));assert.equal(s.Study.pool(s.c,roles[1],p,'all',{block:'institutional',type:'multiple_choice'}).length,26);
 // A pre-withdrawal attempt still carries revision1/keyA and imports unchanged.
 const prior=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-bank-sweep-catalog.json.gz'))));prior.revision='b'.repeat(64);const legacy={...p,active:s.Study.create(prior,roles[2],p,'all',{paperId:'source-cgu-2022-correicao-tarde-tipo1',now})};assert.equal(legacy.active.items.find(i=>i.question.id===qid).question.revision,1);assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(legacy),s.c)),plain(legacy));
});
test('Senado and CFC source references survive backups while spoofed hosts and credentials are rejected',()=>{
 const s=setup(),p=s.Study.empty();
 for(const [paper,host] of [['source-cgu-2022-correicao-tarde-tipo1','legis.senado.leg.br'],['source-993-tce-ac-016-01','www1.cfc.org.br']]){
  const active={...p,active:s.Study.create(s.c,roles[2],p,'all',{paperId:paper,now})};const refs=x=>x.active.items.flatMap(i=>i.explanations.flatMap(e=>e.references));assert.ok(refs(active).some(r=>r.officialUrl?.startsWith('https://'+host+'/')));assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(active),s.c)),plain(active));
  for(const url of ['https://'+host+'.evil.invalid/','https://user:secret@'+host+'/','http://'+host+'/']){const bad=plain(active);refs(bad).find(r=>r.officialUrl?.includes(host)).officialUrl=url;assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(bad),s.c));}
 }
});
