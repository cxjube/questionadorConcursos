'use strict';
const{test}=require('node:test');
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const{webcrypto}=require('node:crypto');const root=path.resolve(__dirname,'../..'),role='abdi-comunicacao-marketing';
const plain=x=>JSON.parse(JSON.stringify(x)),start='2026-10-27T15:00:00.000Z',end='2026-10-27T16:00:00.000Z';
function setup(){const c={window:{},crypto:webcrypto,URL,TextEncoder};vm.createContext(c);for(const f of ['assets/js/study.js','data/catalog.js'])vm.runInContext(fs.readFileSync(path.join(root,'docs',f),'utf8'),c);return{...c,data:c.window.CONCURSOS_CATALOG};}

test('all forty official MC preserve five alternatives, independent keys and explanations through practice and backup',()=>{
 const s=setup(),manifest=JSON.parse(fs.readFileSync(path.join(root,'data/reviews/abdi-first-batch.json'))),wanted=new Set(manifest.items.map(r=>r.questionId)),seen=new Set();
 const cases=[['source-alerj-2026-comunicacao-manha-tipo1',33],['source-senado-2022-administracao-tipo1',3],['source-senado-2022-policial-tipo1',3],['source-128-tcemg-008-01',4]];
 for(const [paperId,count] of cases){
  const session=s.Study.create(s.data,role,s.Study.empty(),'all',{paperId,now:start});assert.equal(session.items.length,count);assert.equal(session.scoringProfile,null);
  for(const i of session.items){assert.equal(i.question.type,'multiple_choice');assert.equal(i.question.options.length,5);assert.equal(i.key.stage,'definitive');assert.ok(i.mappings.every(m=>m.roleId===role));assert.equal(i.explanations.length,1);if(wanted.has(i.question.id))seen.add(i.question.id);session.answers.push({questionId:i.question.id,value:i.key.value});}
  const finished=s.Study.finish({...s.Study.empty(),active:session},end);assert.equal(s.Study.totals(finished.history[0]).correct,count);
  assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(finished),s.data)),plain(finished));
 }
 assert.deepEqual([...seen].sort(),[...wanted].sort());
 const progress=s.Study.empty();assert.equal(s.Study.pool(s.data,role,progress).length,201);assert.equal(s.Study.pool(s.data,role,progress,'all',{type:'multiple_choice'}).length,55);
 assert.equal(s.Study.pool(s.data,role,progress,'all',{block:'institutional'}).length,7);assert.equal(s.Study.pool(s.data,'camara-comunicacao-divulgacao',progress).length,395);
 assert.equal(s.Study.examAvailability(s.data,role).ready,false);
});

test('the 145-item ABDI history remains unchanged and the newly released items become unanswered',()=>{
 const s=setup(),old=JSON.parse(require('node:zlib').gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-abdi-first-batch-catalog.json.gz'))).toString());old.revision='a'.repeat(64);
 const session=s.Study.create(old,role,s.Study.empty(),'all',{now:start});assert.equal(session.items.length,145);
 session.answers=session.items.map(i=>({questionId:i.question.id,value:i.key.value}));let p=s.Study.finish({...s.Study.empty(),active:session},end);
 assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),s.data)),plain(p));assert.equal(s.Study.matches(s.data,p.history[0]),true);
 const newIds=new Set(['abdi-first-batch','abdi-second-batch'].flatMap(name=>JSON.parse(fs.readFileSync(path.join(root,'data/reviews/'+name+'.json'))).items.map(i=>i.questionId)));
 assert.deepEqual(new Set(s.Study.pool(s.data,role,p,'unanswered').map(q=>q.id)),newIds);
 assert.equal(s.Study.performance(p.history,role).attempts,145);assert.equal(s.Study.performance(p.history,'camara-comunicacao-divulgacao').attempts,0);
});
