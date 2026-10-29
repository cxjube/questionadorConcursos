'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib'),{webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'../..'),plain=x=>JSON.parse(JSON.stringify(x)),now='2026-10-29T14:00:00.000Z',roles=['camara-comunicacao-divulgacao','abdi-comunicacao-marketing','cgu-auditoria'];
function setup(){const s={window:{},URL,TextEncoder,crypto:webcrypto};vm.createContext(s);for(const f of ['assets/js/study.js','data/catalog.js'])vm.runInContext(fs.readFileSync(path.join(root,'docs',f),'utf8'),s);s.c=s.window.CONCURSOS_CATALOG;s.old=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-continuation-seventh-catalog.json.gz'))));s.old.revision='a'.repeat(64);s.m=JSON.parse(fs.readFileSync(path.join(root,'data/reviews/continuation-seventh.json')));return s;}
test('seventh lot preserves original formats, all native quotas and the previous709 snapshots',()=>{
 const s=setup(),p=s.Study.empty(),added=new Set(s.m.items.map(i=>i.questionId));assert.equal(s.c.questions.length,721);assert.deepEqual(roles.map(r=>s.Study.pool(s.c,r,p).length),[415,258,329]);assert.equal(new Set(roles.flatMap(r=>s.Study.pool(s.c,r,p).map(q=>q.id))).size,721);
 assert.equal(s.c.questions.filter(q=>added.has(q.id)&&q.type==='true_false').length,1);assert.equal(s.c.questions.filter(q=>added.has(q.id)&&q.type==='multiple_choice').length,11);
 for(const [i,count] of [180,60,170].entries()){
  const current=s.Study.create(s.c,roles[i],p,'exam',{now,random:()=>.4});assert.equal(current.items.length,count);assert.equal(new Set(current.items.map(i=>i.question.id)).size,count);assert.equal(current.scoringProfile.rule.version,1);
  for(const block of current.scoringProfile.rule.blocks)assert.equal(current.items.filter(i=>i.examBlockId===block.id).length,block.questionCount);
  if(i!==1)assert.ok(current.items.every(i=>i.question.type==='true_false'));
  for(const mode of ['all','exam']){const old={...p,active:s.Study.create(s.old,roles[i],p,mode,{now,random:()=>.4})};assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(old),s.c)),plain(old));}
 }
 assert.deepEqual(plain(s.Study.examAvailability(s.c,roles[2]).blocks.map(b=>b.questions.length)),[72,93,172]);assert.equal(s.Study.pool(s.c,roles[1],p,'all',{block:'institutional',type:'multiple_choice'}).length,26);
});
test('historical SIPEF text remains visible and narrow exclusions do not fill neighboring gaps',()=>{
 const s=setup(),p=s.Study.empty(),qid='cgu-2022-correicao-tarde-tipo1-q037';
 const session=s.Study.create(s.c,roles[2],p,'all',{paperId:'source-cgu-2022-correicao-tarde-tipo1',now});const item=session.items.find(i=>i.question.id===qid);assert.ok(item);assert.equal(item.key.value,'d');assert.equal(item.question.review.temporalScope,'historical_question');assert.match(item.question.review.temporalNote,/SITAI/);assert.match(item.question.stem,/10.756/);assert.match(item.explanations[0].text,/7º,V/);
 const finished=s.Study.finish({...p,active:{...session,answers:[{questionId:qid,value:'d'}]}},'2026-10-29T14:10:00.000Z');assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(finished),s.c)),plain(finished));
 for(const id of ['cgu-2022-correicao-tarde-tipo1-q046','cgu-2022-correicao-tarde-tipo1-q078'])assert.equal(s.Study.pool(s.c,roles[2],p).some(q=>q.id===id),false);
 const topicId=s.c.syllabusItems.find(i=>i.id==='cgu-2026-politicas-investigacao-avaliacao-4-2').topicId;assert.equal(s.Study.pool(s.c,roles[2],p,'all',{topicId}).length,0);
 assert.equal(s.Study.pool(s.c,roles[1],p,'all',{paperId:'source-cge-ce-2019-cargo5',block:'institutional'}).length,0);
 const research=s.Study.create(s.c,roles[1],p,'all',{paperId:'source-539-alce-016-01',now}).items.find(i=>i.question.id==='539-alce-016-01-q058');assert.equal(research.key.value,'b');assert.equal(research.question.options.length,5);assert.match(research.question.stem,/IV O pré-testes/);
});
