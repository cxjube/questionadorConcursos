'use strict';
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const base=process.env.APP_BASE_URL||'http://127.0.0.1:8000/';
async function reflow(page){for(const size of ['', '200%']){await page.evaluate(size=>document.documentElement.style.fontSize=size,size);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);}await page.evaluate(()=>document.documentElement.style.fontSize='');}
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try{for(const width of [320,1280]){
  const context=await browser.newContext({viewport:{width,height:960},ignoreHTTPSErrors:base.startsWith('https:')});const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
  for(const contest of ['camara-2026','abdi-2026','cgu-2026','abdi-2026','camara-2026']){
   await page.locator('#questionador-tab').click();await page.locator('#contest').selectOption(contest);
   const camara=contest==='camara-2026',abdi=contest==='abdi-2026',role=await page.locator('#role').inputValue();
   const expected=await page.evaluate(role=>{const d=window.CONCURSOS_CATALOG,pool=Study.pool(d,role,Study.empty()),ids=new Set(pool.map(q=>q.origin.paperId));return {pool:pool.length,documents:d.papers.filter(p=>ids.has(p.id)).map(p=>d.documents.find(x=>x.id===p.documentId).officialUrl).sort()};},role);
   assert.equal(expected.pool,camara?399:abdi?246:260);assert.equal(await page.locator('#start-study').isDisabled(),false);
   if(camara){const left=await page.locator('#customize-study').boundingBox(),right=await page.locator('#start-study').boundingBox();if(width===1280)assert.ok(left.x+left.width<=right.x);else assert.ok(left.y+left.height<=right.y);}
   await reflow(page);
   await page.locator('#program-tab').click();assert.match(await page.locator('#program-summary').innerText(),new RegExp(camara?'9 disciplinas · 228':abdi?'8 disciplinas · 97':'14 disciplinas · 266'));await reflow(page);
   await page.locator('#rules-tab').click();const rules=await page.locator('#rules').innerText();if(camara){assert.match(rules,/300 minutos/);assert.doesNotMatch(rules,/210 minutos/);}else if(abdi){assert.match(rules,/210 minutos/);assert.doesNotMatch(rules,/300 minutos/);}else {assert.match(rules,/300 minutos/);assert.match(rules,/78 pontos/);assert.match(rules,/Conhecimentos complementares/);};await reflow(page);
   await page.locator('#consolidation-tab').click();assert.equal(await page.locator('#official-watch-links li').count(),camara?4:3);const tags=await page.locator('#official-watch-links li').evaluateAll(els=>els.map(x=>x.dataset.contestId));assert.ok(tags.every(id=>id===contest||id==='all'));
   assert.equal(await page.locator('#camara-reference-details').isVisible(),camara);assert.equal(await page.locator('#role-reference-details').isVisible(),!camara);assert.equal(await page.locator('#role-reference-links a').count(),abdi?11:camara?0:6);
   assert.equal(await page.locator('#notices li').count(),camara?6:abdi?1:2);
   for(const details of ['#camara-reference-details','#role-reference-details'])if(await page.locator(details).isVisible())await page.locator(details+' summary').click();await reflow(page);
   await page.locator('#sources-tab').click();assert.equal(await page.locator('#inventory > li').count(),expected.documents.length);const links=await page.locator('#inventory').evaluateAll(els=>[...els[0].querySelectorAll('a')].filter(a=>a.textContent.includes('Caderno')).map(a=>a.href).sort());assert.deepEqual(links,expected.documents);await reflow(page);
  }
  await page.locator('#questionador-tab').click();await page.screenshot({path:'/tmp/abdi-batch1/objective-'+width+'.png',fullPage:true});assert.deepEqual(errors,[]);await context.close();console.log('Objective scope/reflow passed at',width);
 }}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
