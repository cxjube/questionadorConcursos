const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.APP_BASE_URL || 'http://127.0.0.1:8000/';
const key = 'questionador-concursos.progress.v1';
(async () => {
 const browser = await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
  for (const width of [320,1280]) {
   const page = await browser.newPage({viewport:{width,height:1100}});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
   assert.equal(await page.locator('#study-options').getAttribute('open'),null);
   await page.locator('#customize-study').focus();await page.keyboard.press('Enter');
   assert.equal(await page.locator('#study-topic').isDisabled(),true);
   assert.equal(await page.locator('#study-discipline option[value="lingua-inglesa"]').isDisabled(),false);
   await page.locator('#study-discipline').selectOption('comunicacao-social');
   await page.locator('#study-topic').selectOption('comunicacao-social-2');
   assert.match(await page.locator('#study-filter-status').innerText(),/12 de 12/);
   await page.locator('#study-quantity').fill('13');
   assert.equal(await page.locator('#start-study').isDisabled(),true);
   assert.equal(await page.locator('#study-quantity').getAttribute('aria-invalid'),'true');
   assert.match(await page.locator('#study-filter-status').innerText(),/entre 1 e 12/);
   await page.locator('#study-quantity').fill('2');await page.locator('#study-shuffle').check();
   await page.locator('#apply-study-options').click();
   for (const theme of ['light','dark']) {
    await page.locator('[data-theme-choice="'+theme+'"]').click();
    await page.locator('#customize-study').click();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.screenshot({path:'/tmp/questionador-filters-'+width+'-'+theme+'.png',fullPage:true});
    await page.locator('#apply-study-options').click();
   }
   await page.locator('#customize-study').click();
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
   await page.evaluate(()=>document.documentElement.style.fontSize='');
   await page.locator('#apply-study-options').click();
   await page.locator('#start-study').click();await page.locator('#current-question-heading').waitFor();
   const original = await page.evaluate(key=>JSON.parse(localStorage.getItem(key)).progress.active,key);
   assert.equal(original.items.length,2);assert.equal(original.selection.topicId,'comunicacao-social-2');
   assert.equal(original.selection.shuffle,true);assert.equal(new Set(original.items.map(i=>i.question.id)).size,2);
   assert.ok(original.items.every(i=>i.mappings.some(m=>m.topicId.startsWith('comunicacao-social-2-'))));
   assert.equal(await page.locator('.correction').count(),0);
   await page.locator('input[value="false"]').check();
   await page.waitForFunction(key=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===1,key);
   await page.locator('#study-objective').click();
   assert.equal(await page.locator('#study-quantity').isDisabled(),true);
   await page.locator('#contest').selectOption('abdi-2026');
   assert.equal(await page.locator('#start-study').innerText(),'Continuar questões');
   assert.match(await page.locator('#study-resume-note').innerText(),/Câmara dos Deputados/);
   await page.reload();await page.locator('#start-study').click();
   const resumed=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)).progress.active,key);
   assert.equal(resumed.id,original.id);assert.deepEqual(resumed.items,original.items);assert.deepEqual(resumed.selection,original.selection);
   assert.equal(await page.locator('input[value="false"]').isChecked(),true);
   await page.locator('#review-study').click();await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();
   await page.locator('.correction').waitFor();
   assert.equal(await page.locator('#current-question-heading').innerText(),'Questão 1 de 2');
   await page.locator('#study-objective').click();
   if(await page.locator('#study-options').getAttribute('open')===null) await page.locator('#customize-study').click();
   await page.locator('#reset-study-filters').click();
   assert.equal(await page.locator('#study-quantity').inputValue(),'');assert.equal(await page.locator('#study-discipline').inputValue(),'');
   await page.locator('#apply-study-options').click();
   await page.locator('#contest').selectOption('cgu-2026');
   assert.equal(await page.locator('#start-study').isDisabled(),false);
   assert.match(await page.locator('#study-availability').innerText(),/106 questões/);
   await page.locator('#contest').selectOption('camara-2026');
   assert.equal(await page.locator('#start-study').isEnabled(),true);
   assert.deepEqual(errors,[]);await page.close();
  }
 } finally { await browser.close(); }
 console.log('Filters passed: parent topics, counts, quantity validation, draw, immutable resume, legacy navigation, confirmed goals, light/dark, keyboard and 200% text at 320/1280px.');
})().catch(e=>{console.error(e);process.exit(1);});
