'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const {webcrypto} = require('node:crypto');
const root = path.resolve(__dirname, '../..');
const plain = value => JSON.parse(JSON.stringify(value));
function setup(local) {
 const entries = new Map();
 const storage = local || {getItem:key=>entries.get(key)??null,setItem:(key,value)=>entries.set(key,value)};
 const context = {window:{localStorage:storage},crypto:webcrypto,URL,TextEncoder};
 vm.createContext(context);
 for (const file of ['study','progress']) vm.runInContext(fs.readFileSync(path.join(root,'docs/assets/js/'+file+'.js'),'utf8'),context);
 vm.runInContext(fs.readFileSync(path.join(root,'docs/data/catalog.js'),'utf8'),context);
 const data=context.window.CONCURSOS_CATALOG;
 return {...context,data,role:data.roles[0].id,entries};
}
function active(s, mode='all', id='test-session') {
 return {...s.Study.empty(), active:s.Study.create(s.data,s.role,s.Study.empty(),mode,{id,now:'2026-10-23T12:00:00.000Z'})};
}
const finishedAt='2026-10-23T12:10:00.000Z';
test('draw uses reviewed role mappings once per question and preserves contexts',()=>{
 const s=setup();const p=active(s);
 assert.equal(p.active.items.length,s.data.questions.length);
 assert.equal(new Set(p.active.items.map(i=>i.question.id)).size,s.data.questions.length);
 assert.equal(s.Study.pool(s.data,'abdi-futuro',p).length,0);
 const shared=p.active.items.filter(i=>i.question.origin.number===22||i.question.origin.number===23);
 assert.equal(shared.length,2);assert.equal(shared[0].contexts[0].id,shared[1].contexts[0].id);
 const stem=p.active.items[0].question.stem;s.data.questions[0].stem='SYNTHETIC MUTATION TEST ONLY';
 assert.equal(p.active.items[0].question.stem,stem);
});
test('false, blank, missing choices and option E remain distinct',()=>{
 const s=setup();let p=active(s);const first=p.active;
 p.active=s.Study.choose(p.active,false);
 assert.equal(first.answers.length,0);assert.equal(p.active.answers[0].value,false);
 assert.equal(s.Study.grade(p.active.items[0],false),'incorrect');
 assert.equal(s.Study.grade(p.active.items[0],null),'blank');
 assert.throws(()=>s.Study.choose(p.active,'e'));
 const index=p.active.items.findIndex(i=>i.question.type==='multiple_choice'&&i.key.value==='e');
 p.active=s.Study.move(p.active,index);p.active=s.Study.choose(p.active,'e');
 assert.equal(s.Study.grade(p.active.items[index],'e'),'correct');
 assert.throws(()=>s.Study.choose(p.active,false));
});
test('navigation and changed drafts never create attempts; finalization is idempotent',()=>{
 const s=setup();let p=active(s);
 p.active=s.Study.choose(p.active,false);p.active=s.Study.choose(p.active,true);
 p.active=s.Study.move(p.active,1);p.active=s.Study.move(p.active,0);
 assert.equal(p.history.length,0);assert.equal(p.active.answers.length,1);
 p=s.Study.finish(p,finishedAt);
 assert.equal(p.history.length,1);assert.equal(p.active,null);
 assert.equal(s.Study.totals(p.history[0]).correct,1);assert.equal(s.Study.totals(p.history[0]).blank,s.data.questions.length-1);
 assert.equal(s.Study.totals(p.history[0]).rate,100);
 assert.deepEqual(plain(s.Study.finish(p,finishedAt)),plain(p));
 assert.deepEqual(plain(s.Study.finish({...p,active:{...p.history[0],finishedAt:null}},finishedAt)),plain(p));
});
test('zero valid responses has no artificial zero-percent score or official profile',()=>{
 const s=setup();const p=s.Study.finish(active(s),finishedAt);const result=s.Study.totals(p.history[0]);
 assert.equal(result.rate,null);assert.equal(result.blank,s.data.questions.length);assert.equal(p.history[0].scoringProfile,null);
});
test('new sessions never exceed the history limit accepted by restore',()=>{
 const s=setup();const progress=s.Study.empty();progress.history=Array(500).fill({});
 assert.throws(()=>s.Study.create(s.data,s.role,progress),/500 sessões/);
});
test('review errors uses latest finalized outcome and does not treat blanks as errors',()=>{
 const s=setup();let p=active(s);p.active=s.Study.choose(p.active,false);p=s.Study.finish(p,finishedAt);
 assert.equal(s.Study.pool(s.data,s.role,p,'errors').length,1);
 assert.equal(s.Study.pool(s.data,s.role,p,'blank').length,s.data.questions.length-1);
 assert.equal(s.Study.pool(s.data,s.role,p,'unanswered').length,0);
 p.active=s.Study.create(s.data,s.role,p,'errors',{id:'review-session',now:'2026-10-23T12:11:00.000Z'});
 p.active=s.Study.choose(p.active,true);p=s.Study.finish(p,'2026-10-23T12:12:00.000Z');
 assert.equal(s.Study.pool(s.data,s.role,p,'errors').length,0);
 s.data.questions[0].revision+=1;
 assert.equal(s.Study.pool(s.data,s.role,p,'unanswered').length,1);
});
test('backup round trip preserves drafts and snapshots; invalid input never mutates original',()=>{
 const s=setup();let p=active(s);p.active=s.Study.choose(p.active,false);
 const raw=s.Study.exportBackup(p);const restored=s.Study.importBackup(raw,s.data);
 assert.deepEqual(plain(restored),plain(p));assert.equal(restored.active.answers[0].value,false);
 const before=JSON.stringify(p);
 for(const corrupt of ['{','{}',JSON.stringify({format:'questionador-concursos-backup',version:8,progress:p})])assert.throws(()=>s.Study.importBackup(corrupt,s.data));
 assert.equal(JSON.stringify(p),before);
 const malicious=JSON.parse(raw);malicious.progress.active.items[0].key.officialUrl='javascript:alert(1)';
 assert.throws(()=>s.Study.importBackup(JSON.stringify(malicious),s.data));
});
test('backup rejects duplicate sessions, bad positions, type mismatches and altered current keys',()=>{
 const s=setup();const original=active(s);
 for(const mutate of [p=>p.active.position=99,p=>p.active.answers=[{questionId:p.active.items[0].question.id,value:'false'}],p=>p.active.items[0].key.value=false,p=>p.history=[{...p.active,finishedAt}]]){
  const p=plain(original);mutate(p);assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(p),s.data));
 }
 const p=plain(original);p.active.items[0].question.revision=0;
 assert.throws(()=>s.Study.validate(p,s.data));
 assert.throws(()=>s.Study.importBackup(' '.repeat(s.Study.MAX_BYTES+1),s.data));
});
test('historical snapshots survive catalog updates and import without rewriting past answers',()=>{
 const s=setup();let p=active(s);p.active=s.Study.choose(p.active,true);p=s.Study.finish(p,finishedAt);
 const raw=s.Study.exportBackup(p);s.data.questions[0].revision+=1;s.data.questions[0].stem+=' SYNTHETIC UPDATE TEST ONLY';
 const restored=s.Study.importBackup(raw,s.data);
 assert.equal(s.Study.matches(s.data,restored.history[0]),false);
 assert.equal(s.Study.totals(restored.history[0]).correct,1);
 assert.notEqual(restored.history[0].items[0].question.stem,s.data.questions[0].stem);
});
test('atomic persistence restores active answers and completed history together',async()=>{
 const s=setup();const store=s.Progress.open(s.data);let p=active(s);p.active=s.Study.choose(p.active,false);
 assert.equal(await s.Progress.save(store,p),true);
 const restored=s.Progress.open(s.data);assert.equal(restored.state.active.answers[0].value,false);
 const finished=s.Study.finish(restored.state,finishedAt);await s.Progress.save(restored,finished);
 const reopened=s.Progress.open(s.data);assert.equal(reopened.state.active,null);assert.equal(reopened.state.history.length,1);
});
test('another tab cannot silently replace a newer record; unsaved draft remains exportable',async()=>{
 const s=setup();const a=s.Progress.open(s.data),b=s.Progress.open(s.data);
 await s.Progress.save(a,active(s));const before=s.entries.get(s.Progress.KEY);
 const next=active(s,'all','other-session');
 await assert.rejects(s.Progress.save(b,next),/Outra aba/);
 assert.equal(s.entries.get(s.Progress.KEY),before);assert.equal(b.state.active.id,'other-session');
 assert.ok(s.Study.importBackup(s.Study.exportBackup(b.state),s.data));
});
test('blocked/quota storage keeps study usable in memory without claiming a save',async()=>{
 const blocked=setup({getItem(){throw Error('blocked');},setItem(){throw Error('blocked');}});
 const b=blocked.Progress.open(blocked.data);assert.equal(b.readOnly,true);
 assert.equal(await blocked.Progress.save(b,active(blocked)),false);assert.equal(b.state.active.items.length,blocked.data.questions.length);
 const quota=setup({getItem(){return null;},setItem(){throw Error('quota');}});const q=quota.Progress.open(quota.data);
 assert.equal(await quota.Progress.save(q,active(quota)),false);assert.match(q.error,/Não foi possível salvar/);
 assert.ok(quota.Study.exportBackup(q.state));
});
test('corrupt original bytes are retained and never overwritten implicitly',async()=>{
 let raw='{ invalid original';const s=setup({getItem(){return raw;},setItem(k,v){raw=v;}});
 const store=s.Progress.open(s.data);assert.equal(store.readOnly,true);assert.equal(store.raw,raw);
 await s.Progress.save(store,active(s));assert.equal(raw,'{ invalid original');
 assert.match(store.error,/preservado/);
});

