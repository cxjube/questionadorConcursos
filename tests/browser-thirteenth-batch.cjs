const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/';
const key='questionador-concursos.progress.v1';
const cases=[['source-072-stm-004-01','',10],['source-988-cpnuje-010-01','',2]];
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
  for(const width of [320,1280]) {
   const context=await browser.newContext({viewport:{width,height:1000}}),page=await context.newPage();
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   for(const [paper,topic,count] of cases) {
    await page.goto(base);await page.evaluate(()=>localStorage.clear());await page.reload();await page.locator('#start-study:not([disabled])').waitFor();
    assert.match(await page.locator('#study-availability').innerText(),/^266 questões/);
    await page.locator('[data-theme-choice="'+(width===320?'light':'dark')+'"]').click();
    await page.locator('#customize-study').click();await page.locator('#study-paper').selectOption(paper);
    if(topic) {
     const discipline=await page.evaluate(topic=>window.CONCURSOS_CATALOG.topics.find(t=>t.id===topic).disciplineId,topic);
     await page.locator('#study-discipline').selectOption(discipline);await page.locator('#study-topic').selectOption(topic);
    }
    await page.locator('#apply-study-options').click();await page.locator('#start-study').click();await page.locator('#finish-study').waitFor();
    const session=await page.evaluate(k=>JSON.parse(localStorage.getItem(k)).progress.active,key);
    console.log('Checking',width,paper,topic||'all',count);
    assert.equal(session.items.length,count);assert.ok(session.items.every(i=>i.question.origin.paperId===paper&&i.question.type==='true_false'));
    assert.equal(await page.locator('.correction').count(),0);
    for(let index=0;index<count;index++) {
     await page.locator('input[value="'+session.items[index].key.value+'"]').check();
     await page.waitForFunction(({key,n})=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===n,{key,n:index+1});
     if(index+1<count) {
      await page.locator('#next-question').click();
      await page.locator('#current-question-heading').filter({hasText:'Questão '+(index+2)+' de '+count}).waitFor();
     }
    }
    await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.didactic-comment').waitFor();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.evaluate(()=>document.documentElement.style.fontSize='200%');
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.evaluate(()=>document.documentElement.style.fontSize='');
    await page.screenshot({path:'/tmp/thirteenth-'+paper+'-'+width+'.png',fullPage:true});
    const saved=await page.evaluate(k=>JSON.parse(localStorage.getItem(k)).progress,key);
    assert.equal(saved.history.length,1);assert.equal(saved.active,null);
    await page.reload();await page.locator('#start-study:not([disabled])').waitFor();
    assert.deepEqual(await page.evaluate(k=>JSON.parse(localStorage.getItem(k)).progress.history,key),saved.history);
   }
   assert.deepEqual(errors,[]);await context.close();
  }
  console.log('Thirteenth batch passed: two new origins, all 12 new questions per viewport, official correction/comments, target filters, history/reload, light/dark and 200% text at 320/1280px.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
