'use strict';
const {chromium}=require('playwright'),assert=require('node:assert/strict');
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/',key='questionador-concursos.progress.v1';
const state=p=>p.evaluate(k=>JSON.parse(localStorage.getItem(k)).progress,key);
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});try{
 for(const [width,theme] of [[320,'light'],[1280,'light'],[320,'dark'],[1280,'dark']]){
  const context=await browser.newContext({viewport:{width,height:1000},ignoreHTTPSErrors:base.startsWith('https:')});const p=await context.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.addInitScript(()=>{let seed=Number(sessionStorage.getItem('test-only.random-seed'))||918273;Math.random=()=>{seed=(seed*16807)%2147483647;sessionStorage.setItem('test-only.random-seed',String(seed));return (seed-1)/2147483646;};});
  await p.goto(base);await p.locator('#start-study:not([disabled])').waitFor();await p.locator('[data-theme-choice="'+theme+'"]').click();
  await p.locator('#customize-study').click();assert.equal(await p.locator('#study-shuffle').count(),0);assert.equal(await p.locator('#study-topic-field').isVisible(),false);
  await p.locator('#study-discipline').selectOption('comunicacao-social');assert.equal(await p.locator('#study-topic-field').isVisible(),true);await p.locator('#study-topic').selectOption('comunicacao-social-2');await p.locator('#study-quantity').fill('3');await p.locator('#apply-study-options').click();
  // X is a cancellation: dependent values and quantity must return together.
  await p.locator('#customize-study').click();await p.locator('#study-discipline').selectOption('');assert.equal(await p.locator('#study-topic-field').isVisible(),false);assert.equal(await p.locator('#study-topic').inputValue(),'');await p.locator('#study-quantity').fill('9');await p.getByRole('button',{name:'Fechar personalização',exact:true}).click();
  assert.equal(await p.locator('#study-options').evaluate(e=>e.open),false);assert.equal(await p.locator('#study-discipline').inputValue(),'comunicacao-social');assert.equal(await p.locator('#study-topic').inputValue(),'comunicacao-social-2');assert.equal(await p.locator('#study-quantity').inputValue(),'3');assert.equal(await p.locator('#customize-study').evaluate(e=>e===document.activeElement),true);
  await p.locator('#customize-study').click();await p.locator('#study-quantity').fill('8');await p.keyboard.press('Escape');assert.equal(await p.locator('#study-quantity').inputValue(),'3');
  await p.locator('#customize-study').click();await p.locator('#study-quantity').fill('5');await p.locator('#study-options [data-close-dialog]').click();assert.equal(await p.locator('#study-quantity').inputValue(),'3');
  await p.locator('#customize-study').click();await p.locator('#reset-study-filters').click();assert.equal(await p.locator('#study-topic-field').isVisible(),false);await p.locator('#study-type').selectOption('true_false');await p.locator('#study-quantity').fill('8');
  for(const font of ['', '200%']){await p.evaluate(v=>document.documentElement.style.fontSize=v,font);const d=p.locator('#study-options');assert.ok(await d.evaluate(e=>e.scrollWidth<=e.clientWidth));assert.ok(await p.locator('#close-study-options').evaluate(e=>{const r=e.getBoundingClientRect(),d=e.closest('dialog').getBoundingClientRect();return r.top>=d.top&&r.right<=d.right;}));}
  await p.evaluate(()=>document.documentElement.style.fontSize='');
  const gap=await p.locator('#study-options').evaluate(e=>{const d=e.getBoundingClientRect(),b=e.querySelector('#apply-study-options').getBoundingClientRect();return d.bottom-b.bottom;});assert.ok(gap>=12&&gap<=20,'compact footer gap '+gap);
  await p.screenshot({path:'/tmp/questionador-refinement/dialog-'+width+'-'+theme+'.png',fullPage:true});
  await p.locator('#apply-study-options').click();
  const orders=[];
  for(let round=0;round<2;round++){
   if(round){await p.locator('#customize-study').click();await p.locator('#study-type').selectOption('true_false');await p.locator('#study-quantity').fill('8');await p.locator('#apply-study-options').click();}
   await p.locator('#start-study').click();await p.locator('#finish-study').waitFor();const s=(await state(p)).active;assert.equal(s.selection.shuffle,true);assert.equal(s.items.length,8);assert.equal(new Set(s.items.map(i=>i.question.id)).size,8);orders.push(s.items.map(i=>i.question.id));
   await p.reload();await p.locator('#start-study:not([disabled])').waitFor();await p.locator('#start-study').click();await p.locator('#finish-study').waitFor();assert.deepEqual((await state(p)).active.items,s.items);
   await p.locator('#finish-study').click();await p.locator('#confirm-finish').click();await p.locator('#new-session').click();
  }
  assert.notDeepEqual(orders[0],orders[1]);
  await p.locator('#rules-tab').click();const label=await p.locator('label[for="rules-objective"]').boundingBox(),select=await p.locator('#rules-objective').boundingBox();assert.ok(label.x+label.width<select.x);assert.ok(Math.abs(label.y+label.height/2-select.y-select.height/2)<2);
  for(const role of ['camara-comunicacao-divulgacao','abdi-comunicacao-marketing','cgu-auditoria']){
   await p.locator('#rules-objective').selectOption(role);assert.equal(await p.locator('#contest-logistics details').count(),1);await p.locator('#contest-logistics summary').click();assert.match(await p.locator('#contest-logistics').innerText(),/Conferido nos editais cadastrados/);assert.match(await p.locator('#contest-logistics').innerText(),role.startsWith('abdi')?/03\/12\/2026/:role.startsWith('cgu')?/02\/12\/2026/:/22\/12\/2026/);await p.locator('#contest-logistics summary').click();
   for(const font of ['', '200%']){await p.evaluate(v=>document.documentElement.style.fontSize=v,font);assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,role+' '+font);}
   await p.evaluate(()=>document.documentElement.style.fontSize='');
  }
  await p.screenshot({path:'/tmp/questionador-refinement/rules-'+width+'-'+theme+'.png',fullPage:true});assert.deepEqual(errors,[]);await context.close();console.log('Compact customization, X/cancel/Escape, conditional topics, automatic random draw/resume and compact rules passed:',width,theme);
 }
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
