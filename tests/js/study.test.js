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
 assert.equal(p.active.items.length,20);
 assert.equal(new Set(p.active.items.map(i=>i.question.id)).size,20);
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
 assert.equal(s.Study.totals(p.history[0]).correct,1);assert.equal(s.Study.totals(p.history[0]).blank,19);
 assert.equal(s.Study.totals(p.history[0]).rate,100);
 assert.deepEqual(plain(s.Study.finish(p,finishedAt)),plain(p));
 assert.deepEqual(plain(s.Study.finish({...p,active:{...p.history[0],finishedAt:null}},finishedAt)),plain(p));
});
test('zero valid responses has no artificial zero-percent score or official profile',()=>{
 const s=setup();const p=s.Study.finish(active(s),finishedAt);const result=s.Study.totals(p.history[0]);
 assert.equal(result.rate,null);assert.equal(result.blank,20);assert.equal(p.history[0].scoringProfile,null);
});
test('new sessions never exceed the history limit accepted by restore',()=>{
 const s=setup();const progress=s.Study.empty();progress.history=Array(500).fill({});
 assert.throws(()=>s.Study.create(s.data,s.role,progress),/500 sessões/);
});
test('review errors uses latest finalized outcome and does not treat blanks as errors',()=>{
 const s=setup();let p=active(s);p.active=s.Study.choose(p.active,false);p=s.Study.finish(p,finishedAt);
 assert.equal(s.Study.pool(s.data,s.role,p,'errors').length,1);
 assert.equal(s.Study.pool(s.data,s.role,p,'blank').length,19);
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
 assert.equal(await blocked.Progress.save(b,active(blocked)),false);assert.equal(b.state.active.items.length,20);
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
