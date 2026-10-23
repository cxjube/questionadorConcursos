const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const base = process.env.APP_BASE_URL || 'http://127.0.0.1:8000/';
const key = 'questionador-concursos.progress.v1';
const mark = async (page,value) => {
 await page.locator('input[value="'+value+'"]').check();
 await page.waitForFunction(({key,value})=>JSON.parse(localStorage.getItem(key)).progress.active.answers.some(a=>String(a.value)===value),{key,value});
};
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox']});
 try {
  for(const width of [320,1280]) {
   const page=await browser.newPage({viewport:{width,height:1000}});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base);await page.locator('#start-study:not([disabled])').waitFor();
   assert.equal(await page.locator('#landing-history').isHidden(),true);
   await page.locator('#study-options summary').click();
   await page.locator('#study-discipline').selectOption('lingua-portuguesa');
   await page.locator('#study-topic').selectOption('lingua-portuguesa-1');
   await page.locator('#study-quantity').fill('2');await page.locator('#start-study').click();
   await page.locator('.source-lines').waitFor();
   assert.equal(await page.locator('.source-lines li').count(),26);
   assert.equal(await page.locator('.source-lines li').nth(14).getAttribute('value'),'15');
   assert.match(await page.locator('.source-lines li').nth(14).innerText(),/uma vez que não havia mais dúvidas/);
   assert.match(await page.locator('.source-credit').innerText(),/Adriana Falcão/);
   assert.equal(await page.locator('.didactic-comment').count(),0);
   assert.equal(await page.locator('.correction').count(),0);
   for(const theme of ['light','dark']) {
    await page.locator('[data-theme-choice="'+theme+'"]').click();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.locator('.question-context').screenshot({path:'/tmp/numbered-passage-'+width+'-'+theme+'.png'});
   }
   await mark(page,'false');await page.locator('#next-question').click();await mark(page,'true');
   await page.locator('#study-history').click();await page.locator('.performance-details > summary').click();
   assert.match(await page.locator('.performance-details').innerText(),/Finalize a sessão/);
   assert.equal(await page.locator('.performance-list').count(),0);
   await page.getByRole('button',{name:'Retomar sessão em andamento',exact:true}).click();
   await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.correction').waitFor();
   assert.equal(await page.locator('.didactic-comment h5').innerText(),'Comentário didático');
   assert.match(await page.locator('.didactic-comment').innerText(),/assistido por IA/);
   assert.match(await page.locator('.didactic-comment a').getAttribute('href'),/232FUNPRESPEXE_CB1_01/);
   await page.locator('.performance-details > summary').click();
   assert.match(await page.locator('.performance-details').innerText(),/2 questões distintas · 2 tentativas · 1 sessão finalizada/);
   assert.match(await page.locator('.performance-rate').first().innerText(),/50%/);
   await page.locator('.performance-list details > summary').click();
   assert.equal(await page.locator('.performance-topics > li').count(),1);
   assert.match(await page.locator('.performance-topics').innerText(),/Compreensão e interpretação/);
   await page.locator('#new-session').click();assert.equal(await page.locator('#landing-history').isVisible(),true);
   await page.locator('#landing-history').click();
   if(await page.locator('.performance-details').getAttribute('open')===null) await page.locator('.performance-details > summary').click();
   assert.match(await page.locator('.performance-rate').first().innerText(),/50%/);
   await page.getByRole('button',{name:'Revisar erros (1)',exact:true}).click();
   await mark(page,'false');await page.locator('#finish-study').click();await page.locator('#confirm-finish').click();await page.locator('.correction').waitFor();
   await page.locator('#study-history').click();
   assert.match(await page.locator('.performance-details').innerText(),/2 questões distintas · 3 tentativas · 2 sessões finalizadas/);
   assert.match(await page.locator('.performance-rate').first().innerText(),/67%/);
   assert.match(await page.locator('.performance-list').innerText(),/2 acertos · 1 erro · 0 brancos/);
   for(const theme of ['light','dark']) {
    await page.locator('[data-theme-choice="'+theme+'"]').click();
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
    await page.screenshot({path:'/tmp/performance-history-'+width+'-'+theme+'.png',fullPage:true});
   }
   await page.evaluate(()=>document.documentElement.style.fontSize='200%');
   assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
   await page.evaluate(()=>document.documentElement.style.fontSize='');
   await page.locator('#backup-tools > summary').click();
   const downloaded=page.waitForEvent('download');await page.getByRole('button',{name:'Exportar backup',exact:true}).click();
   const raw=await fs.readFile(await (await downloaded).path(),'utf8');
   const backup=JSON.parse(raw);assert.equal(backup.progress.history.length,2);
   assert.equal(backup.progress.history[0].items[0].contexts[0].sourceLines.length,26);
   assert.equal(backup.progress.history[0].items[0].explanations.length,1);
   await page.reload();await page.locator('#landing-history').click();await page.locator('.performance-details > summary').click();
   assert.match(await page.locator('.performance-rate').first().innerText(),/67%/);
   assert.deepEqual(errors,[]);await page.close();
  }
 } finally {await browser.close();}
 console.log('Performance passed: numbered original lines and credit, no correction before finish, editorial comments with source, session and historical rates, repeated attempts vs distinct questions, drafts excluded, local backup/reload, keyboard-ready disclosures and light/dark 320/1280px with 200% text.');
})().catch(e=>{console.error(e);process.exit(1);});
