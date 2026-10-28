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
 assert.equal(p.active.items.length,s.Study.pool(s.data,s.role,s.Study.empty()).length);
 assert.equal(new Set(p.active.items.map(i=>i.question.id)).size,s.Study.pool(s.data,s.role,s.Study.empty()).length);
 assert.equal(s.Study.pool(s.data,'abdi-futuro',p).length,0);
 const shared=p.active.items.filter(i=>i.question.origin.paperId==='source-539-alce-016-01'&&(i.question.origin.number===22||i.question.origin.number===23));
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
 assert.equal(s.Study.totals(p.history[0]).correct,1);assert.equal(s.Study.totals(p.history[0]).blank,s.Study.pool(s.data,s.role,s.Study.empty()).length-1);
 assert.equal(s.Study.totals(p.history[0]).rate,100);
 assert.deepEqual(plain(s.Study.finish(p,finishedAt)),plain(p));
 assert.deepEqual(plain(s.Study.finish({...p,active:{...p.history[0],finishedAt:null}},finishedAt)),plain(p));
});
test('zero valid responses has no artificial zero-percent score or official profile',()=>{
 const s=setup();const p=s.Study.finish(active(s),finishedAt);const result=s.Study.totals(p.history[0]);
 assert.equal(result.rate,null);assert.equal(result.blank,s.Study.pool(s.data,s.role,s.Study.empty()).length);assert.equal(p.history[0].scoringProfile,null);
});
test('new sessions never exceed the history limit accepted by restore',()=>{
 const s=setup();const progress=s.Study.empty();progress.history=Array(500).fill({});
 assert.throws(()=>s.Study.create(s.data,s.role,progress),/500 sessões/);
});
test('review errors uses latest finalized outcome and does not treat blanks as errors',()=>{
 const s=setup();let p=active(s);p.active=s.Study.choose(p.active,false);p=s.Study.finish(p,finishedAt);
 assert.equal(s.Study.pool(s.data,s.role,p,'errors').length,1);
 assert.equal(s.Study.pool(s.data,s.role,p,'blank').length,s.Study.pool(s.data,s.role,s.Study.empty()).length-1);
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
 for(const mutate of [p=>p.active.position=p.active.items.length,p=>p.active.answers=[{questionId:p.active.items[0].question.id,value:'false'}],p=>p.active.items[0].key.value=false,p=>p.history=[{...p.active,finishedAt}]]){
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
 assert.equal(await blocked.Progress.save(b,active(blocked)),false);assert.equal(b.state.active.items.length,blocked.Study.pool(blocked.data,blocked.role,blocked.Study.empty()).length);
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
 assert.equal(parent.length,8);assert.equal(child.length,7);
 assert.ok(child.every(q=>parent.some(p=>p.id===q.id)));
 assert.deepEqual(plain(s.Study.pool(s.data,s.role,progress,'all',{topicId:'comunicacao-social-7-2'}).map(q=>q.id)),['989-codevasf-010-01-q102']);
 const mapped=s.data.mappings.find(m=>m.questionId===parent[0].id);
 s.data.mappings.push({...mapped,id:'synthetic-duplicate-mapping-for-test-only'});
 assert.equal(s.Study.pool(s.data,s.role,progress,'all',{topicId:'comunicacao-social-7'}).length,8);
 assert.equal(s.Study.pool(s.data,s.role,progress,'all',{topicId:'comunicacao-social-2'}).length,12);
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
 for(const limit of [0,-1,1.5,'2',pool.length+1,NaN]) assert.throws(()=>s.Study.create(s.data,s.role,progress,'all',{...filters,limit}),/quantidade/);
 assert.throws(()=>s.Study.create(s.data,s.role,progress,'all',{topicId:'ciencia-politica-10',type:'true_false'}),/Não há questões/);
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
 assert.equal(report.annulled,1);assert.equal(report.blank,s.Study.pool(s.data,s.role,s.Study.empty()).length-1);assert.equal(report.rate,null);
 const before=s.Study.performance(p.history,s.role);
 s.data.questions[0].revision+=1;s.data.mappings=[];s.data.disciplines=[];s.data.topics=[];
 assert.deepEqual(plain(s.Study.performance(p.history,s.role)),plain(before));
 assert.equal(before.correct,1);assert.equal(before.rate,100);
 assert.equal(Object.hasOwn(before,'score'),false);
});
test('numbered passages and editorial comments survive backup, while damaged line numbering or missing references fail',()=>{
 const s=setup();const p={...s.Study.empty(),active:s.Study.create(s.data,s.role,s.Study.empty(),'all',{disciplineId:'lingua-portuguesa'})};
 assert.equal(p.active.items.length,41);
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
 const mc=s.Study.pool(s.data,s.role,p,'all',{type:'multiple_choice'});assert.equal(mc.length,21);
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

test('block filters use target syllabus blocks, preserve distinct IDs and validate snapshots',()=>{
 const s=setup(),p=s.Study.empty();
 const basic=s.Study.pool(s.data,s.role,p,'all',{block:'basic'}),specific=s.Study.pool(s.data,s.role,p,'all',{block:'specific'});
 assert.equal(basic.length,171);assert.equal(specific.length,229);
 assert.equal(s.Study.pool(s.data,s.role,p,'all',{block:'specific',disciplineId:'lingua-inglesa'}).length,0);
 const session=s.Study.create(s.data,s.role,p,'all',{block:'basic',disciplineId:'lingua-inglesa'});
 assert.equal(session.items.length,19);assert.equal(session.selection.block,'basic');
 assert.equal(session.items[0].question.language,'en');assert.equal(session.items[0].contexts[0].language,'en');
 assert.ok(session.items.every(i=>i.mappings.some(m=>m.block==='basic')));
 const restored=s.Study.importBackup(s.Study.exportBackup({...p,active:session}),s.data);assert.deepEqual(plain(restored.active),plain(session));
 for(const mutate of [p=>p.active.selection.block='specific',p=>p.active.items[0].question.language='invalid',p=>p.active.items[0].contexts[0].language='invalid']) {
  const broken=plain({...p,active:session});mutate(broken);assert.throws(()=>s.Study.validate(broken,s.data));
 }
 const legacy=s.Study.create(s.data,s.role,p,'all',{limit:1});delete legacy.selection.block;
 legacy.items.forEach(i=>i.mappings.forEach(m=>delete m.block));
 assert.ok(s.Study.validate({...p,active:legacy},s.data));
 const multi=plain(s.data),target=multi.syllabusItems.find(t=>t.block==='specific');
 multi.mappings.push({id:'synthetic-cross-block-link',questionId:basic[0].id,syllabusItemId:target.id,status:'confirmed'});
 assert.equal(s.Study.pool(multi,s.role,p,'all',{block:'specific'}).length,230);
 assert.equal(s.Study.pool(multi,s.role,p).length,399);
 assert.throws(()=>s.Study.pool(s.data,s.role,p,'all',{block:'invalid'}),/Bloco/);
});
test('evolution uses local calendar days, weighted accuracy and finalized role snapshots only',()=>{
 const s=setup();const make=(id,date,answers)=>{
  let session=s.Study.create(s.data,s.role,s.Study.empty(),'all',{id,now:date,limit:answers.length});
  answers.forEach((answer,index)=>{session=s.Study.move(session,index);if(answer!==null)session=s.Study.choose(session,answer?session.items[index].key.value:!session.items[index].key.value);});
  return s.Study.finish({...s.Study.empty(),active:session},date).history[0];
 };
 // 01:30 UTC is still the previous calendar day in São Paulo.
 const a=make('day-one','2026-10-22T01:30:00.000Z',[true]);
 const b=make('day-two','2026-10-22T15:00:00.000Z',[true,false,false]);
 const blank=make('blank-day','2026-10-23T10:00:00.000Z',[null]);
 const other={...a,id:'other-role',roleId:'abdi-futuro'},draft={...a,id:'draft',finishedAt:null};
 const history=[a,b,blank,other,draft,a];const before=JSON.stringify(history);
 const result=s.Study.evolution(history,s.role,{days:7,now:'2026-10-23T12:00:00.000Z',timeZone:'America/Sao_Paulo'});
 assert.equal(result.from,'2026-10-17');assert.equal(result.to,'2026-10-23');assert.equal(result.totals.sessions,3);
 assert.equal(result.totals.questions,3);assert.equal(result.totals.attempts,5);assert.equal(result.totals.rate,50);
 assert.deepEqual(plain(result.rows.map(r=>[r.date,r.rate])),[['2026-10-21',100],['2026-10-22',33],['2026-10-23',null]]);
 assert.equal(result.rows.length,3);assert.equal(JSON.stringify(history),before);
 s.data.mappings=[];s.data.questions=[];
 assert.equal(s.Study.evolution(history,s.role,{days:null,now:'2026-10-23T12:00:00.000Z',timeZone:'UTC'}).totals.rate,50);
});
test('evolution includes calendar window boundaries across DST and leap day without inventing zero-study days',()=>{
 const s=setup();const source=s.Study.create(s.data,s.role,s.Study.empty(),'all',{limit:1});
 const finish=(id,date)=>({...plain(source),id,startedAt:date,finishedAt:date});
 const history=[finish('outside','2026-03-02T04:59:59.999Z'),finish('boundary','2026-03-02T05:00:00.000Z'),finish('inside','2026-03-08T06:30:00.000Z'),finish('future','2026-03-09T00:00:00.000Z')];
 const report=s.Study.evolution(history,s.role,{days:7,now:'2026-03-08T12:00:00.000Z',timeZone:'America/New_York'});
 assert.equal(report.from,'2026-03-02');assert.equal(report.totals.sessions,2);assert.equal(report.rows.length,2);
 assert.equal(report.totals.rate,null);
 const leap=s.Study.evolution([finish('leap','2024-02-29T12:00:00.000Z')],s.role,{days:7,now:'2024-03-06T12:00:00.000Z',timeZone:'UTC'});
 assert.equal(leap.from,'2024-02-29');assert.equal(leap.totals.sessions,1);
 assert.equal(s.Study.evolution([],s.role,{days:30,now:'2026-10-23T12:00:00.000Z'}).totals.sessions,0);
 for(const settings of [{days:0},{days:'7'},{now:'invalid'},{timeZone:'invalid/zone'}])assert.throws(()=>s.Study.evolution([],s.role,settings));
});

test('sixth batch counts shared topics once and keeps MC separate from CE composition',()=>{
 const s=setup(),p=s.Study.empty();
 const basic=s.Study.pool(s.data,s.role,p,'all',{block:'basic'}),specific=s.Study.pool(s.data,s.role,p,'all',{block:'specific'});
 const shared='camara-2023-tecnica-tarde-tipo1-q017';
 assert.equal(basic.filter(q=>q.id===shared).length,1);assert.equal(specific.filter(q=>q.id===shared).length,1);
 assert.equal(s.Study.pool(s.data,s.role,p).filter(q=>q.id===shared).length,1);
 assert.equal(s.Study.pool(s.data,s.role,p,'all',{block:'basic',type:'true_false'}).length,169);
 assert.equal(s.Study.pool(s.data,s.role,p,'all',{block:'specific',type:'true_false'}).length,209);
 for(const discipline of s.data.disciplines.filter(d=>s.data.syllabusItems.some(i=>i.roleId===s.role && s.data.topics.find(t=>t.id===i.topicId).disciplineId===d.id))) assert.ok(s.Study.pool(s.data,s.role,p,'all',{disciplineId:discipline.id}).length>0);
});

test('legal and FGV source snapshots survive backup with narrowly allowed official URLs',()=>{
 const s=setup(),p=s.Study.empty();
 p.active=s.Study.create(s.data,s.role,p,'all',{paperId:'source-camara-2023-tecnica-tarde-tipo1'});
 assert.equal(p.active.items.length,10);assert.ok(p.active.items.every(i=>i.explanations.length===1));
 const restored=s.Study.importBackup(s.Study.exportBackup(p),s.data);assert.deepEqual(plain(restored),plain(p));
 p.active=s.Study.create(s.data,s.role,s.Study.empty(),'all',{disciplineId:'direito-administrativo-administracao-publica'});
 assert.equal(p.active.items.length,55);assert.ok(s.Study.importBackup(s.Study.exportBackup(p),s.data));
 const bad=plain(p);bad.active.items[0].explanations[0].references[0].officialUrl='https://www.planalto.gov.br.evil.invalid/fake';
 // Snapshot references carry the canonical source URL; reject a lookalike hostname.
 const ref=p.active.items[0].explanations[0].references[0];
 assert.ok(Object.hasOwn(ref,'officialUrl'));
 assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(bad),s.data));
 p.active=s.Study.create(s.data,s.role,s.Study.empty(),'all',{paperId:'source-094-pf-cb1-01'});
 assert.ok(s.Study.importBackup(s.Study.exportBackup(p),s.data));
 const spoof=plain(p),learn=spoof.active.items.flatMap(i=>i.explanations.flatMap(e=>e.references)).find(r=>r.officialUrl.startsWith('https://learn.microsoft.com/'));
 assert.ok(learn);learn.officialUrl=learn.officialUrl.replace('learn.microsoft.com','learn.microsoft.com.evil.invalid');
 assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(spoof),s.data));
});

