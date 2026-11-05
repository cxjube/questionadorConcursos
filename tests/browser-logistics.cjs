'use strict';
const {chromium}=require('playwright'),assert=require('node:assert/strict');
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/',key='questionador-concursos.progress.v1',prefs='questionador-concursos.preferences.v1';
const cases=[['camara-comunicacao-divulgacao','camara-2026','17/11/2026','17/01/2027','Cebraspe','Presencial'],['abdi-comunicacao-marketing','abdi-2026','10/11/2026','20/12/2026','FGV','On-line · telepresencial'],['cgu-auditoria','cgu-2026','04/11/2026','13/12/2026','Cebraspe','Presencial']];
const opportunities={
 'camara-comunicacao-divulgacao':['4','9','R$ 32.070,88'],
 'abdi-comunicacao-marketing':['1','8','R$ 16.034,70'],
 'cgu-auditoria':['20','81','R$ 20.000,00']
};
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/chromium',headless:true,args:['--no-sandbox']});try{
 for(const [width,theme] of [[320,'light'],[1280,'light'],[320,'dark'],[1280,'dark']]){
  const context=await browser.newContext({viewport:{width,height:1100},ignoreHTTPSErrors:base.startsWith('https:')});const p=await context.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(base);await p.locator('#start-study:not([disabled])').waitFor();await p.locator('[data-theme-choice="'+theme+'"]').click();
  const credits=await p.locator('.footer-credits').innerText();assert.match(credits,/João Calixto/);assert.match(credits,/Baseado no Questionador, de Miguel Muniz e Rubens Braz/);assert.equal(await p.getByRole('link',{name:'Ver o projeto no GitHub'}).getAttribute('href'),'https://github.com/cxjube/questionadorConcursos');
  const cards=await p.locator('.mode-card').evaluateAll(els=>els.map(e=>({width:e.getBoundingClientRect().width,padding:getComputedStyle(e).padding,border:getComputedStyle(e).borderRadius})));assert.deepEqual(cards[0],cards[1]);
  await p.screenshot({path:'/tmp/questionador-ux/landing-'+width+'-'+theme+'.png',fullPage:true});
  await p.locator('#rules-tab').click();
  for(const [role,contest,deadline,date,board,mode] of cases){
   await p.locator('#rules-objective').selectOption(role);assert.equal(await p.locator('#contest').inputValue(),contest);assert.equal(await p.locator('#role').inputValue(),role);assert.ok((await p.locator('[data-objective-select]').evaluateAll(els=>els.map(e=>e.value))).every(v=>v===role));
   const panel=p.locator('#contest-logistics'),text=await panel.innerText();assert.ok(text.includes(deadline));assert.ok(text.includes(date));assert.ok(text.includes('Banca organizadora: '+board));assert.ok(text.includes(mode));assert.match(text,/Horário de Brasília/);assert.equal(await panel.locator('.registration-card a').getAttribute('target'),'_blank');assert.match(await panel.locator('.registration-card a').getAttribute('href'),board==='FGV'?/^https:\/\/conhecimento.fgv.br\/concursos\/psabdi$/:/^https:\/\/www.cebraspe.org.br\/concursos\//);
   if(board==='FGV'){assert.match(text,/13h30 às 17h/);assert.match(text,/Teste de plataforma obrigatório/);await panel.locator('details').first().locator('summary').click();assert.match(await panel.innerText(),/03\/12\/2026/);assert.match(await panel.innerText(),/webcam/);}
   const opportunity=p.locator('#contest-opportunity');
   assert.deepEqual((await opportunity.locator('dd').allTextContents()).map(t=>t.replace(/\s/g,' ')),opportunities[role]);
   assert.equal(await opportunity.evaluate(e=>e.parentElement.lastElementChild===e),true);
   if(role==='cgu-auditoria') {
    assert.match(await opportunity.innerText(),/Distrito Federal/);
    assert.match(await opportunity.locator('dt').nth(1).innerText(),/Limite de aprovados \(inclui vagas imediatas\)/);
    assert.match(await opportunity.innerText(),/não uma quantidade separada de cadastro de reserva/);
   } else assert.equal(await opportunity.locator('dt').nth(1).innerText(),'Cadastro de reserva');
   await opportunity.locator('summary').click();
   assert.equal(await opportunity.locator('a').getAttribute('target'),'_blank');
   assert.match(await opportunity.locator('a').getAttribute('href'),/^https:\/\//);
   assert.match(await opportunity.innerText(),/05\/11\/2026/);
   for(const font of ['', '200%']){await p.evaluate(s=>document.documentElement.style.fontSize=s,font);assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,role+' '+width+' '+font);}
   await p.evaluate(()=>document.documentElement.style.fontSize='');
   await opportunity.screenshot({path:'/tmp/questionador-ux/opportunity-'+contest+'-'+width+'-'+theme+'.png'});
  }
  await p.screenshot({path:'/tmp/questionador-ux/rules-'+width+'-'+theme+'.png',fullPage:true});
  await p.locator('#program-tab').click();await p.locator('#program-objective').selectOption(cases[1][0]);assert.match(await p.locator('#program-summary').innerText(),/8 disciplinas · 97/);
  await p.locator('#consolidation-tab').click();assert.match(await p.locator('#official-watch-links').innerText(),/FGV/);assert.doesNotMatch(await p.locator('#official-watch-links').innerText(),/concurso da Câmara/);
  await p.locator('#notices-objective').selectOption(cases[0][0]);await p.locator('#sources-tab').click();await p.locator('#papers-objective').selectOption(cases[1][0]);
  await p.reload();await p.locator('#start-study:not([disabled])').waitFor();assert.equal(await p.locator('#role').inputValue(),cases[1][0]);
  await p.locator('#customize-study').click();await p.locator('#study-quantity').fill('2');await p.locator('#apply-study-options').click();await p.locator('#start-study').click();await p.locator('#apply-study-options').click();await p.locator('#finish-study').waitFor();
  const before=await p.evaluate(k=>JSON.parse(localStorage.getItem(k)).progress.active,key);assert.equal(before.roleId,cases[1][0]);
  await p.locator('#rules-tab').click();await p.locator('#rules-objective').selectOption(cases[2][0]);assert.deepEqual(await p.evaluate(k=>JSON.parse(localStorage.getItem(k)).progress.active,key),before);
  await p.reload();await p.locator('#start-study:not([disabled])').waitFor();assert.equal(await p.locator('#role').inputValue(),cases[2][0]);assert.equal(await p.evaluate(k=>JSON.parse(localStorage.getItem(k)).lastRoleId,prefs),cases[2][0]);
  await p.locator('#start-study').click();await p.locator('#finish-study').waitFor();assert.deepEqual(await p.evaluate(k=>JSON.parse(localStorage.getItem(k)).progress.active,key),before);
  await p.locator('#finish-study').click();await p.locator('#confirm-finish').click();await p.locator('#new-session').click();assert.equal(await p.locator('#role').inputValue(),cases[2][0]);assert.equal(await p.evaluate(k=>JSON.parse(localStorage.getItem(k)).progress.history.at(-1).roleId,key),cases[1][0]);
  await p.evaluate(k=>localStorage.removeItem(k),prefs);await p.reload();await p.locator('#start-study:not([disabled])').waitFor();assert.equal(await p.locator('#role').inputValue(),cases[1][0]);
  assert.deepEqual(errors,[]);await context.close();console.log('Logistics, synchronized objectives, persisted selection, active-session preservation, cards and footer passed:',width,theme);
 }
 // Invalid/stale preferences and blocked storage must not prevent startup.
 for(const blocked of [false,true]){
  const context=await browser.newContext({ignoreHTTPSErrors:base.startsWith('https:')});const p=await context.newPage();await p.addInitScript(({blocked,prefs})=>{if(blocked){Storage.prototype.setItem=()=>{throw Error('blocked');};Storage.prototype.getItem=()=>{throw Error('blocked');};}else localStorage.setItem(prefs,JSON.stringify({lastRoleId:'missing-role'}));},{blocked,prefs});await p.goto(base);await p.locator('#start-study:not([disabled])').waitFor();assert.equal(await p.locator('#contest').inputValue(),'camara-2026');await context.close();
 }
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
