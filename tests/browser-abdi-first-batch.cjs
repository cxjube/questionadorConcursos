'use strict';
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const wanted=new Set(JSON.parse(fs.readFileSync('data/reviews/abdi-first-batch.json','utf8')).items.map(x=>x.questionId));
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/',key='questionador-concursos.progress.v1';
const state=p=>p.evaluate(key=>JSON.parse(localStorage.getItem(key)).progress,key);
(async()=>{const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});try{
 for(const width of [320,1280]){const context=await browser.newContext({viewport:{width,height:960},ignoreHTTPSErrors:base.startsWith('https:')}),page=await context.newPage(),errors=[],seen=new Set();page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();await page.locator('#contest').selectOption('abdi-2026');await page.locator('[data-theme-choice="'+(width===320?'light':'dark')+'"]').click();
 for(const [paper,count] of [['source-alerj-2026-comunicacao-manha-tipo1',33],['source-senado-2022-administracao-tipo1',3],['source-senado-2022-policial-tipo1',3],['source-128-tcemg-008-01',2]]){
  await page.locator('#customize-study').click();await page.locator('#study-type').selectOption('multiple_choice');await page.locator('#study-paper').selectOption(paper);await page.locator('#study-quantity').fill(String(count));await page.locator('#apply-study-options').click();await page.locator('#start-study').click();await page.locator('#finish-study').waitFor();const session=(await state(page)).active;assert.equal(session.items.length,count);
  for(let i=0;i<count;i++){const item=session.items[i];assert.equal(item.question.type,'multiple_choice');assert.equal(await page.locator('input[name="answer"]').count(),6);if(wanted.has(item.question.id))seen.add(item.question.id);await page.locator('input[value="'+item.key.value+'"]').check();await page.waitForFunction(({key,n})=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===n,{key,n:i+1});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);if(i<count-1){await page.locator('#next-question').click();await page.locator('#current-question-heading').filter({hasText:'Questão '+(i+2)+' de '+count}).waitFor();}}
  await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.didactic-comment').waitFor();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await page.locator('#new-session').click();
 }
 assert.deepEqual(seen,wanted);await page.reload();await page.locator('#start-study:not([disabled])').waitFor();const saved=await state(page);assert.equal(saved.history.length,4);assert.equal(saved.active,null);assert.equal(await page.evaluate(({key})=>Study.performance(JSON.parse(localStorage.getItem(key)).progress.history,'abdi-comunicacao-marketing').correct,{key}),41);assert.deepEqual(errors,[]);await context.close();console.log('All 40 new MC, answers, comments and persisted results passed at',width);
 }
 }finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
