const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const base = process.env.APP_BASE_URL || 'http://127.0.0.1:8000/';
const key = 'questionador-concursos.progress.v1';
const progress = page => page.evaluate(key=>JSON.parse(localStorage.getItem(key)).progress,key);
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
  for(const width of [320,1280]) {
   const page=await browser.newPage({viewport:{width,height:1000}});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.clock.install({time:new Date('2026-10-23T12:00:00.000Z')});
   await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
   await page.locator('#customize-study').click();
   await page.locator('#study-paper').selectOption('source-232funprespexe-cb1-01');
   await page.locator('#study-year').selectOption('2025');
   assert.equal(await page.locator('#start-study').isDisabled(),true);
   assert.match(await page.locator('#study-filter-status').innerText(),/Nenhuma questão/);
   await page.locator('#study-year').selectOption('2016');
   await page.locator('#study-type').selectOption('multiple_choice');
   assert.equal(await page.locator('#start-study').isDisabled(),true);
   await page.locator('#study-type').selectOption('true_false');
   await page.locator('#study-quantity').fill('3');
   await page.locator('#study-minutes').fill('0');assert.equal(await page.locator('#start-study').isDisabled(),true);
   await page.locator('#study-minutes').fill('1');await page.locator('#study-scoring').selectOption('net');
   await page.locator('#apply-study-options').click();
   for(const theme of ['light','dark']) {
    await page.locator('[data-theme-choice="'+theme+'"]').click();
    await page.locator('#customize-study').click();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.screenshot({path:'/tmp/timed-options-'+width+'-'+theme+'.png',fullPage:true});
    await page.locator('#apply-study-options').click();
   }
   await page.locator('#customize-study').click();
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
   await page.evaluate(()=>document.documentElement.style.fontSize='');
   await page.locator('#apply-study-options').click();
   await page.locator('#start-study').click();await page.locator('#finish-study').waitFor();
   const session=(await progress(page)).active;
   assert.equal(session.items.length,3);assert.equal(session.selection.year,2016);
   assert.equal(session.timer.durationSeconds,60);assert.equal(session.scoringProfile.incorrect,-1);
   const wrong=String(!session.items[0].key.value);
   await page.locator('input[value="'+wrong+'"]').check();
   await page.waitForFunction(key=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===1,key);
   await page.clock.fastForward(20000);await page.reload();await page.locator('#start-study').click();await page.locator('#finish-study').waitFor();
   assert.equal((await progress(page)).active.timer.deadlineAt,session.timer.deadlineAt);
   assert.equal(await page.locator('input[value="'+wrong+'"]').isChecked(),true);
   // Expiry also works while the confirmation dialog is open.
   await page.locator('#finish-study').click();await page.clock.fastForward(60000);
   await page.locator('#training-score').waitFor();
   assert.equal(await page.locator('#finish-dialog').isVisible(),false);
   let p=await progress(page);assert.equal(p.active,null);assert.equal(p.history.length,1);
   assert.equal(p.history[0].finishReason,'time_limit');assert.equal(p.history[0].finishedAt,session.timer.deadlineAt);
   assert.match(await page.locator('#training-score').innerText(),/-1 \/ 3/);
   assert.equal(await page.locator('input[name="answer"]').count(),0);
   for(const theme of ['light','dark']) {
    await page.locator('[data-theme-choice="'+theme+'"]').click();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.locator('#study-content .metrics').screenshot({path:'/tmp/timed-results-'+width+'-'+theme+'.png'});
   }
   await page.clock.fastForward(30000);assert.equal((await progress(page)).history.length,1);
   await page.locator('#new-session').click();await page.locator('#customize-study').click();
   assert.equal(await page.locator('#study-minutes').inputValue(),'');assert.equal(await page.locator('#study-scoring').inputValue(),'none');
   assert.equal(await page.locator('#study-paper').inputValue(),'');assert.equal(await page.locator('#study-year').inputValue(),'');assert.equal(await page.locator('#study-type').inputValue(),'');
   await page.locator('#study-quantity').fill('1');await page.locator('#study-minutes').fill('1');await page.locator('#apply-study-options').click();
   await page.locator('#start-study').click();await page.locator('#finish-study').waitFor();
   const second=(await progress(page)).active;
   // Closed-page time is wall time, not interval ticks. Reopen beyond the deadline.
   await page.goto('about:blank');await page.clock.fastForward(70000);await page.goto(base);
   await page.locator('.correction').waitFor();p=await progress(page);
   assert.equal(p.active,null);assert.equal(p.history.length,2);assert.equal(p.history[1].finishedAt,second.timer.deadlineAt);
   assert.equal(p.history[1].scoringProfile,null);assert.equal(await page.locator('#training-score').count(),0);
   assert.deepEqual(errors,[]);await page.close();
  }
 } finally {await browser.close();}
 console.log('Timed practice passed: filters, invalid time, scoring, negative result, persisted deadline and answers, reload/closed page, automatic single finish, dialog closure, new-session reset, light/dark and 200% text at 320/1280px.');
})().catch(e=>{console.error(e);process.exit(1);});
