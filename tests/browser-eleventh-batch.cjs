const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/';
const key='questionador-concursos.progress.v1';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
  for(const width of [320,1280]) {
   const context=await browser.newContext({viewport:{width,height:1000}}),page=await context.newPage(),errors=[],external=[];
   page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(new URL(base).origin+'/'))external.push(r.url());});
   await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
   assert.match(await page.locator('#study-availability').innerText(),/^224 questões/);
   await page.locator('#prepare-exam').click();assert.match(await page.locator('#exam-bank-note').innerText(),/sorteio usa apenas questões elegíveis/);await page.keyboard.press('Escape');
   const added=new Set();
   for(const paperId of ['source-846-serpro-23-cb1-01','source-018-stj-cb1-01','source-106-pf-cg1-01','source-038-anm-010-01','source-038-anm-012-01','source-038-anm-008-01']) {
    await page.locator('#customize-study').click();await page.locator('#study-paper').selectOption(paperId);await page.locator('#study-type').selectOption('true_false');await page.locator('#apply-study-options').click();
    await page.locator('#start-study').click();await page.locator('#finish-study').waitFor();
    const session=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)).progress.active,key);
    for(let i=0;i<session.items.length;i++) {
     const item=session.items[i],fresh=item.question.review.decisionReference==='documentation/eleventh-batch-release.md';
     if(fresh) {
      added.add(item.question.id);
      assert.equal(await page.locator('.correction').count(),0);
      if(item.question.language==='en') {
       assert.equal(await page.locator('.question-stem').getAttribute('lang'),'en');
       assert.equal(await page.locator('.question-context').first().getAttribute('lang'),'en');
      }
      if(item.question.id==='038-anm-012-01-q079') {
       assert.equal((await page.locator('.question-context').innerText()).includes('Manual de Identidade do Senado'),true);
       assert.equal((await page.locator('.question-context').innerText()).split('•').length-1,4);
      }
      for(const theme of ['light','dark']) {
       await page.locator('[data-theme-choice="'+theme+'"]').click();
       await page.evaluate(()=>document.documentElement.style.fontSize='200%');
       assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
       await page.evaluate(()=>document.documentElement.style.fontSize='');
      }
     }
     await page.locator('input[value="'+item.key.value+'"]').check();
     await page.waitForFunction(({key,count})=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===count,{key,count:i+1});
     if(paperId==='source-846-serpro-23-cb1-01' && i===1) {
      await page.reload();await page.locator('#start-study').click();await page.locator('#current-question-heading').filter({hasText:'Questão 2 de 4'}).waitFor();
     }
     if(i<session.items.length-1) {await page.locator('#next-question').click();await page.locator('#current-question-heading').filter({hasText:'Questão '+(i+2)+' de '+session.items.length}).waitFor();}
    }
    await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.correction').waitFor();
    const result=await page.evaluate(key=>{const p=JSON.parse(localStorage.getItem(key)).progress,s=p.history.at(-1);return {count:s.items.length,correct:Study.totals(s).correct,comments:s.items.filter(i=>i.explanations.length).length};},key);
    assert.deepEqual(result,{count:session.items.length,correct:session.items.length,comments:session.items.length});
    await page.locator('#new-session').click();
   }
   assert.equal(added.size,32);
   const restored=await page.evaluate(key=>{const p=JSON.parse(localStorage.getItem(key)).progress,r=Study.importBackup(Study.exportBackup(p),window.CONCURSOS_CATALOG);return {history:r.history.length,count:r.history.flatMap(s=>s.items).length};},key);
   assert.deepEqual(restored,{history:6,count:54});assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
   await page.screenshot({path:'/tmp/eleventh-landing-'+width+'.png',fullPage:true});await context.close();
  }
  console.log('Eleventh batch passed: all 32 new CE through six source selections, 54 correct answers/comments, full English/Senate contexts, reload, backup, 320/1280px, light/dark, 200% text and no external runtime requests.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
