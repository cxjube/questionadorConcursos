const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/';
const key='questionador-concursos.progress.v1',role='abdi-comunicacao-marketing';
const state=page=>page.evaluate(k=>JSON.parse(localStorage.getItem(k)).progress,key);
async function reflow(page){assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await page.evaluate(()=>document.documentElement.style.fontSize='200%');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await page.evaluate(()=>document.documentElement.style.fontSize='');}
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try{
  for(const width of [320,1280]){
   const context=await browser.newContext({viewport:{width,height:960},ignoreHTTPSErrors:base.startsWith('https:')}),page=await context.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
   await page.locator('#contest').selectOption('abdi-2026');assert.equal(await page.locator('#role').inputValue(),role);
   assert.match(await page.locator('#study-availability').innerText(),/^185 questões/);
   assert.equal(await page.locator('#study-format-note').isVisible(),true);assert.equal(await page.locator('#prepare-exam').isDisabled(),true);assert.match(await page.locator('#exam-availability').innerText(),/múltipla escolha/);
   await page.locator('[data-theme-choice="'+(width===320?'light':'dark')+'"]').click();
   await page.locator('#program-tab').click();assert.match(await page.locator('#program-summary').innerText(),/8 disciplinas · 97 tópicos/);assert.equal(await page.locator('#program .syllabus-group').count(),8);await reflow(page);
   await page.locator('#rules-tab').click();const rules=await page.locator('#rules').innerText();assert.match(rules,/Múltipla escolha/);assert.match(rules,/210 minutos/);assert.match(rules,/30 questões/);assert.equal((rules.match(/Maior que 0 pontos/g)||[]).length,3);assert.doesNotMatch(rules,/Certo\/Errado|null pontos|54 pontos|−1/);await reflow(page);
   await page.locator('#consolidation-tab').click();assert.equal(await page.locator('#camara-reference-details').isVisible(),false);assert.equal(await page.locator('#notices li').count(),1);assert.match(await page.locator('#notices a').getAttribute('href'),/edital-01-2026-abertura/);assert.equal(await page.locator('#official-watch-links a[href="https://conhecimento.fgv.br/concursos/psabdi"]').count(),1);await reflow(page);
   await page.locator('#questionador-tab').click();await page.locator('#customize-study').click();const choices=await page.locator('#study-block option').allTextContents();assert.deepEqual(choices,['Todos os blocos','Conhecimentos gerais','Conhecimentos institucionais','Conhecimentos específicos']);
   await page.locator('#study-block').selectOption('institutional');await page.locator('#study-quantity').fill('1');assert.equal(await page.locator('#apply-study-options').isDisabled(),true);assert.match(await page.locator('#study-filter-status').innerText(),/Nenhuma questão/);assert.doesNotMatch(await page.locator('#study-filter-status').innerText(),/1 e 0/);
   await page.keyboard.press('Escape');assert.equal(await page.locator('#study-block').inputValue(),'');assert.equal(await page.locator('#study-quantity').inputValue(),'');
   await page.locator('#customize-study').click();await page.locator('#study-type').selectOption('multiple_choice');await page.locator('#study-quantity').fill('6');await page.locator('#apply-study-options').click();await page.locator('#start-study').click();await page.locator('#finish-study').waitFor();let active=(await state(page)).active;assert.equal(active.roleId,role);assert.equal(active.items.length,6);
   await page.locator('input[value="'+active.items[0].key.value+'"]').check();await page.waitForFunction(k=>JSON.parse(localStorage.getItem(k)).progress.active.answers.length===1,key);
   await page.reload();await page.locator('#start-study:not([disabled])').waitFor();assert.equal(await page.locator('#contest').inputValue(),'abdi-2026');await page.locator('#start-study').click();await page.locator('#finish-study').waitFor();assert.equal((await state(page)).active.items.length,6);
   for(let i=0;i<6;i++){
    assert.equal(await page.locator('input[name="answer"]').count(),6);assert.equal(active.items[i].question.type,'multiple_choice');assert.ok(active.items[i].mappings.every(m=>m.roleId===role));
    await page.locator('input[value="'+active.items[i].key.value+'"]').check();await page.waitForFunction(({key,n})=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===n,{key,n:i+1});if(i<5){await page.locator('#next-question').click();await page.locator('#current-question-heading').filter({hasText:'Questão '+(i+2)+' de 6'}).waitFor();}
   }
   await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.didactic-comment').waitFor();assert.equal((await state(page)).history[0].scoringProfile,null);await reflow(page);
   await page.locator('#new-session').click();await page.locator('#customize-study').click();await page.locator('#study-block').selectOption('basic');await page.locator('#study-type').selectOption('true_false');await page.locator('#study-quantity').fill('2');await page.locator('#apply-study-options').click();await page.locator('#start-study').click();await page.locator('#finish-study').waitFor();active=(await state(page)).active;assert.equal(active.items.length,2);assert.ok(active.items.every(i=>i.question.type==='true_false'&&i.mappings.every(m=>m.roleId===role)));
   for(let i=0;i<2;i++){await page.locator('input[value="'+active.items[i].key.value+'"]').check();await page.waitForFunction(({key,n})=>JSON.parse(localStorage.getItem(key)).progress.active.answers.length===n,{key,n:i+1});if(i===0){await page.locator('#next-question').click();await page.locator('#current-question-heading').filter({hasText:'Questão 2 de 2'}).waitFor();}}
   await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('#new-session').waitFor();await page.locator('#new-session').click();
   const saved=await state(page);assert.equal(saved.history.length,2);assert.ok(saved.history.every(s=>s.roleId===role));
   assert.equal(await page.evaluate(({key,role})=>Study.performance(JSON.parse(localStorage.getItem(key)).progress.history,role).attempts,{key,role:'camara-comunicacao-divulgacao'}),0);
   await page.locator('#contest').selectOption('camara-2026');assert.match(await page.locator('#study-availability').innerText(),/^395 questões/);assert.equal(await page.locator('#study-format-note').isVisible(),false);assert.equal(await page.locator('#prepare-exam').isDisabled(),false);assert.equal(await page.locator('#study-block option[value="institutional"]').count(),0);
   assert.deepEqual(errors,[]);await context.close();console.log('ABDI verified at width',width);
  }
  console.log('ABDI passed: exact program/rules, empty institutional filter, cancel, six original MC, CE practice, active-role resume, isolated history and unchanged Camara exam availability.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
