'use strict';
// Synthetic quota fixtures live only in isolated copied catalogs in this test.
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path'),{webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'../..'),role='abdi-comunicacao-marketing',start='2026-10-27T12:00:00.000Z';
const plain=x=>JSON.parse(JSON.stringify(x));
function setup(complete=true){
 const s={window:{},crypto:webcrypto,URL,TextEncoder};vm.createContext(s);for(const f of ['assets/js/study.js','data/catalog.js'])vm.runInContext(fs.readFileSync(path.join(root,'docs',f),'utf8'),s);s.data=s.window.CONCURSOS_CATALOG;
 const institutional=new Set(s.data.syllabusItems.filter(i=>i.roleId===role && i.block==='institutional').map(i=>i.id));if(complete!=='native')s.data.mappings=s.data.mappings.filter(m=>!institutional.has(m.syllabusItemId));
 if(complete===true){const template=s.data.questions.find(q=>q.type==='multiple_choice'),key=s.data.answerKeys.find(k=>k.id===template.answerKeyId);let n=0;
  for(const quota of s.data.scoringRules.find(r=>r.roleId===role).blocks[1].distribution){const topic=s.data.topics.find(t=>t.disciplineId===quota.disciplineId && institutional.has(t.id));for(let i=0;i<quota.questionCount;i++){
   const id='synthetic-institutional-test-'+(++n),q=plain(template);q.id=id;q.stem='SYNTHETIC TEST FIXTURE ONLY '+n;q.contextIds=[];q.answerKeyId=id+'-key';q.origin.number=1000+n;s.data.questions.push(q);s.data.answerKeys.push({...plain(key),id:q.answerKeyId,questionId:id});s.data.mappings.push({id:id+'-mapping',questionId:id,syllabusItemId:topic.id,status:'confirmed'});
  }}
 }
 return s;
}
function active(s){return {...s.Study.empty(),active:s.Study.create(s.data,role,s.Study.empty(),'exam',{now:start,id:'synthetic-abdi-exam-test',random:()=>.4})};}
function withCounts(s,counts){let p=active(s);for(const [index,count] of counts.entries())for(const item of p.active.items.filter(i=>i.examBlockId===['basic','institutional','specific'][index]).slice(0,count))p.active.answers.push({questionId:item.question.id,value:item.key.value});return s.Study.finish(p,'2026-10-27T13:00:00.000Z');}

