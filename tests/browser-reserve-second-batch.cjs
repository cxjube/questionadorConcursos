'use strict';
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/',key='questionador-concursos.progress.v1',manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/reviews/reserve-second-batch.json'))),wanted=new Set(manifest.items.map(i=>i.questionId));
const cases=[['cgu-2026','source-896-tcdf-002-01'],['cgu-2026','source-896-tcdf-ce1-01'],['cgu-2026','source-993-tce-ac-014-01'],['cgu-2026','source-993-tce-ac-016-01'],['cgu-2026','source-057-ibama-001-01'],['abdi-2026','source-896-tcdf-cb1-01'],['abdi-2026','source-abdi-2008-projetos-biotecnologia'],['camara-2026','source-128-tcemg-008-01']];
const state=p=>p.evaluate(k=>JSON.parse(localStorage.getItem(k)).progress,key);
async function reflow(p){for(const size of ['', '200%']){await p.evaluate(s=>document.documentElement.style.fontSize=s,size);assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);}await p.evaluate(()=>document.documentElement.style.fontSize='');}
(async()=>{const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});try{for(const width of [320,1280]){
 const context=await browser.newContext({viewport:{width,height:1000},ignoreHTTPSErrors:base.startsWith('https:')}),p=await context.newPage(),seen=new Set(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(base);await p.locator('#start-study:not([disabled])').waitFor();await p.locator('[data-theme-choice="'+(width===320?'light':'dark')+'"]').click();
 for(const [contest,paper] of cases){
  await p.locator('#contest').selectOption(contest);await p.locator('#customize-study').click();await p.locator('#study-paper').selectOption(paper);await p.locator('#apply-study-options').click();await p.locator('#start-study').click();await p.locator('#finish-study').waitFor();const session=(await state(p)).active,selected=session.items.map((item,index)=>({item,index})).filter(({item})=>wanted.has(item.question.id));assert.ok(selected.length>0);
  let marked=0;
  for(const {item,index} of selected){
   const active=(await state(p)).active;if(active.position!==index){if(active.position===active.items.length-1)await p.locator('#next-question').click();else await p.locator('#review-study').click();await p.getByRole('button',{name:new RegExp('^Questão '+(index+1)+' —')}).click();}
   await p.locator('#current-question-heading').filter({hasText:'Questão '+(index+1)+' de '+session.items.length}).waitFor();assert.equal(await p.locator('.question-stem').textContent(),item.question.stem);assert.equal(await p.locator('input[name="answer"]').count(),item.question.type==='true_false'?3:item.question.options.length+1);seen.add(item.question.id);
   if(item.question.id==='896-tcdf-002-01-q143')for(const text of ['R$ 200 mil','R$ 150 mil','R$ 20 mil'])assert.match(await p.locator('#study-content').innerText(),new RegExp(text.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')));
   if(item.question.id==='896-tcdf-cb1-01-q032'){assert.match(await p.locator('.question-context').innerText(),/conjunção ∧/);assert.match(await p.locator('.question-context').innerText(),/bicondicional ⇔/);}
   await p.locator('input[value="'+item.key.value+'"]').check();marked++;await p.waitForFunction(({key,n})=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===n,{key,n:marked});if(index===selected[0].index)await reflow(p);
  }
  await p.locator('#finish-study').click();await p.locator('#confirm-finish').click();await p.locator('.correction').waitFor();const progress=await state(p),saved=progress.history.at(-1);assert.equal(saved.answers.length,selected.length);const restored=await p.evaluate(k=>{const progress=JSON.parse(localStorage.getItem(k)).progress;return Study.importBackup(Study.exportBackup(progress),window.CONCURSOS_CATALOG);},key);assert.equal(restored.history.length,progress.history.length);await reflow(p);await p.locator('#new-session').click();assert.equal((await state(p)).active,null);
 }
 assert.deepEqual([...seen].sort(),[...wanted].sort());assert.deepEqual(errors,[]);await context.close();console.log('All 48 reviewed additions and source contexts passed at',width);
 }}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
