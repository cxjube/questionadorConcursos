const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs/promises');
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/';
const key='questionador-concursos.progress.v1';
const progress=page=>page.evaluate(key=>JSON.parse(localStorage.getItem(key)).progress,key);
async function reflow(page) {
 for(const theme of ['light','dark']) {
  await page.locator('[data-theme-choice="'+theme+'"]').click();
  for(const size of ['','200%']) {
   await page.evaluate(size=>document.documentElement.style.fontSize=size,size);
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
   assert.equal(await page.evaluate(()=>[...document.querySelectorAll('dialog[open]')].every(d=>d.scrollWidth<=d.clientWidth+1)),true);
  }
 }
 await page.evaluate(()=>document.documentElement.style.fontSize='');
}
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
  for(const width of [320,1280]) {
   const context=await browser.newContext({viewport:{width,height:1000}}),page=await context.newPage();
   const errors=[],external=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(new URL(base).origin+'/')&&!r.url().startsWith('blob:'))external.push(r.url());});
   await page.clock.install({time:new Date('2026-10-23T12:00:00.000Z')});
   await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
   await page.screenshot({path:'/tmp/exam-landing-'+width+'.png',fullPage:true});
   // Keep a real legacy-style unscored practice alongside the new exam.
   await page.locator('#customize-study').click();await page.locator('#study-quantity').fill('1');await page.locator('#apply-study-options').click();
   await page.locator('#start-study').click();await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.correction').waitFor();
   const practice=(await progress(page)).history[0];assert.equal(practice.scoringProfile,null);
   await page.locator('#new-session').click();
   await page.locator('#customize-study').click();await page.locator('#study-quantity').fill('1');await page.locator('#study-minutes').fill('1');await page.locator('#study-scoring').selectOption('right_only');await page.locator('#apply-study-options').click();
   await page.locator('#prepare-exam').focus();await page.keyboard.press('Enter');await page.locator('#exam-dialog[open]').waitFor();
   assert.equal((await progress(page)).active,null);
   assert.match(await page.locator('#exam-description-details').innerText(),/mínimo 18 pontos/);
   assert.match(await page.locator('#exam-description-details').innerText(),/mínimo 27 pontos/);
   await page.keyboard.press('Escape');assert.equal(await page.locator('#exam-dialog').isVisible(),false);
   await page.locator('#prepare-exam').click();
   // Check the dialog itself at 200% without clicking behind a modal.
   for(const size of ['','200%']) {
    await page.evaluate(size=>document.documentElement.style.fontSize=size,size);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth && document.querySelector('#exam-dialog').scrollWidth<=document.querySelector('#exam-dialog').clientWidth+1),true);
   }
   await page.evaluate(()=>document.documentElement.style.fontSize='');
   await page.screenshot({path:'/tmp/exam-dialog-'+width+'.png',fullPage:true});
   await page.locator('#start-exam').click();await page.locator('#finish-study').waitFor();
   const session=(await progress(page)).active;
   assert.equal(session.items.length,180);assert.equal(new Set(session.items.map(i=>i.question.id)).size,180);
   assert.equal(session.timer.durationSeconds,18000);assert.equal(session.scoringProfile.rule.version,1);
   assert.equal(await page.locator('.correction').count(),0);assert.equal(await page.locator('#training-score').count(),0);
   assert.equal(await page.locator('.question-details a').filter({hasText:'Gabarito'}).count(),0);
   await page.locator('[data-exam-block="p2"]').click();await page.locator('#current-question-heading').filter({hasText:'Questão 91 de 180'}).waitFor();
   await page.locator('[data-exam-block="p1"]').click();await page.locator('#current-question-heading').filter({hasText:'Questão 1 de 180'}).waitFor();
   await page.locator('#study-history').click();assert.equal(await page.getByRole('button',{name:'Rever respostas',exact:true}).count(),0);
   assert.match(await page.locator('#study-content').innerText(),/resultados anteriores ficam ocultos/);
   await page.getByRole('button',{name:'Retomar sessão em andamento'}).click();
   for(let index=0;index<180;index++) {
    const item=session.items[index], correct=index<90 ? index<54 : index-90<63;
    const value=correct ? item.key.value : !item.key.value;
    await page.locator('input[value="'+value+'"]').check();
    await page.waitForFunction(({key,count})=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===count,{key,count:index+1});
    if(index===89) {
     await page.reload();await page.locator('#start-study').click();
     assert.equal((await progress(page)).active.timer.deadlineAt,session.timer.deadlineAt);
     assert.match(await page.locator('#current-question-heading').innerText(),/Questão 90 de 180/);
    }
    if(index===90) assert.match(await page.locator('.exam-current-block').innerText(),/P2.*questão 1 de 90/);
    if(index<179) {await page.locator('#next-question').click();await page.locator('#current-question-heading').filter({hasText:'Questão '+(index+2)+' de 180'}).waitFor();}
   }
   await reflow(page);
   await page.locator('#next-question').click();await page.locator('.exam-question-group').first().waitFor({state:'attached'});
   assert.equal(await page.locator('.exam-question-map button').count(),180);
   assert.equal(await page.locator('.correction').count(),0);assert.equal(await page.locator('#exam-results').count(),0);
   await reflow(page);await page.screenshot({path:'/tmp/exam-review-'+width+'.png',fullPage:true});
   await page.locator('#finish-study').click();await page.locator('#finish-dialog [data-close-dialog]').click();assert.ok((await progress(page)).active);
   await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('#exam-results').waitFor();
   const p=await progress(page);assert.equal(p.history.length,2);assert.equal(p.active,null);assert.deepEqual(p.history[0],practice);
   for(const [block,points] of [['p1',18],['p2',36],['total',54]]) {
    assert.match(await page.locator('[data-result-block="'+block+'"] dd').first().innerText(),new RegExp('^'+points+' / '));
    assert.equal(await page.locator('[data-result-block="'+block+'"] .exam-minimum').innerText(),'Mínimo atingido');
   }
   assert.match(await page.locator('.exam-outcome').innerText(),/atingiu os três mínimos/);
   assert.equal(await page.locator('.didactic-comment').count()>0,true);
   await reflow(page);await page.screenshot({path:'/tmp/exam-results-'+width+'.png',fullPage:true});
   await page.locator('#study-history').click();await page.locator('#backup-tools summary').click();
   const downloadEvent=page.waitForEvent('download');await page.getByRole('button',{name:'Exportar backup',exact:true}).click();
   const raw=await fs.readFile(await (await downloadEvent).path(),'utf8');assert.equal(JSON.parse(raw).progress.history[1].scoringProfile.kind,'official_rules');
   await page.locator('#import-backup').setInputFiles({name:'exam-backup.json',mimeType:'application/json',buffer:Buffer.from(raw)});
   await page.locator('#confirm-import').click();assert.deepEqual((await progress(page)).history,p.history);
   await page.locator('#study-objective').click();await page.locator('#prepare-exam').click();await page.locator('#start-exam').click();await page.locator('#finish-study').waitFor();
   const timed=(await progress(page)).active;
   await page.locator('input[value="'+timed.items[0].key.value+'"]').check();
   await page.waitForFunction(key=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===1,key);
   await page.goto('about:blank');await page.clock.fastForward(18001000);await page.goto(base);
   await page.locator('#exam-results').waitFor();
   const expired=await progress(page);assert.equal(expired.history.length,3);assert.equal(expired.history[2].finishedAt,timed.timer.deadlineAt);assert.equal(expired.history[2].finishReason,'time_limit');
   assert.match(await page.locator('[data-result-block="total"] dd').first().innerText(),/^1 \/ 180/);
   assert.match(await page.locator('.exam-outcome').innerText(),/não atingiu/);
   await page.reload();await page.locator('#start-study:not([disabled])').waitFor();assert.equal((await progress(page)).history.length,3);
   assert.deepEqual(errors,[]);assert.deepEqual(external,[]);await context.close();
  }
  // Clearly isolated copied-catalog fixture: only 89 basic C/E remain.
  const context=await browser.newContext(),page=await context.newPage();
  await page.route('**/data/catalog.js*',async route=>{const response=await route.fetch();await route.fulfill({response,body:await response.text()+`\n(()=>{const d=window.CONCURSOS_CATALOG,s=new Set(d.syllabusItems.filter(i=>i.block==='basic').map(i=>i.id)),ids=new Set(d.mappings.filter(m=>s.has(m.syllabusItemId)).map(m=>m.questionId));let count=0;d.questions=d.questions.filter(q=>!ids.has(q.id)||q.type!=='true_false'||++count<=89);})();\n`});});
  await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();assert.equal(await page.locator('#prepare-exam').isDisabled(),true);assert.match(await page.locator('#exam-availability').innerText(),/insuficiente/);await context.close();
  console.log('Exam passed: 180 distinct CE, independent settings, P1/P2 navigation, hidden corrections/history, exact 18+36=54 minima, persisted timer, legacy history, backup UI, five-hour expiry, shortage blocking, keyboard, light/dark and 200% text at 320/1280px.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
