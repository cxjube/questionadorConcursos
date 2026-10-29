'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),zlib=require('node:zlib'),{webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'../..'),plain=x=>JSON.parse(JSON.stringify(x)),now='2026-10-29T21:00:00.000Z',roles=['camara-comunicacao-divulgacao','abdi-comunicacao-marketing','cgu-auditoria'];
function setup(){const s={window:{},URL,TextEncoder,crypto:webcrypto};vm.createContext(s);for(const f of ['assets/js/study.js','data/catalog.js'])vm.runInContext(fs.readFileSync(path.join(root,'docs',f),'utf8'),s);s.c=s.window.CONCURSOS_CATALOG;s.old=JSON.parse(zlib.gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-expansion-eighth-catalog.json.gz'))));s.old.revision='a'.repeat(64);s.m=JSON.parse(fs.readFileSync(path.join(root,'data/reviews/expansion-eighth.json')));return s;}
test('eighth lot keeps 34 original formats, every native quota and old721 backups',()=>{
 const s=setup(),p=s.Study.empty(),added=new Set(s.m.items.map(i=>i.questionId));assert.equal(s.c.questions.length,755);assert.deepEqual(roles.map(r=>s.Study.pool(s.c,r,p).length),[421,261,358]);assert.equal(new Set(roles.flatMap(r=>s.Study.pool(s.c,r,p).map(q=>q.id))).size,755);
 assert.equal(s.c.questions.filter(q=>added.has(q.id)&&q.type==='true_false').length,8);assert.equal(s.c.questions.filter(q=>added.has(q.id)&&q.type==='multiple_choice').length,26);
 for(const [i,count] of [180,60,170].entries()){
  const current=s.Study.create(s.c,roles[i],p,'exam',{now,random:()=>.4});assert.equal(current.items.length,count);assert.equal(new Set(current.items.map(i=>i.question.id)).size,count);assert.equal(current.scoringProfile.rule.version,1);
  for(const b of current.scoringProfile.rule.blocks){assert.equal(current.items.filter(i=>i.examBlockId===b.id).length,b.questionCount);for(const d of b.distribution||[])assert.equal(current.items.filter(i=>i.examBlockId===b.id&&i.examDisciplineId===d.disciplineId).length,d.questionCount);}
  if(i!==1)assert.ok(current.items.every(i=>i.question.type==='true_false'));
  for(const mode of ['all','exam']){const old={...p,active:s.Study.create(s.old,roles[i],p,mode,{now,random:()=>.4})};assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(old),s.c)),plain(old));}
 }
 assert.deepEqual(plain(s.Study.examAvailability(s.c,roles[2]).blocks.map(b=>b.questions.length)),[73,95,175]);assert.equal(s.Study.pool(s.c,roles[1],p,'all',{block:'institutional',type:'multiple_choice'}).length,26);
});
test('partial new samples keep all contexts and definitive keys without admitting excluded candidates',()=>{
 const s=setup(),p=s.Study.empty();
 for(const row of s.m.items){const role=s.c.syllabusItems.find(i=>i.id===row.syllabusItemIds[0]).roleId;const item=s.Study.create(s.c,role,p,'all',{paperId:row.paperId,now}).items.find(i=>i.question.id===row.questionId);assert.ok(item);assert.equal(item.key.value,row.answerValue);assert.deepEqual(plain(item.contexts.map(c=>c.id)),row.contextIds);assert.equal(item.question.type,row.paperId.includes('tcdf')?'true_false':'multiple_choice');}
 const topicId=s.c.syllabusItems.find(i=>i.id==='cgu-2026-politicas-investigacao-avaliacao-4-2').topicId;const mixed=s.Study.pool(s.c,roles[2],p,'all',{topicId});assert.equal(mixed.length,1);assert.equal(mixed[0].id,'cgesp-2025-fin-pm-q057');
 for(const qid of ['cgu-2022-correicao-tarde-tipo1-q046','cgu-2022-correicao-tarde-tipo1-q078','cgesp-2025-audit-pm-q003','cgesp-2025-audit-pm-q014','tcdf-2024-psicologia-002-01-q148'])assert.equal(s.c.questions.some(q=>q.id===qid),false);
 assert.equal(s.c.papers.find(p=>p.id==='source-tcdf-2024-psicologia-002-01').inventory.containsPreliminaryAnswers,true);
});
