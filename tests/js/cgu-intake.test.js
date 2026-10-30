'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),{webcrypto}=require('node:crypto');
const root=path.resolve(__dirname,'../..'),role='cgu-auditoria',start='2026-10-28T12:00:00.000Z';
const plain=x=>JSON.parse(JSON.stringify(x));
function setup(){const s={window:{},URL,TextEncoder,crypto:webcrypto};vm.createContext(s);for(const f of ['assets/js/study.js','assets/js/catalog.js','data/catalog.js'])vm.runInContext(fs.readFileSync(path.join(root,'docs',f),'utf8'),s);s.data=s.window.CONCURSOS_CATALOG;return s;}
test('confirmed Auditoria offers original shared training while native 170 CE uses distinct reviewed questions',()=>{
 const s=setup(),d=s.data,p=s.Study.empty(),all=s.Study.pool(d,role,p),r=JSON.parse(fs.readFileSync(path.join(root,'data/reviews/cgu-bank-readiness.json')));
 assert.equal(s.Catalog.rolesFor(d,'cgu-2026')[0].id,role);assert.equal(s.Catalog.noticesFor(d,'cgu-2026',role).length,2);assert.equal(s.Catalog.syllabusFor(d,role).length,266);assert.equal(all.length,376);assert.equal(new Set(all.map(q=>q.id)).size,376);assert.equal(all.filter(q=>q.type==='true_false').length,280);assert.equal(all.filter(q=>q.type==='multiple_choice').length,96);
 const a=s.Study.examAvailability(d,role);assert.equal(a.ready,r.ready);assert.equal(a.distinct,r.distinctCE);assert.equal(a.missing.reduce((n,b)=>n+b.count,0),r.minimumAdditionalCE);assert.deepEqual(plain(a.blocks.map(b=>b.questions.length)),r.blocks.map(b=>b.availableCE));assert.deepEqual(plain(a.missing.map(m=>[m.blockId,m.count])),r.blocks.filter(b=>b.missingForThisAllocation).map(b=>[b.blockId,b.missingForThisAllocation]));const session=s.Study.create(d,role,p,'exam',{now:start});assert.equal(session.items.length,170);assert.equal(new Set(session.items.map(i=>i.question.id)).size,170);
 for(const block of ['basic','complementary','specific'])assert.equal(s.Study.pool(d,role,p,'all',{block,type:'true_false'}).length,r.blocks.find(b=>b.blockId===block).availableCE);
 assert.throws(()=>s.Study.pool(d,role,p,'all',{topicId:'abdi-2026-abdi-licitacoes-convenios-1'}));assert.equal(s.Study.examAvailability(d,'camara-comunicacao-divulgacao').ready,true);assert.equal(s.Study.examAvailability(d,'abdi-comunicacao-marketing').ready,true);
});
test('CGU study, corrections and backups preserve original provenance and independent role history',()=>{
 const s=setup(),d=s.data;let p={...s.Study.empty(),active:s.Study.create(d,role,s.Study.empty(),'all',{now:start,block:'complementary',type:'true_false',limit:3})};const before=plain(p.active);
 assert.equal(before.scoringProfile,null);assert.equal(before.selection.block,'complementary');assert.ok(before.items.every(i=>i.mappings.every(m=>m.roleId===role)));assert.ok(before.items.every(i=>i.paper.provider==='Cebraspe'));
 p.active=s.Study.choose(p.active,p.active.items[0].key.value,'2026-10-28T12:01:00.000Z');p.active=s.Study.move(p.active,1);p.active=s.Study.choose(p.active,!p.active.items[1].key.value,'2026-10-28T12:02:00.000Z');p=s.Study.importBackup(s.Study.exportBackup(p),d);p=s.Study.finish(p,'2026-10-28T12:03:00.000Z');const totals=s.Study.totals(p.history[0]);assert.deepEqual(plain([totals.correct,totals.incorrect,totals.blank]),[1,1,1]);assert.equal(s.Study.score(p.history[0]),null);assert.equal(s.Study.performance(p.history,role).attempts,3);assert.equal(s.Study.performance(p.history,'camara-comunicacao-divulgacao').attempts,0);assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),d)),plain(p));
 const old=JSON.parse(require('node:zlib').gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-cgu-intake-catalog.json.gz'))));old.revision='d'.repeat(64);
 for(const other of ['camara-comunicacao-divulgacao','abdi-comunicacao-marketing']){const prior={...s.Study.empty(),active:s.Study.create(old,other,s.Study.empty(),'all',{now:start,limit:2})};assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(prior),d)),plain(prior));}
});

test('CGU consolidated normative references round-trip with exact official host and preserve pre-lot sessions',()=>{
 const s=setup(),d=s.data;const session=s.Study.create(d,role,s.Study.empty(),'all',{paperId:'source-993-tce-ac-016-01',now:start});const p={...s.Study.empty(),active:session};
 const refs=session.items.flatMap(i=>i.explanations.flatMap(e=>e.references));assert.ok(refs.some(r=>r.documentId==='reference-cgu-in3-2017-consolidada'));assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(p),d)),plain(p));
 for(const url of ['https://basedeconhecimento.cgu.gov.br.evil.example/download','https://user:password@basedeconhecimento.cgu.gov.br/download']){const bad=plain(p);bad.active.items.flatMap(i=>i.explanations.flatMap(e=>e.references)).find(r=>r.documentId==='reference-cgu-in3-2017-consolidada').officialUrl=url;assert.throws(()=>s.Study.importBackup(s.Study.exportBackup(bad),d));}
 const old=JSON.parse(require('node:zlib').gunzipSync(fs.readFileSync(path.join(root,'data/reviews/pre-cgu-first-batch-catalog.json.gz'))));old.revision='f'.repeat(64);assert.equal(s.Study.examAvailability(old,role).ready,false);
 for(const other of [role,'camara-comunicacao-divulgacao','abdi-comunicacao-marketing']){let previous={...s.Study.empty(),active:s.Study.create(old,other,s.Study.empty(),'all',{now:start,limit:2})};previous.active=s.Study.choose(previous.active,previous.active.items[0].key.value,'2026-10-28T12:01:00.000Z');assert.deepEqual(plain(s.Study.importBackup(s.Study.exportBackup(previous),d)),plain(previous));}
});
