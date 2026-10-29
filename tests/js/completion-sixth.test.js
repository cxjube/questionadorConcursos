'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib'),{webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'../..'),plain=x=>JSON.parse(JSON.stringify(x)),now='2026-10-29T14:00:00.000Z',roles=['camara-comunicacao-divulgacao','abdi-comunicacao-marketing','cgu-auditoria'];
function setup(){const s={window:{},URL,TextEncoder,crypto:webcrypto};vm.createContext(s);for(const f of ['assets/js/study.js','data/catalog.js'])vm.runInContext(fs.readFileSync(path.join(root,'docs',f),'utf8'),s);s.c=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-continuation-seventh-catalog.json.gz'))));s.c.revision='c'.repeat(64);s.old=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-completion-sixth-catalog.json.gz'))));s.old.revision='a'.repeat(64);s.m=JSON.parse(fs.readFileSync(path.join(root,'data/reviews/completion-sixth.json')));return s;}
test('current reviewed lot preserves formats, exact native quotas and immutable previous backups',()=>{
 const s=setup(),p=s.Study.empty(),newIds=new Set(s.m.items.map(i=>i.questionId));assert.equal(s.c.questions.length,709);assert.deepEqual(roles.map(r=>s.Study.pool(s.c,r,p).length),[409,251,320]);assert.equal(new Set(roles.flatMap(r=>s.Study.pool(s.c,r,p).map(q=>q.id))).size,709);
 assert.equal(s.c.questions.filter(q=>newIds.has(q.id)&&q.type==='true_false').length,6);assert.equal(s.c.questions.filter(q=>newIds.has(q.id)&&q.type==='multiple_choice').length,9);
 for(const [i,count] of [180,60,170].entries()){
  const current=s.Study.create(s.c,roles[i],p,'exam',{now,random:()=>.4});assert.equal(current.items.length,count);assert.equal(new Set(current.items.map(i=>i.question.id)).size,count);assert.equal(current.scoringProfile.rule.version,1);
  for(const block of current.scoringProfile.rule.blocks)assert.equal(current.items.filter(i=>i.examBlockId===block.id).length,block.questionCount);
  const old={...p,active:s.Study.create(s.old,roles[i],p,'exam',{now,random:()=>.4})};assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(old),s.c)),plain(old));
 }
 assert.deepEqual(plain(s.Study.examAvailability(s.c,roles[2]).blocks.map(b=>b.questions.length)),[71,92,172]);assert.equal(s.Study.pool(s.c,roles[1],p,'all',{block:'institutional',type:'multiple_choice'}).length,26);
});
test('additive RICD classification leaves the previous revision and performance unchanged',()=>{
 const s=setup(),p=s.Study.empty(),paper='source-camara-2014-consultor-cb2-03',qid='camara-2014-cb2-03-q084';
 let old={...p,active:s.Study.create(s.old,roles[0],p,'all',{paperId:paper,now})};const a=old.active.items.find(i=>i.question.id===qid);assert.equal(a.question.revision,1);assert.equal(a.mappings.length,1);old.active.answers.push({questionId:qid,value:a.key.value});old=s.Study.finish(old,'2026-10-29T14:10:00.000Z');const imported=s.Study.importBackup(s.Study.exportBackup(old),s.c);assert.deepEqual(plain(imported),plain(old));assert.deepEqual(plain(s.Study.performance(imported.history,roles[0])),plain(s.Study.performance(old.history,roles[0])));
 const b=s.Study.create(s.c,roles[0],p,'all',{paperId:paper,now}).items.find(i=>i.question.id===qid);assert.equal(b.question.revision,2);assert.equal(b.mappings.length,2);assert.equal(b.question.stem,a.question.stem);assert.deepEqual(plain(b.key),plain(a.key));assert.equal(s.c.questions.filter(q=>q.id===qid).length,1);
 for(const role of roles)assert.equal(s.Study.pool(s.c,role,p).some(q=>q.id==='cgu-2022-correicao-tarde-tipo1-q078'),false);
 const topicId=s.c.syllabusItems.find(i=>i.id==='cgu-2026-politicas-investigacao-avaliacao-4-2').topicId;assert.equal(s.Study.pool(s.c,roles[2],p,'all',{topicId}).length,0);
});