test('the expanded CE reserve provides 169 basic and 209 specific distinct valid items',()=>{
 const s=setup(),p=s.Study.empty();
 const basic=s.Study.pool(s.data,s.role,p,'all',{block:'basic',type:'true_false'});
 const specific=s.Study.pool(s.data,s.role,p,'all',{block:'specific',type:'true_false'});
 assert.equal(basic.length,169);assert.equal(specific.length,209);
 assert.equal(new Set([...basic,...specific].map(q=>q.id)).size,378);
 for(const block of ['basic','specific']) {
  const session=s.Study.create(s.data,s.role,p,'all',{block,type:'true_false',limit:90});
  assert.equal(session.items.length,90);
  assert.ok(session.items.every(i=>i.question.type==='true_false'&&i.key.result==='valid'&&i.mappings.some(m=>m.block===block)));
  assert.equal(session.scoringProfile,null);
  assert.ok(s.Study.importBackup(s.Study.exportBackup({...p,active:session}),s.data));
 }
});

test('the complete democracy command uses a new question revision and preserves old drafts and history',()=>{
 const s=setup(),legacy=plain(s.data);
 const repair=JSON.parse(fs.readFileSync(path.join(root,'data/reviews/tenth-batch.json'),'utf8')).contextCorrections[0];
 const ctx=legacy.contexts.find(c=>c.id===repair.contextId);ctx.revision=repair.previousRevision;ctx.text=repair.previousText;
 legacy.questions=legacy.questions.filter(q=>q.id==='camara-2014-area-xix-q136');legacy.questions[0].revision=1;
 let p={...s.Study.empty(),active:s.Study.create(legacy,s.role,s.Study.empty(),'all',{id:'legacy-democracy',now:'2026-10-23T12:00:00.000Z'})};
 p.active=s.Study.choose(p.active,false);
 const raw=s.Study.exportBackup(p),before=plain(p);
 const restored=s.Study.importBackup(raw,s.data);
 assert.deepEqual(plain(restored),before);assert.equal(s.Study.matches(s.data,restored.active),false);
 p=s.Study.finish(restored,finishedAt);
 assert.equal(s.Study.totals(p.history[0]).correct,1);
 assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));
 const fresh=s.Study.snapshot(s.data,s.data.questions.find(q=>q.id==='camara-2014-area-xix-q136'),s.role);
 assert.equal(fresh.question.revision,2);assert.equal(fresh.contexts[0].revision,2);
 assert.match(fresh.contexts[0].text,/^Considerando dois grandes modelos/);
 assert.equal(before.active.items[0].contexts[0].text,repair.previousText);
});

