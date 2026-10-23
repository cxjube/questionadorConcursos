const { chromium } = require('playwright');
const assert = require('node:assert/strict');
// Optional maintainer smoke test; requires local Playwright and a static HTTP server.
const base = process.env.APP_BASE_URL || 'http://127.0.0.1:8765/questionadorConcursos/';
(async () => {
 const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium', headless: true, args: ['--no-sandbox'] });
 const page = await browser.newPage();
 const errors = []; const external = [];
 page.on('pageerror', error => errors.push(error.message));
 page.on('request', request => { if (!request.url().startsWith(new URL(base).origin + '/') && !request.url().startsWith('file:')) external.push(request.url()); });
 for (const width of [320, 1280]) {
  await page.setViewportSize({width, height: 900});
  await page.goto(base);
  await page.waitForFunction(() => document.getElementById('notices').children.length === 3);
  assert.equal(await page.locator('#contest option').count(), 3);
  assert.equal(await page.locator('#role option').count(), 1);
  assert.equal(await page.locator('#notices li').count(), 3);
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
  for (const theme of ['dark', 'light']) {
   await page.locator(`[data-theme-choice="${theme}"]`).click();
   assert.equal(await page.locator('html').getAttribute('data-theme'), theme);
   assert.equal(await page.locator(`[data-theme-choice="${theme}"]`).getAttribute('aria-pressed'), 'true');
  }
  await page.selectOption('#contest', 'abdi-futuro');
  assert.equal(await page.locator('#role').isDisabled(), true);
  assert.match(await page.locator('#contest-status').innerText(), /futuro/);
  await page.selectOption('#contest', 'cgu-futuro');
  assert.equal(await page.locator('#role').isDisabled(), true);
  await page.selectOption('#contest', 'camara-2026');
  assert.equal(await page.locator('#notices li').count(), 3);
  await page.reload();
  assert.equal(await page.locator('html').getAttribute('data-theme'), 'light');
  await page.keyboard.press('Tab');
  assert.equal(await page.locator('a.skip-link').evaluate(el => el === document.activeElement), true);
 }
 assert.deepEqual(errors, []);
 assert.deepEqual(external, []);
 await browser.close();
 console.log('Browser smoke passed: 320/1280px, light/dark, selection, persisted theme, keyboard skip link, project subpath and zero external runtime requests.');
})().catch(error => { console.error(error); process.exit(1); });
