const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/';
const storageKey='questionador-concursos.progress.v1';
const groups=[
 ['source-961-anatel-cb1-01','lingua-inglesa',[true,false,true,false,false,false,true]],
 ['source-094-pf-cb1-01','tecnologia-informacao-dados',[true,false,true,true]],
 ['source-057-ibama-cb1-01','tecnologia-informacao-dados',[true]],
 ['source-057-ibama-001-01','direito-administrativo-administracao-publica',[false,false,false,true,false,false]],
 ['source-038-anm-008-01','',[true,true]],
 ['source-038-anm-012-01','',[true,true]],
 ['source-038-anm-013-01','',[true,false]]
];
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
  for(const width of [320,1280]) {
   const context=await browser.newContext({viewport:{width,height:1000}}),page=await context.newPage();
   const errors=[],external=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(base))external.push(r.url());});
   await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
   for(const [paper,discipline,answers] of groups) {
    await page.locator('#customize-study').click();
    await page.locator('#study-paper').selectOption(paper);
    if(discipline)await page.locator('#study-discipline').selectOption(discipline);
    await page.locator('#study-type').selectOption('true_false');
    await page.locator('#study-quantity').fill(String(answers.length));
    await page.locator('#apply-study-options').click();await page.locator('#start-study').click();
    if(discipline==='lingua-inglesa') {
     assert.equal(await page.locator('.question-stem').getAttribute('lang'),'en');
     assert.match(await page.locator('.source-credit').innerText(),/unsdg\.un\.org/);
     assert.match(await page.locator('.question-context').first().innerText(),/50,000 people/);
    }
    for(const [index,value] of answers.entries()) {
     await page.locator('input[value="'+value+'"]').check();
     await page.waitForFunction(({key,count})=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===count,{key:storageKey,count:index+1});
     assert.equal(await page.locator('.correction').count(),0);
     for(const theme of ['light','dark']) {
      await page.evaluate(t=>{document.documentElement.dataset.theme=t;document.documentElement.style.fontSize='200%';},theme);
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
     }
     await page.evaluate(()=>document.documentElement.style.fontSize='');
     if(index<answers.length-1) {
      await page.locator('#next-question').click();
      await page.locator('#current-question-heading').filter({hasText:'Questão '+(index+2)+' de '+answers.length}).waitFor();
     }
    }
    await page.reload();await page.locator('#start-study').click();
    await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.didactic-comment').waitFor();
    const saved=await page.evaluate(key=>{const h=JSON.parse(localStorage.getItem(key)).progress.history.at(-1);return {count:h.items.length,right:h.answers.filter(a=>h.items.find(i=>i.question.id===a.questionId).key.value===a.value).length,comments:h.items.filter(i=>i.explanations.length===1).length};},storageKey);
    assert.deepEqual(saved,{count:answers.length,right:answers.length,comments:answers.length});
    if(paper==='source-094-pf-cb1-01') {
     await page.locator('#next-question').click();await page.locator('#next-question').click();
     assert.match(await page.locator('.didactic-comment a[href^="https://learn.microsoft.com/"]').getAttribute('href'),/potentially-unwanted-apps-microsoft-defender-antivirus/);
     assert.match(await page.locator('.didactic-comment').innerText(),/habilitada/);
    }
    await page.locator('#new-session').click();
   }
   const history=await page.evaluate(key=>JSON.parse(localStorage.getItem(key)).progress.history.length,storageKey);
   assert.equal(history,7);assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
   await context.close();
  }
  console.log('Ninth batch passed: 24 official answers, seven new-source sessions, full English passages, Microsoft references, reload/history, 200% text, light/dark, 320/1280px and no external runtime requests.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