test('content audit preserves older context and taxonomy snapshots without weakening current checks',()=>{
 const s=setup(),legacy=plain(s.data);
 const audit=JSON.parse(fs.readFileSync(path.join(root,'data/reviews/content-audit-2026-10-26.json'),'utf8'));
 for(const [section,changes] of [['mappings',audit.mappingCorrections],['contexts',audit.contextCorrections],['questions',audit.questionRevisions]])
  for(const change of changes) legacy[section][legacy[section].findIndex(row=>row.id===change.after.id)]=change.before;
 legacy.revision='e'.repeat(64);
 legacy.questions=legacy.questions.filter(q=>['camara-2014-cb2-03-q096','camara-2014-area-xix-q145'].includes(q.id));
 let progress={...s.Study.empty(),active:s.Study.create(legacy,s.role,s.Study.empty(),'all',{id:'before-content-audit'})};
 const before=plain(progress);
 assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(progress),s.data)),before);
 const oldContext=progress.active.items.find(i=>i.question.id==='camara-2014-cb2-03-q096').contexts.find(c=>c.id==='camara-2014-ethics-cf-command');
 assert.match(oldContext.text,/\. 94$/);assert.equal(oldContext.revision,1);
 assert.ok(progress.active.items.find(i=>i.question.id==='camara-2014-area-xix-q145').mappings.some(m=>m.topicId==='ciencia-politica-13'));
 progress=s.Study.finish(progress);
 assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(progress),s.data)),plain(progress));
 const fresh=s.Study.snapshot(s.data,s.data.questions.find(q=>q.id==='camara-2014-cb2-03-q096'),s.role);
 assert.equal(fresh.question.revision,2);assert.equal(fresh.contexts.find(c=>c.id===oldContext.id).revision,2);
 const current={...s.Study.empty(),active:s.Study.create(s.data,s.role,s.Study.empty(),'all',{paperId:'source-camara-2014-consultor-cb2-03'})};
 current.active.items.find(i=>i.question.id===fresh.question.id).contexts.find(c=>c.id===oldContext.id).text+=' 94';
 assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(current),s.data));
});