test('subject filters include descendants, respect the role and count canonical questions once',()=>{
 const s=setup(), progress=s.Study.empty();
 const parent=s.Study.pool(s.data,s.role,progress,'all',{disciplineId:'comunicacao-social',topicId:'comunicacao-social-7'});
 const child=s.Study.pool(s.data,s.role,progress,'all',{topicId:'comunicacao-social-7-1'});
 assert.equal(parent.length,6);assert.deepEqual(plain(parent),plain(child));
 const mapped=s.data.mappings.find(m=>m.questionId===parent[0].id);
 s.data.mappings.push({...mapped,id:'synthetic-duplicate-mapping-for-test-only'});
 assert.equal(s.Study.pool(s.data,s.role,progress,'all',{topicId:'comunicacao-social-7'}).length,6);
 assert.equal(s.Study.pool(s.data,s.role,progress,'all',{topicId:'comunicacao-social-2'}).length,5);
 for(const filters of [{disciplineId:'missing-test-only'},{topicId:'missing-test-only'},{disciplineId:'lingua-portuguesa',topicId:'comunicacao-social-7'}]) {
  assert.throws(()=>s.Study.pool(s.data,s.role,progress,'all',filters),/inválido/);
 }
 assert.equal(s.Study.pool(s.data,'abdi-futuro',progress).length,0);
 assert.throws(()=>s.Study.pool(s.data,'abdi-futuro',progress,'all',{topicId:'comunicacao-social-7'}),/inválido/);
});
test('custom quantity and draw preserve sources, options and contexts without repetition',()=>{
 const s=setup(), progress=s.Study.empty(), before=JSON.stringify(s.data);
 const filters={disciplineId:'comunicacao-social',topicId:'comunicacao-social-2'};
 const pool=s.Study.pool(s.data,s.role,progress,'all',filters);
 const session=s.Study.create(s.data,s.role,progress,'all',{...filters,limit:2,shuffle:true,random:()=>0});
 assert.equal(session.items.length,2);assert.equal(new Set(session.items.map(i=>i.question.id)).size,2);
 assert.deepEqual(plain(session.items.map(i=>i.question.id)),plain(pool.slice(1,3).map(q=>q.id)));
 for(const item of session.items) assert.deepEqual(plain(item),plain(s.Study.snapshot(s.data,s.data.questions.find(q=>q.id===item.question.id),s.role)));
 assert.equal(JSON.stringify(s.data),before);assert.equal(session.scoringProfile,null);
 for(const limit of [0,-1,1.5,'2',6,NaN]) assert.throws(()=>s.Study.create(s.data,s.role,progress,'all',{...filters,limit}),/quantidade/);
 assert.throws(()=>s.Study.create(s.data,s.role,progress,'all',{disciplineId:'lingua-inglesa'}),/Não há questões/);
});
test('filtered errors use finalized outcomes and ignore unfinished choices',()=>{
 const s=setup(), settings={topicId:'comunicacao-social-7',limit:1};let p=s.Study.empty();
 p.active=s.Study.create(s.data,s.role,p,'all',settings);
 const item=p.active.items[0];
 const wrong=item.question.type==='true_false' ? !item.key.value : item.question.options.find(o=>o.id!==item.key.value).id;
 p.active=s.Study.choose(p.active,wrong);
 assert.equal(s.Study.pool(s.data,s.role,p,'errors',settings).length,0);
 p=s.Study.finish(p);
 assert.equal(s.Study.pool(s.data,s.role,p,'errors',settings).length,1);
 assert.equal(s.Study.pool(s.data,s.role,p,'errors',{topicId:'comunicacao-social-2'}).length,0);
});
test('custom and legacy backups resume the exact selection even after taxonomy changes',()=>{
 const s=setup();const p={...s.Study.empty(),active:s.Study.create(s.data,s.role,s.Study.empty(),'all',{disciplineId:'comunicacao-social',topicId:'comunicacao-social-2',limit:2,shuffle:true,random:()=>0})};
 const raw=s.Study.exportBackup(p);s.data.topics.find(t=>t.id==='comunicacao-social-2').label='SYNTHETIC RENAME TEST ONLY';
 const restored=s.Study.importBackup(raw,s.data);assert.deepEqual(plain(restored),plain(p));
 const legacy=plain(p);delete legacy.active.selection;
 assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(legacy),s.data)),legacy);
 for(const mutate of [p=>p.active.selection.limit=3,p=>p.active.selection.shuffle='yes',p=>p.active.selection.topicLabel=null]) {
  const broken=plain(p);mutate(broken);assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(broken),s.data));
 }
});

