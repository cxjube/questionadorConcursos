const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/';
const key='questionador-concursos.progress.v1';
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'../data/reviews/fifteenth-batch.json'),'utf8'));
const added=new Set(manifest.items.map(r=>r.questionId));
const cases=[['source-camara14-cb1-01',11],['source-camara14-001-01',6],['source-108-tcutefc-001-01',6],['source-803-tj-es-006-01',6],['source-893-dataprev-005-01',6],['source-038-anm-005-01',1],['source-038-anm-024-01',11]];
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
  for(const width of [320,1280]) {
   const context=await browser.newContext({viewport:{width,height:1000}}),page=await context.newPage(),seen=new Set(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   for(const [paper,count,topic] of cases) {
    await page.goto(base);await page.evaluate(()=>localStorage.clear());await page.reload();await page.locator('#start-study:not([disabled])').waitFor();
    assert.match(await page.locator('#study-availability').innerText(),/^339 questões/);
    await page.locator('[data-theme-choice="'+(width===320?'light':'dark')+'"]').click();
    await page.locator('#consolidation-tab').click();await page.getByText('Materiais de referência da Câmara',{exact:true}).click();
    const refs=page.locator('#study-reference-links a');assert.equal(await refs.count(),4);
    for(const a of await refs.all()) {assert.equal(await a.getAttribute('target'),'_blank');assert.match(await a.getAttribute('href'),/^https:\/\//);assert.match(await a.getAttribute('rel'),/noopener/);}
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.locator('#questionador-tab').click();
    await page.locator('#customize-study').click();await page.locator('#study-paper').selectOption(paper);
    if(topic) {await page.locator('#study-discipline').selectOption('processo-legislativo-regimento');await page.locator('#study-topic').selectOption(topic);}
    await page.locator('#study-quantity').fill(String(count));await page.locator('#apply-study-options').click();await page.locator('#start-study').click();await page.locator('#finish-study').waitFor();
    const session=await page.evaluate(k=>JSON.parse(localStorage.getItem(k)).progress.active,key);
    assert.equal(session.items.length,count);assert.ok(session.items.every(i=>i.question.origin.paperId===paper));
    console.log('Checking',width,paper,count);
    for(let index=0;index<count;index++) {
     const item=session.items[index];if(added.has(item.question.id))seen.add(item.question.id);
     if(paper==='source-142-tcuaufc-cb1-01') {assert.equal(await page.locator('.question-context').getAttribute('lang'),'en');assert.equal(await page.locator('.question-stem').getAttribute('lang'),'en');}
     if(topic) {assert.equal(item.question.type,'multiple_choice');assert.equal(await page.locator('input[name="answer"]').count(),6);assert.equal(await page.locator('.question-stem').evaluate(e=>getComputedStyle(e).whiteSpace),'pre-line');}
     await page.locator('input[value="'+item.key.value+'"]').check();
     await page.waitForFunction(({key,n})=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===n,{key,n:index+1});
     if(index+1<count) {await page.locator('#next-question').click();await page.locator('#current-question-heading').filter({hasText:'Questão '+(index+2)+' de '+count}).waitFor();}
    }
    await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.didactic-comment').waitFor();
    for(let index=0;index<count;index++) {
     const item=session.items[index];
     if(added.has(item.question.id)) {
      const links=await page.locator('.comment-references a').evaluateAll(es=>es.map(e=>e.href));
      assert.ok(item.explanations.every(e=>e.references.every(r=>links.includes(r.officialUrl))));
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
      await page.evaluate(()=>document.documentElement.style.fontSize='200%');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await page.evaluate(()=>document.documentElement.style.fontSize='');
      if(paper==='source-camara14-cb1-01'&&index===0)await page.screenshot({path:'/tmp/qc15-regimento-'+width+'.png',fullPage:true});
      if(paper==='source-142-tcuaufc-cb1-01'&&index===0)await page.screenshot({path:'/tmp/qc14-english-'+width+'.png',fullPage:true});
     }
     if(index+1<count) {await page.locator('#next-question').click();await page.locator('#current-question-heading').filter({hasText:'Questão '+(index+2)+' de '+count}).waitFor();}
    }
    const saved=await page.evaluate(k=>JSON.parse(localStorage.getItem(k)).progress,key);assert.equal(saved.active,null);assert.equal(saved.history.length,1);
    await page.reload();await page.locator('#start-study:not([disabled])').waitFor();assert.deepEqual(await page.evaluate(k=>JSON.parse(localStorage.getItem(k)).progress.history,key),saved.history);
   }
   assert.deepEqual([...seen].sort(),[...added].sort());assert.deepEqual(errors,[]);await context.close();
  }
  console.log('Fifteenth batch passed: all 37 new CE items, normative/STF/government links, manual links, history/reload, light/dark and 200% text at 320/1280px.');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