test('ABDI exam allocates 60 unique original MC across exact 8/6/6 and 4/4/8/4 quotas',()=>{
 const s=setup(),before=JSON.stringify(s.data),p=active(s),a=p.active,rule=s.data.scoringRules.find(r=>r.roleId===role);
 assert.equal(JSON.stringify(s.data),before);assert.equal(a.items.length,60);assert.equal(new Set(a.items.map(i=>i.question.id)).size,60);assert.equal(a.selection.type,'multiple_choice');assert.equal(a.timer.durationSeconds,12600);assert.equal(a.timer.deadlineAt,'2026-10-27T15:30:00.000Z');assert.deepEqual(plain(a.scoringProfile.rule),plain(rule));
 for(const [i,b] of rule.blocks.entries()){assert.ok(a.items.slice(i*20,(i+1)*20).every(q=>q.examBlockId===b.id && q.question.type==='multiple_choice' && q.key.result==='valid'));for(const d of b.distribution)assert.equal(a.items.filter(q=>q.examBlockId===b.id && q.examDisciplineId===d.disciplineId).length,d.questionCount);}
 assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));
});
test('ABDI weighted points, thirty correct and positive scores in all areas are independent',()=>{
 const s=setup();for(const [counts,points,meets] of [[[20,9,1],9.35,true],[[1,1,20],13.6,false],[[20,10,0],9,false],[[0,10,20],16,false],[[10,0,20],16,false],[[9,1,20],16,true],[[20,20,20],25,true],[[0,0,0],0,false]]){
  const p=withCounts(s,counts),r=s.Study.score(p.history[0]);assert.equal(r.points,points);assert.equal(r.maximum,25);assert.equal(r.minimum,null);assert.equal(r.minimumCorrectCount,30);assert.equal(r.correctMet,counts.reduce((a,b)=>a+b,0)>=30);assert.equal(r.meetsMinimums,meets);assert.equal(r.totalMet,r.correctMet);assert.ok(r.blocks.every((b,i)=>b.met===(counts[i]>0)));assert.equal(s.Study.totals(p.history[0]).correct,counts.reduce((a,b)=>a+b,0));
 }
});
test('ABDI empty institutional quota blocks exams and exposes exact shortages without blocking practice',()=>{
 const s=setup(false),a=s.Study.examAvailability(s.data,role);assert.equal(a.ready,false);assert.equal(a.rule.roleId,role);assert.match(a.reason,/insuficiente/);assert.equal(a.missing.reduce((n,d)=>n+d.count,0),20);assert.deepEqual(plain(a.missing.map(x=>x.count)),[4,4,8,4]);assert.throws(()=>active(s),/insuficiente/);assert.ok(s.Study.create(s.data,role,s.Study.empty(),'all',{limit:1}));
});
test('quota matching detects deficient subsets even with enough questions overall and in each discipline',()=>{
 const s=setup(),sy=new Map(s.data.syllabusItems.map(i=>[i.id,i])),topics=new Map(s.data.topics.map(t=>[t.id,t]));
 const port=s.Study.pool(s.data,role,s.Study.empty(),'all',{disciplineId:'lingua-portuguesa',type:'multiple_choice'}),rlm=s.data.syllabusItems.find(x=>x.roleId===role && topics.get(x.topicId).disciplineId==='raciocinio-logico');
 s.data.mappings=s.data.mappings.filter(m=>sy.get(m.syllabusItemId)?.roleId!==role || topics.get(sy.get(m.syllabusItemId)?.topicId)?.disciplineId!=='raciocinio-logico');
 for(const q of port)s.data.mappings.push({id:'synthetic-overlap-'+q.id,questionId:q.id,syllabusItemId:rlm.id,status:'confirmed'});
 // Extra questions in the specific area cannot compensate a Portuguese/Logic shortage.
 const template=port[0],key=s.data.answerKeys.find(k=>k.id===template.answerKeyId),specific=s.data.syllabusItems.find(i=>i.roleId===role && i.block==='specific');
 for(let n=0;n<10;n++){const id='synthetic-surplus-test-'+n,q={...plain(template),id,stem:'SYNTHETIC SURPLUS TEST ONLY '+n,answerKeyId:id+'-key',contextIds:[]};s.data.questions.push(q);s.data.answerKeys.push({...plain(key),id:q.answerKeyId,questionId:id});s.data.mappings.push({id:id+'-mapping',questionId:id,syllabusItemId:specific.id,status:'confirmed'});}
 const a=s.Study.examAvailability(s.data,role);assert.ok(a.distinct>=60);assert.ok(a.slots.every(slot=>slot.questions.length>=slot.questionCount));assert.equal(a.ready,false);assert.throws(()=>active(s),/insuficiente/);
});
test('ABDI backups reject quota, block, criteria and timing tampering and preserve older rule versions',()=>{
 const s=setup(),p=active(s),before=JSON.stringify(p);
 for(const mutate of [p=>p.active.scoringProfile.rule.minimumCorrectCount=1,p=>p.active.scoringProfile.rule.minimumTotalScore=0,p=>p.active.scoringProfile.rule.blocks[0].distribution[0].questionCount++,p=>p.active.scoringProfile.rule.blocks[0].minimumScoreExclusive=false,p=>p.active.items[0].examDisciplineId='abdi-comunicacao-marketing',p=>p.active.items[20].examBlockId='specific',p=>p.active.items[20]=p.active.items[0],p=>p.active.selection.type='true_false',p=>p.active.timer.durationSeconds=18000]){const bad=plain(p);mutate(bad);assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(bad),s.data));}
 assert.equal(JSON.stringify(p),before);const raw=s.Study.exportBackup(withCounts(s,[20,9,1]));const rule=s.data.scoringRules.find(r=>r.roleId===role);rule.version++;rule.minimumCorrectCount=35;const old=s.Study.importBackup(raw,s.data);assert.equal(s.Study.score(old.history[0]).points,9.35);assert.equal(s.Study.score(old.history[0]).meetsMinimums,true);
});
test('ABDI deadline survives reload, expires exactly once and cannot inherit custom practice settings',()=>{
 const s=setup();let p=active(s);p.active=s.Study.choose(p.active,p.active.items[0].key.value,'2026-10-27T12:01:00.000Z');p=s.Study.importBackup(s.Study.exportBackup(p),s.data);assert.equal(p.active.answers.length,1);assert.equal(s.Study.remaining(p.active,'2026-10-27T15:29:59.000Z'),1);assert.throws(()=>s.Study.choose(p.active,null,'2026-10-27T15:30:00.000Z'),/terminou/);p=s.Study.finish(p,'2026-10-27T16:00:00.000Z');assert.equal(p.history[0].finishedAt,'2026-10-27T15:30:00.000Z');assert.deepEqual(plain(s.Study.finish(p)),plain(p));for(const settings of [{limit:5},{block:'institutional'},{durationMinutes:5},{scoringMode:'net'}])assert.throws(()=>s.Study.create(s.data,role,s.Study.empty(),'exam',settings),/fixados/);
});