test('Regimento Comum MC snapshots preserve official normative references and reject a lookalike host',()=>{
 const s=setup(),p={...s.Study.empty(),active:s.Study.create(s.data,s.role,s.Study.empty(),'all',{topicId:'processo-legislativo-regimento-6',type:'multiple_choice'})};
 assert.equal(p.active.items.length,3);assert.ok(p.active.items.every(i=>i.question.type==='multiple_choice'));
 assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));
 const bad=plain(p),ref=bad.active.items.flatMap(i=>i.explanations.flatMap(e=>e.references)).find(r=>r.officialUrl.startsWith('https://www25.senado.leg.br/'));
 assert.ok(ref);ref.officialUrl=ref.officialUrl.replace('www25.senado.leg.br','www25.senado.leg.br.evil.invalid');
 assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(bad),s.data));
});

test('government and STF references round-trip while lookalike domains are rejected',()=>{
 const s=setup();
 for(const [paper,host] of [['source-038-anm-024-01','www.gov.br'],['source-038-anm-005-01','portal.stf.jus.br'],['source-alerj-2026-comunicacao-manha-tipo1','bd.camara.leg.br']]) {
  const p={...s.Study.empty(),active:s.Study.create(s.data,s.role,s.Study.empty(),'all',{paperId:paper})};
  assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));
  const broken=plain(p),ref=broken.active.items.flatMap(i=>i.explanations.flatMap(e=>e.references)).find(r=>new URL(r.officialUrl).hostname===host);
  assert.ok(ref);ref.officialUrl=ref.officialUrl.replace(host,host+'.evil.invalid');
  assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(broken),s.data));
 }
});
