const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.APP_BASE_URL || 'http://127.0.0.1:8000/';
const key = 'questionador-concursos.progress.v1';
(async () => {
 const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 for (const width of [320,1280]) {
  const page = await browser.newPage({viewport:{width,height:950}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
  await page.locator('#start-study').click();
  const total = await page.evaluate(key=>JSON.parse(localStorage.getItem(key)).progress.active.items.length,key);
  const startState = await page.evaluate(key=>localStorage.getItem(key),key);
  assert.equal(await page.locator('#next-question').innerText(),'Próxima');
  assert.equal(await page.locator('#next-question').evaluate(el=>el.classList.contains('primary')),true);
  assert.equal(await page.locator('#finish-study').count(),0);
  assert.equal(await page.locator('.question-details').getAttribute('open'),null);
  assert.equal(await page.locator('.question-instruction').isVisible(),true);
  const top = await page.locator('#next-question').evaluate(el=>el.getBoundingClientRect().top+scrollY);
  await page.locator('input[value="false"]').check();
  await page.waitForFunction(key=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===1,key);
  assert.equal(await page.locator('#next-question').evaluate(el=>el.getBoundingClientRect().top+scrollY),top);
  await page.locator('.question-details summary').click();
  assert.equal(await page.locator('.source-links').isVisible(),true);
  await page.locator('input[value="true"]').check();
  await page.waitForFunction(key=>JSON.parse(localStorage.getItem(key)).progress.active.answers[0].value===true,key);
  assert.equal(await page.locator('.question-details').getAttribute('open'),'');
  await page.locator('#next-question').focus();await page.keyboard.press('Enter');
  await page.waitForFunction(key=>JSON.parse(localStorage.getItem(key)).progress.active.position===1,key);
  const beforeReview = await page.evaluate(key=>localStorage.getItem(key),key);
  await page.locator('#review-study').click();
  assert.equal(await page.locator('.question-map button').count(),total);
  assert.equal(await page.locator('.correction').count(),0);
  assert.equal(await page.evaluate(key=>localStorage.getItem(key),key),beforeReview);
  await page.locator('.question-map button').first().click();
  await page.locator('input[value="true"]:checked').waitFor();
  await page.locator('#review-study').click();await page.locator('#finish-study').click();
  assert.equal(await page.locator('#finish-dialog [data-close-dialog]').evaluate(el=>el===document.activeElement),true);
  await page.keyboard.press('Escape');assert.equal(await page.locator('#finish-dialog').isVisible(),false);
  assert.equal(await page.evaluate(key=>JSON.parse(localStorage.getItem(key)).progress.history.length,key),0);
  await page.getByRole('button',{name:'Voltar às questões',exact:true}).click();
  // Reaching the last question opens review; it cannot finalize a session.
  for(let i=0;i<total-1;i++) {
   await page.locator('#next-question').click();
   await page.waitForFunction(({position,total})=>document.getElementById('current-question-heading')?.textContent==='Questão '+position+' de '+total,{position:i+2,total});
  }
  assert.equal(await page.locator('#next-question').innerText(),'Revisar sessão');
  assert.equal(await page.locator('#finish-study').count(),0);
  await page.locator('#next-question').click();
  assert.equal(await page.evaluate(key=>JSON.parse(localStorage.getItem(key)).progress.history.length,key),0);
  await page.getByRole('button',{name:'Voltar às questões',exact:true}).click();
  for(const theme of ['light','dark']) {
   await page.locator('[data-theme-choice="'+theme+'"]').click();
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  }
  await page.evaluate(()=>document.documentElement.style.fontSize='200%');
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  await page.evaluate(()=>document.documentElement.style.fontSize='');
  await page.locator('#program-tab').click();await page.locator('#program details summary').first().click();
  assert.equal(await page.locator('#program .program-reference').first().isVisible(),false);
  await page.locator('#show-program-references').check();
  assert.equal(await page.locator('#program .program-reference').first().isVisible(),true);
  await page.locator('#questionador-tab').click();await page.locator('#study-history').click();
  assert.equal(await page.locator('#backup-tools').getAttribute('open'),null);
  assert.equal(await page.getByRole('button',{name:'Apagar progresso deste navegador',exact:true}).isVisible(),false);
  await page.locator('#backup-tools summary').focus();await page.keyboard.press('Space');
  assert.equal(await page.getByRole('button',{name:'Exportar backup',exact:true}).isVisible(),true);
  assert.notEqual(await page.evaluate(key=>localStorage.getItem(key),key),startState);
  assert.deepEqual(errors,[]);await page.close();
 }
 await browser.close();
 console.log('Usability passed: stable navigation, primary next, review before finish, last-question safety, keyboard/cancel, disclosure persistence, references, 200% text and light/dark at 320/1280px.');
})().catch(e=>{console.error(e);process.exit(1);});
