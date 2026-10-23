const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/';
const progressKey='questionador-concursos.progress.v1';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
  for(const width of [320,1280]) {
   const context=await browser.newContext({viewport:{width,height:1000}}),page=await context.newPage();
   const errors=[],external=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(base))external.push(r.url());});
   await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
   await page.locator('#customize-study').click();
   await page.locator('#study-discipline').selectOption('ciencia-politica');await page.locator('#study-type').selectOption('true_false');
   assert.match(await page.locator('#study-filter-status').innerText(),/8 de 8/);
   await page.locator('#apply-study-options').click();await page.locator('#start-study').click();
   for(const [i,value] of [true,true,false,true,true,true,true,true].entries()) {
    await page.locator('input[value="'+value+'"]').check();
    await page.waitForFunction(({key,count})=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===count,{key:progressKey,count:i+1});
    assert.equal(await page.locator('.correction').count(),0);
    for(const theme of ['light','dark']) {
     await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);
     await page.evaluate(()=>document.documentElement.style.fontSize='200%');
     assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
     await page.evaluate(()=>document.documentElement.style.fontSize='');
    }
    if(i<7){await page.locator('#next-question').click();await page.locator('#current-question-heading').filter({hasText:'Questão '+(i+2)+' de 8'}).waitFor();}
   }
   await page.reload();await page.locator('#start-study').click();
   await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.correction').waitFor();
   assert.match(await page.locator('.didactic-comment').innerText(),/Weber/);
   const stored=await page.evaluate(key=>{const p=JSON.parse(localStorage.getItem(key)).progress;const h=p.history.at(-1);return {right:h.answers.filter(a=>h.items.find(i=>i.question.id===a.questionId).key.value===a.value).length,comments:h.items.filter(i=>i.explanations.length).length};},progressKey);
   assert.deepEqual(stored,{right:8,comments:8});
   await page.locator('#new-session').click();await page.locator('#customize-study').click();
   await page.locator('#study-paper').selectOption('source-camara-2014-consultor-cb2-03');
   await page.locator('#study-discipline').selectOption('direito-constitucional-regimento');
   await page.locator('#study-quantity').fill('1');await page.locator('#apply-study-options').click();await page.locator('#start-study').click();
   assert.match(await page.locator('.question-stem').innerText(),/procuração/);
   await page.locator('input[value="true"]').check();await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();
   await page.locator('.didactic-comment').waitFor();assert.match(await page.locator('.didactic-comment').innerText(),/videoconferência/);
   await page.locator('#new-session').click();await page.locator('#customize-study').click();
   await page.locator('#study-paper').selectOption('source-038-anm-cg1-01');
   await page.locator('#study-discipline').selectOption('tecnologia-informacao-dados');
   await page.locator('#study-topic').selectOption('tecnologia-informacao-dados-4-3');
   await page.locator('#apply-study-options').click();await page.locator('#start-study').click();await page.locator('input[value="false"]').check();
   await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.didactic-comment').waitFor();
   assert.match(await page.locator('.didactic-comment').innerText(),/phishing/);
   assert.match(await page.locator('.didactic-comment a').getAttribute('href'),/^https:\/\/cartilha.cert.br\//);
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
   assert.deepEqual(errors,[]);assert.deepEqual(external,[]);await context.close();
  }
  console.log('Seventh batch passed: C/E science filter, eight official answers and comments, reload, dated RICD explanation, CERT.br reference, light/dark, 200% text, 320/1280px and no external runtime requests.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