test('original four-choice MC remain four-choice in exam snapshots without inventing an option E',()=>{
 const s=setup(),q=s.data.questions.find(q=>q.id==='synthetic-institutional-test-1'),key=s.data.answerKeys.find(k=>k.id===q.answerKeyId);assert.notEqual(key.value,'e');q.options=q.options.slice(0,4);
 const p=active(s),item=p.active.items.find(i=>i.question.id===q.id);assert.equal(item.question.options.length,4);assert.deepEqual(plain(item.question.options.map(o=>o.id)),['a','b','c','d']);assert.equal(s.Study.grade(item,key.value),'correct');assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));
});

test('new institutional and IBFC official links round-trip while lookalike domains and credentials fail',()=>{
 const s=setup('native'),session=s.Study.create(s.data,role,s.Study.empty(),'all',{paperId:'source-abdi-2008-especialista-juridico',limit:1,now:start});let p={...s.Study.empty(),active:session};assert.equal(session.items[0].question.options.length,4);assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));
 for(const url of ['https://www2.ibfc.org.br.evil.example/key.pdf','https://user:password@www2.ibfc.org.br/key.pdf','https://www.abdi.com.br.evil.example/ethics.pdf']){const bad=plain(p);bad.active.items[0].paper.officialUrl=url;assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(bad),s.data));}
 const bad=plain(p);bad.active.items[0].explanations[0].references[2].officialUrl='https://www.abdi.com.br.evil.example/statute.pdf';assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(bad),s.data));
});

test('historical third-lot shortage remains documented while the real fourth-lot exam fills all quotas',()=>{
 const s=setup('native'),a=s.Study.examAvailability(s.data,role),r=JSON.parse(fs.readFileSync(path.join(root,'data/reviews/abdi-bank-readiness.json')));
 assert.equal(a.ready,true);assert.equal(a.missing.length,0);assert.equal(r.quotaCheck.allocatableDistinctMC,60);assert.equal(s.Study.pool(s.data,role,s.Study.empty(),'all',{block:'institutional',type:'multiple_choice'}).length,20);
 const old=JSON.parse(require('node:zlib').gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-abdi-fourth-batch-catalog.json.gz'))));old.revision='a'.repeat(64);assert.equal(s.Study.examAvailability(old,role).ready,false);const previous=s.Study.create(old,role,s.Study.empty(),'all',{now:start});assert.equal(previous.items.length,218);
 const restored=s.Study.importBackup(s.Study.exportBackup({...s.Study.empty(),active:previous}),s.data);assert.deepEqual(plain(restored.active),plain(previous));
 const p=active(s),session=p.active,ids=session.items.map(i=>i.question.id);assert.equal(ids.length,60);assert.equal(new Set(ids).size,60);assert.ok(ids.every(id=>!id.startsWith('synthetic-')));
 for(const block of session.scoringProfile.rule.blocks){assert.equal(session.items.filter(i=>i.examBlockId===block.id).length,20);for(const quota of block.distribution)assert.equal(session.items.filter(i=>i.examBlockId===block.id && i.examDisciplineId===quota.disciplineId).length,quota.questionCount);}
 assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));
 const correct=withCounts(s,[20,20,20]);assert.equal(s.Study.score(correct.history[0]).points,25);assert.equal(s.Study.score(correct.history[0]).meetsMinimums,true);
 const fiocruz=session.items.find(i=>i.paper.officialUrl.includes('fiocruz.br'));assert.ok(fiocruz);const bad=plain(p),item=bad.active.items.find(i=>i.question.id===fiocruz.question.id);item.paper.officialUrl='https://concurso2023.fiotec.fiocruz.br.evil.example/paper.pdf';assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(bad),s.data));
});
