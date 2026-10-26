const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.APP_BASE_URL || 'http://127.0.0.1:8000/';
const key = 'questionador-concursos.progress.v1';
const progress = page => page.evaluate(key=>JSON.parse(localStorage.getItem(key)).progress,key);
(async () => {
 const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
  for (const width of [320,1280]) {
   const page = await browser.newPage({viewport:{width,height:1050}});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
   await page.locator('#customize-study').click();
   await page.locator('#study-discipline').selectOption('comunicacao-social');
   await page.locator('#study-topic').selectOption('comunicacao-social-2');
   await page.locator('#study-quantity').fill('2');await page.locator('#study-shuffle').check();await page.locator('#apply-study-options').click();
   await page.locator('#start-study').click();await page.locator('#finish-study').waitFor();
   for (const theme of ['light','dark']) {
    await page.locator('[data-theme-choice="'+theme+'"]').click();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.locator('.question-controls').screenshot({path:'/tmp/questionador-controls-'+width+'-'+theme+'.png'});
   }
   const first = (await progress(page)).active;
   const keyValue = first.items[0].key.value;
   await page.locator('input[value="'+String(!keyValue)+'"]').check();
   await page.waitForFunction(key=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===1,key);
   await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();
   await page.locator('.correction').waitFor();
   const finished = await progress(page);
   assert.equal(finished.active,null);assert.equal(finished.history.length,1);
   assert.equal(await page.locator('#review-errors').innerText(),'Revisar erros (1)');
   assert.equal(await page.locator('.result-next-steps').evaluate(el=>Boolean(el.compareDocumentPosition(document.querySelector('.question-heading')) & Node.DOCUMENT_POSITION_FOLLOWING)),true);
   for (const theme of ['light','dark']) {
    await page.locator('[data-theme-choice="'+theme+'"]').click();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.screenshot({path:'/tmp/questionador-results-'+width+'-'+theme+'.png',fullPage:true});
   }
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
   await page.evaluate(()=>document.documentElement.style.fontSize='');
   const stored = await page.evaluate(key=>localStorage.getItem(key),key);
   await page.locator('#new-session').click();
   assert.equal(await page.locator('#study-landing').isVisible(),true);
   assert.equal(await page.locator('#study-workspace').isHidden(),true);
   assert.equal(await page.locator('#start-study').innerText(),'Iniciar questões');
   assert.equal(await page.locator('#contest').evaluate(el=>el===document.activeElement),true);
   assert.equal(await page.locator('#study-options').getAttribute('open'),null);
   assert.equal(await page.locator('#study-discipline').inputValue(),'');
   assert.equal(await page.locator('#study-topic').inputValue(),'');
   assert.equal(await page.locator('#study-quantity').inputValue(),'');
   assert.equal(await page.locator('#study-shuffle').isChecked(),false);
   assert.equal(await page.evaluate(key=>localStorage.getItem(key),key),stored);
   await page.reload();await page.locator('#start-study:not([disabled])').waitFor();
   assert.deepEqual(await progress(page),finished);
   // Only the explicit start creates a session. The previous result is preserved.
   await page.locator('#start-study').click();await page.locator('#finish-study').waitFor();
   const second = await progress(page);
   assert.equal(second.history.length,1);assert.notEqual(second.active.id,first.id);
   assert.equal(second.active.answers.length,0);assert.equal(second.active.items.length,254);
   // Viewing a past result during a new session must not discard the active draft.
   await page.locator('input[value="true"]').check();
   await page.waitForFunction(key=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===1,key);
   await page.locator('#study-history').click();await page.getByRole('button',{name:'Rever respostas',exact:true}).click();
   const beforeRestart = await page.evaluate(key=>localStorage.getItem(key),key);
   await page.locator('#new-session').click();
   assert.match(await page.locator('#finish-title').innerText(),/Encerrar e preparar/);
   assert.equal(await page.locator('#finish-dialog [data-close-dialog]').evaluate(el=>el===document.activeElement),true);
   await page.keyboard.press('Escape');
   assert.equal(await page.evaluate(key=>localStorage.getItem(key),key),beforeRestart);
   await page.locator('#new-session').click();await page.locator('#confirm-finish').click();
   await page.locator('#study-landing').waitFor();
   const restarted = await progress(page);
   assert.equal(restarted.active,null);assert.equal(restarted.history.length,2);
   assert.deepEqual(restarted.history[0],finished.history[0]);
   assert.equal(restarted.history[1].id,second.active.id);assert.equal(restarted.history[1].answers.length,1);
   assert.equal(await page.locator('#start-study').innerText(),'Iniciar questões');
   // Starting and finishing a blank session shows an explanation instead of a dead review button.
   await page.locator('#start-study').click();await page.locator('#finish-study').waitFor();
   await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();
   await page.locator('.correction').waitFor();
   assert.equal(await page.locator('#review-errors').count(),0);
   assert.match(await page.locator('.result-next-copy').innerText(),/Nenhum erro/);
   assert.deepEqual(errors,[]);await page.close();
  }
 } finally { await browser.close(); }
 console.log('New session passed: selection reset, no automatic start, completed history preserved, active draft finalized only on confirmation, cancel, reload, review errors and responsive action groups at 320/1280px.');
})().catch(e=>{console.error(e);process.exit(1);});
