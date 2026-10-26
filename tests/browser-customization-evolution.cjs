const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const base=process.env.APP_BASE_URL || 'http://127.0.0.1:8000/';
const key='questionador-concursos.progress.v1';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
  for(const width of [320,1280]) {
   const context=await browser.newContext({viewport:{width,height:1000},timezoneId:'America/Sao_Paulo'});
   const page=await context.newPage();
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.clock.install({time:new Date('2026-10-23T12:00:00.000Z')});
   await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
   const customize=page.locator('#customize-study'),start=page.locator('#start-study');
   assert.equal(await customize.innerText(),'Personalizar treino');
   assert.equal(await customize.evaluate(el=>Boolean(el.compareDocumentPosition(document.querySelector('#start-study')) & Node.DOCUMENT_POSITION_FOLLOWING)),true);
   if(width===1280) {const a=await customize.boundingBox(),b=await start.boundingBox();assert.ok(a.x+a.width<=b.x);assert.equal(a.y,b.y);}
   for(const theme of ['light','dark']) {
    await page.locator('[data-theme-choice="'+theme+'"]').click();
    await page.screenshot({path:'/tmp/selection-buttons-'+width+'-'+theme+'.png',fullPage:true});
   }
   await customize.focus();await page.keyboard.press('Enter');
   assert.equal(await page.locator('#study-options').evaluate(el=>el.matches(':modal')),true);
   assert.equal(await page.locator('#study-block').evaluate(el=>el===document.activeElement),true);
   await page.locator('#study-block').selectOption('basic');
   assert.match(await page.locator('#study-filter-status').innerText(),/107 de 107/);
   await page.locator('#study-discipline').selectOption('lingua-inglesa');
   await page.locator('#study-quantity').fill('1');await page.locator('#apply-study-options').click();
   assert.equal(await customize.evaluate(el=>el===document.activeElement),true);
   assert.match(await page.locator('#study-selection-summary').innerText(),/1 questão/);
   assert.equal(await page.evaluate(key=>localStorage.getItem(key),key),null);
   await customize.click();await page.locator('#study-block').selectOption('specific');
   await page.locator('#study-discipline').selectOption('comunicacao-social');await page.locator('#study-topic').selectOption('comunicacao-social-2');
   await page.locator('#study-quantity').fill('3');await page.keyboard.press('Escape');
   assert.equal(await page.locator('#study-block').inputValue(),'basic');
   assert.equal(await page.locator('#study-discipline').inputValue(),'lingua-inglesa');
   assert.equal(await page.locator('#study-quantity').inputValue(),'1');assert.equal(await start.isEnabled(),true);
   await customize.click();await page.locator('#study-quantity').fill('999');
   assert.equal(await page.locator('#apply-study-options').isDisabled(),true);
   await page.locator('#study-options [data-close-dialog]').click();assert.equal(await page.locator('#study-quantity').inputValue(),'1');
   await customize.click();
   for(const theme of ['light','dark']) {
    await page.evaluate(theme=>document.documentElement.dataset.theme=theme,theme);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    assert.equal(await page.locator('#study-options-title').evaluate(el=>{const d=el.closest('dialog').getBoundingClientRect(),r=el.getBoundingClientRect();return r.top>=d.top && r.bottom<=d.bottom;}),true);
    await page.screenshot({path:'/tmp/customization-dialog-'+width+'-'+theme+'.png',fullPage:true});
   }
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');
   assert.equal(await page.locator('#study-options').evaluate(el=>el.scrollWidth<=el.clientWidth),true);
   await page.evaluate(()=>document.documentElement.style.fontSize='');await page.locator('#apply-study-options').click();
   await start.click();await page.locator('#finish-study').waitFor();
   assert.equal(await page.locator('.question-context').getAttribute('lang'),'en');
   assert.equal(await page.locator('.question-stem').getAttribute('lang'),'en');
   assert.match(await page.locator('.source-credit').innerText(),/thequantuminsider/);
   assert.equal(await page.locator('.correction').count(),0);
   await page.locator('input[value="false"]').check();
   await page.waitForFunction(key=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===1,key);
   await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.correction').waitFor();
   assert.match(await page.locator('.didactic-comment').innerText(),/assistido por IA/);
   await page.locator('#new-session').click();await customize.click();assert.equal(await page.locator('#study-block').inputValue(),'');
   await page.locator('#study-options [data-close-dialog]').click();
   // Another tab creating a session closes an open customization without applying it.
   await customize.click();await page.locator('#study-quantity').fill('3');
   const tab=await page.context().newPage();await tab.goto(base);await tab.locator('#start-study:not([disabled])').click();await tab.locator('#finish-study').waitFor();
   await page.locator('#progress-warning').waitFor();
   assert.equal(await page.locator('#study-options').isVisible(),false);
   assert.equal(await page.locator('#study-quantity').inputValue(),'');
   assert.equal(await customize.isDisabled(),true);await tab.close();
   // Controlled attempts from real snapshots, restricted to this isolated browser context.
   await page.evaluate(key=>{
    const data=window.CONCURSOS_CATALOG,role=data.roles[0].id,p=Study.empty();
    for(const [id,date,right] of [['old','2026-09-01T12:00:00.000Z',true],['recent','2026-10-20T12:00:00.000Z',true],['today','2026-10-23T11:00:00.000Z',false]]) {
     let session=Study.create(data,role,Study.empty(),'all',{id,now:date,limit:1});
     session=Study.choose(session,right?session.items[0].key.value:!session.items[0].key.value);
     p.history.push(Study.finish({...Study.empty(),active:session},date).history[0]);
    }
    localStorage.setItem(key,JSON.stringify({version:1,token:crypto.randomUUID(),progress:p}));
   },key);
   await page.reload();await page.locator('#landing-history').click();
   await page.locator('.evolution-details > summary').click();
   assert.match(await page.locator('#evolution-summary').innerText(),/2 sessões finalizadas · 1 questão distinta · 2 tentativas · 50%/);
   assert.equal(await page.locator('.evolution-days li').count(),2);
   await page.locator('#evolution-period').selectOption('all');
   assert.match(await page.locator('#evolution-summary').innerText(),/3 sessões finalizadas · 1 questão distinta · 3 tentativas · 67%/);
   assert.equal(await page.locator('.evolution-days li').count(),3);
   assert.equal(await page.locator('.evolution-days meter').count(),3);
   for(const theme of ['light','dark']) {
    await page.locator('[data-theme-choice="'+theme+'"]').click();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.screenshot({path:'/tmp/evolution-'+width+'-'+theme+'.png',fullPage:true});
   }
   await page.locator('#study-objective').click();await page.locator('#contest').selectOption('abdi-futuro');await page.locator('#landing-history').click();
   if(!await page.locator('#evolution-period').isVisible())await page.locator('.evolution-details > summary').click();
   assert.match(await page.locator('#evolution-summary').innerText(),/Nenhuma sessão finalizada/);assert.equal(await page.locator('.evolution-days li').count(),0);
   assert.deepEqual(errors,[]);await context.close();
  }
 } finally {await browser.close();}
 console.log('Customization and evolution passed: button order, keyboard/focus, modal apply/cancel/Escape, validation, P1/P2, new source English language/context/comment, immutable history, weighted calendar-day evolution, period switch and role separation at 320/1280px in light/dark and 200% text.');
})().catch(error=>{console.error(error);process.exit(1);});
