const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
  for(const width of [320,1280]) {
   const context=await browser.newContext({viewport:{width,height:1000}}),page=await context.newPage();
   const errors=[],external=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(base))external.push(r.url());});
   await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
   await page.locator('#customize-study').click();
   const options=await page.locator('#study-discipline option').evaluateAll(els=>els.filter(e=>e.value).map(e=>({value:e.value,disabled:e.disabled})));
   assert.equal(options.length,9);assert.equal(options.some(o=>o.disabled),false);
   await page.locator('#study-paper').selectOption('source-camara-2023-tecnica-tarde-tipo1');
   await page.locator('#apply-study-options').click();await page.locator('#start-study').click();
   for(const [index,answer] of ['c','d','a','d','e','a','b'].entries()) {
    await page.locator('input[value="'+answer+'"]').check();
    if(index===5) {
     assert.match(await page.locator('.question-context').innerText(),/1\. Maior qualificação/);
     assert.match(await page.locator('.question-context').innerText(),/3\. Favorecimento/);
     assert.match(await page.locator('.question-stem').innerText(),/Assinale a opção/);
    }
    if(index===6)assert.match(await page.locator('.source-credit').innerText(),/ROSE, Richard & MACKIE/);
    for(const theme of ['light','dark']) {
     await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);
     assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    }
    await page.evaluate(()=>document.documentElement.style.fontSize='200%');
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.evaluate(()=>document.documentElement.style.fontSize='');
    if(index<6) {await page.getByRole('button',{name:'Próxima',exact:true}).click();await page.locator('#current-question-heading').filter({hasText:'Questão '+(index+2)+' de 7'}).waitFor();}
   }
   await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.correction').waitFor();
   assert.equal(await page.evaluate(()=>JSON.parse(localStorage.getItem('questionador-concursos.progress.v1')).progress.history.at(-1).items.length),7);
   await page.evaluate(()=>document.querySelector('#study-content')?.scrollIntoView());
   const summary=await page.evaluate(()=>{const p=JSON.parse(localStorage.getItem('questionador-concursos.progress.v1')).progress;return p.history.at(-1).answers;});
   assert.equal(summary.length,10);
   // Return to first correction, inspect the separate legal comment and usable official link.
   assert.equal(await page.getByRole('button',{name:'Anterior',exact:true}).isDisabled(),true);
   assert.match(await page.locator('.didactic-comment').innerText(),/art\. 111/);
   assert.match(await page.locator('.didactic-comment a').getAttribute('href'),/^https:\/\/www2.camara.leg.br\//);
   await page.locator('#new-session').click();await page.locator('#customize-study').click();
   await page.locator('#study-discipline').selectOption('direito-administrativo-administracao-publica');
   await page.locator('#study-quantity').fill('1');await page.locator('#apply-study-options').click();await page.locator('#start-study').click();
   await page.locator('input[value="false"]').check();await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();
   await page.locator('.didactic-comment').waitFor();assert.match(await page.locator('.didactic-comment').innerText(),/art\. 55/);
   assert.match(await page.locator('.didactic-comment a').getAttribute('href'),/^https:\/\/www.planalto.gov.br\//);
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
   assert.deepEqual(errors,[]);assert.deepEqual(external,[]);await context.close();
  }
  console.log('Sixth batch passed: all nine disciplines, FGV A–E answers and source contexts, separate RICD/Planalto comment links, persisted sessions, light/dark, 320/1280px, 200% text and no external runtime requests.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