test('performance counts distinct questions, repeated attempts and each mapping group without duplicating totals',()=>{
 const s=setup();let p=s.Study.empty();
 const settings={topicId:'comunicacao-social-7',limit:1,id:'first-metrics',now:'2026-10-23T12:00:00.000Z'};
 p.active=s.Study.create(s.data,s.role,p,'all',settings);
 const q=p.active.items[0].question;
 p.active=s.Study.choose(p.active,q.options.find(o=>o.id!==p.active.items[0].key.value).id);
 p=s.Study.finish(p,finishedAt);
 p.active=s.Study.create(s.data,s.role,p,'all',{...settings,id:'second-metrics',now:'2026-10-23T12:11:00.000Z'});
 p.active=s.Study.choose(p.active,p.active.items[0].key.value);p=s.Study.finish(p,'2026-10-23T12:12:00.000Z');
 const item=p.history[1].items[0];
 item.mappings.push({...item.mappings[0],id:'synthetic-duplicate-mapping-only'});
 item.mappings.push({...item.mappings[0],id:'synthetic-second-topic-only',topicId:'test-second-topic',topicLabel:'SYNTHETIC TEST TOPIC',number:'99'});
 const before=JSON.stringify(p);
 const report=s.Study.performance(p.history,s.role);
 assert.equal(report.sessions,2);assert.equal(report.questions,1);assert.equal(report.attempts,2);
 assert.equal(report.correct,1);assert.equal(report.incorrect,1);assert.equal(report.rate,50);
 assert.equal(report.disciplines.length,1);assert.equal(report.disciplines[0].attempts,2);
 assert.equal(report.topics.length,2);assert.equal(report.topics.find(t=>t.id===item.mappings[0].topicId).attempts,2);
 assert.equal(report.topics.find(t=>t.id==='test-second-topic').attempts,1);
 assert.equal(JSON.stringify(p),before);
 assert.equal(s.Study.performance([...p.history,...p.history],s.role).attempts,2);
 assert.equal(s.Study.performance(p.history,'abdi-futuro').attempts,0);
});
test('performance ignores drafts, preserves historical results and never turns blanks or annulments into accuracy',()=>{
 const s=setup();let p=active(s);
 p.active=s.Study.choose(p.active,true);
 assert.equal(s.Study.performance([p.active],s.role).attempts,0);
 p=s.Study.finish(p,finishedAt);
 const history=plain(p.history);history[0].items[0].key.result='annulled';history[0].items[0].key.value=null;
 const report=s.Study.performance(history,s.role);
 assert.equal(report.annulled,1);assert.equal(report.blank,s.data.questions.length-1);assert.equal(report.rate,null);
 const before=s.Study.performance(p.history,s.role);
 s.data.questions[0].revision+=1;s.data.mappings=[];s.data.disciplines=[];s.data.topics=[];
 assert.deepEqual(plain(s.Study.performance(p.history,s.role)),plain(before));
 assert.equal(before.correct,1);assert.equal(before.rate,100);
 assert.equal(Object.hasOwn(before,'score'),false);
});
test('numbered passages and editorial comments survive backup, while damaged line numbering or missing references fail',()=>{
 const s=setup();const p={...s.Study.empty(),active:s.Study.create(s.data,s.role,s.Study.empty(),'all',{disciplineId:'lingua-portuguesa'})};
 assert.equal(p.active.items.length,16);
 const raw=s.Study.exportBackup(p), original=plain(p);
 const restored=s.Study.importBackup(raw,s.data);assert.deepEqual(plain(restored),original);
 assert.equal(restored.active.items[0].contexts[0].sourceLines.length,26);
 const comment=restored.active.items.find(i=>i.question.origin.number===13).explanations[0];
 assert.match(comment.author,/assistido por IA/);assert.ok(comment.references.length);
 for(const change of [p=>p.active.items[0].contexts[0].sourceLines[1].number=99,p=>p.active.items[0].contexts[0].sourceLines[0].text='SYNTHETIC DAMAGED LINE',p=>p.active.items.find(i=>i.explanations.length).explanations[0].references=[]]) {
  const broken=plain(original);change(broken);assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(broken),s.data));
 }
 s.data.explanations[0].text='SYNTHETIC EDITORIAL UPDATE';
 assert.deepEqual(plain(s.Study.importBackup(raw,s.data)),original);
});

