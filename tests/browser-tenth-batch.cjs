const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/';
const key='questionador-concursos.progress.v1';
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
  for(const width of [320,1280]) {
   const context=await browser.newContext({viewport:{width,height:1000}}),page=await context.newPage();
   const errors=[],external=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(base))external.push(r.url());});
   await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
   await page.locator('#consolidation-tab').click();
   await page.screenshot({path:'/tmp/tenth-notices-'+width+'.png',fullPage:true});
   await page.locator('#questionador-tab').click();
   for(const block of ['basic','specific']) {
    await page.locator('#customize-study').click();
    await page.locator('#study-block').selectOption(block);
    await page.locator('#study-type').selectOption('true_false');
    await page.locator('#study-quantity').fill('90');
    await page.locator('#apply-study-options').click();await page.locator('#start-study').click();
    await page.locator('#current-question-heading').filter({hasText:'Questão 1 de 90'}).waitFor();
    for(let i=0;i<90;i++) {
     const value=await page.evaluate(({key,index})=>JSON.parse(localStorage.getItem(key)).progress.active.items[index].key.value,{key,index:i});
     await page.locator('input[value="'+value+'"]').check();
     await page.waitForFunction(({key,count})=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===count,{key,count:i+1});
     assert.equal(await page.locator('.correction').count(),0);
     if(i%20===0)for(const theme of ['light','dark']) {
      await page.evaluate(t=>{document.documentElement.dataset.theme=t;document.documentElement.style.fontSize='200%';},theme);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      await page.evaluate(()=>document.documentElement.style.fontSize='');
     }
     if(i===44) {
      await page.reload();await page.locator('#start-study').click();
      await page.locator('#current-question-heading').filter({hasText:'Questão 45 de 90'}).waitFor();
     }
     if(i<89) {
      await page.locator('#next-question').click();
      await page.locator('#current-question-heading').filter({hasText:'Questão '+(i+2)+' de 90'}).waitFor();
     }
    }
    await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.correction').waitFor();
    const result=await page.evaluate(key=>{const h=JSON.parse(localStorage.getItem(key)).progress.history.at(-1);return {count:h.items.length,right:h.answers.filter(a=>h.items.find(i=>i.question.id===a.questionId).key.value===a.value).length,comments:h.items.filter(i=>i.explanations.length).length,block:h.selection.block,profile:h.scoringProfile};},key);
    assert.deepEqual(result,{count:90,right:90,comments:90,block,profile:null});
    await page.locator('#new-session').click();
   }
   const saved=await page.evaluate(key=>{
    const p=JSON.parse(localStorage.getItem(key)).progress,items=p.history.flatMap(h=>h.items);
    const restored=Study.importBackup(Study.exportBackup(p),window.CONCURSOS_CATALOG);
    return {sessions:p.history.length,items:items.length,distinct:new Set(items.map(i=>i.question.id)).size,restored:restored.history.length};
   },key);
   assert.deepEqual(saved,{sessions:2,items:180,distinct:180,restored:2});
   assert.deepEqual(errors,[]);assert.deepEqual(external,[]);await context.close();
  }
  console.log('Tenth batch passed: two distinct 90-item CE practices, 180 corrections/comments, halfway reload, 180 distinct saved snapshots, backup, 320/1280px, light/dark, 200% text and no external runtime requests.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