test('origin/year/format intersect syllabus filters without duplicating questions',()=>{
 const s=setup(), p=s.Study.empty(), paperId='source-232funprespexe-cb1-01';
 const found=s.Study.pool(s.data,s.role,p,'all',{paperId,year:2016,type:'true_false',disciplineId:'lingua-portuguesa'});
 assert.ok(found.length);assert.ok(found.every(q=>q.origin.paperId===paperId&&q.type==='true_false'));
 assert.equal(s.Study.pool(s.data,s.role,p,'all',{paperId,year:2025}).length,0);
 const mc=s.Study.pool(s.data,s.role,p,'all',{type:'multiple_choice'});assert.equal(mc.length,5);
 assert.equal(s.Study.pool(s.data,'abdi-futuro',p,'all',{paperId}).length,0);
 for(const filters of [{paperId:'missing-source'},{year:'2016'},{year:NaN},{type:'essay'}]) assert.throws(()=>s.Study.pool(s.data,s.role,p,'all',filters));
 const session=s.Study.create(s.data,s.role,p,'all',{paperId,year:2016,type:'true_false',limit:2});
 const restored=s.Study.importBackup(s.Study.exportBackup({...p,active:session}),s.data);
 assert.equal(restored.active.selection.paperId,paperId);assert.equal(restored.active.selection.year,2016);
});
test('timed sessions use a persisted deadline, reject late answers and finalize once at the deadline',()=>{
 const s=setup();let p=s.Study.empty();
 p.active=s.Study.create(s.data,s.role,p,'all',{id:'timed-practice',now:'2026-10-23T12:00:00.000Z',durationMinutes:1,limit:3});
 assert.equal(s.Study.remaining(p.active,'2026-10-23T12:00:01.100Z'),59);
 assert.equal(s.Study.expired(p.active,'2026-10-23T12:01:00.000Z'),true);
 p.active=s.Study.choose(p.active,true,'2026-10-23T12:00:59.999Z');
 const resumed=s.Study.importBackup(s.Study.exportBackup(p),s.data);
 assert.equal(resumed.active.timer.deadlineAt,'2026-10-23T12:01:00.000Z');
 assert.throws(()=>s.Study.choose(resumed.active,false,'2026-10-23T12:01:00.000Z'),/tempo/);
 p=s.Study.finish(resumed,'2026-10-24T12:00:00.000Z');
 assert.equal(p.history[0].finishedAt,'2026-10-23T12:01:00.000Z');assert.equal(p.history[0].finishReason,'time_limit');
 assert.equal(s.Study.totals(p.history[0]).blank,2);assert.equal(s.Study.finish(p).history.length,1);
 assert.deepEqual(plain(s.Study.validate(p,s.data)),plain(p));
 const early={...s.Study.empty(),active:s.Study.create(s.data,s.role,s.Study.empty(),'all',{now:'2026-10-23T12:00:00.000Z',durationMinutes:10,limit:1})};
 const manual=s.Study.finish(early,'2026-10-23T12:01:00.000Z');
 assert.equal(manual.history[0].finishReason,'manual');assert.equal(manual.history[0].finishedAt,'2026-10-23T12:01:00.000Z');
 assert.ok(s.Study.validate(manual,s.data));
 for(const durationMinutes of [0,1.5,1441,'10',NaN]) assert.throws(()=>s.Study.create(s.data,s.role,s.Study.empty(),'all',{durationMinutes}),/tempo/);
});
test('custom scoring never changes accuracy, unscored history or official criteria',()=>{
 const s=setup();const make=mode=>s.Study.create(s.data,s.role,s.Study.empty(),'all',{limit:3,scoringMode:mode});
 const unscored=make('none');assert.equal(s.Study.score(unscored),null);
 for(const mode of ['net','right_only']) {
  let session=make(mode);session=s.Study.choose(session,session.items[0].key.value);
  session=s.Study.move(session,1);session=s.Study.choose(session,!session.items[1].key.value);
  const p=s.Study.finish({...s.Study.empty(),active:session});const finished=p.history[0];
  assert.equal(s.Study.score(finished).points,mode==='net'?0:1);assert.equal(s.Study.score(finished).maximum,3);
  assert.equal(s.Study.totals(finished).rate,50);assert.equal(Object.hasOwn(finished.scoringProfile,'minimumScore'),false);
  assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));
  finished.items[2].key.result='annulled';finished.items[2].key.value=null;assert.equal(s.Study.score(finished).points,mode==='net'?0:1);assert.equal(s.Study.score(finished).maximum,2);
 }
 const p={...s.Study.empty(),active:make('net')};p.active=s.Study.choose(p.active,!p.active.items[0].key.value);assert.equal(s.Study.score(p.active).points,-1);
 for(const change of [p=>p.active.scoringProfile.kind='official',p=>p.active.scoringProfile.incorrect=1,p=>p.active.scoringProfile.blank=1,p=>p.active.scoringProfile.minimumScore=54,p=>p.active.timer={durationSeconds:60,deadlineAt:'2026-10-23T12:00:00.000Z'},p=>p.active.selection.year='2016',p=>p.active.selection.type='essay']) {
  const broken=plain(p);change(broken);assert.throws(()=>s.Study.validate(broken,s.data));
 }
 const legacy={...s.Study.empty(),active:unscored};delete legacy.active.timer;delete legacy.active.selection;
 assert.deepEqual(plain(s.Study.validate(legacy,s.data)),plain(legacy));
 assert.equal(s.Study.finish({...s.Study.empty(),active:make('none')}).history[0].scoringProfile,null);
});
