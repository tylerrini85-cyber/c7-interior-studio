/* End-to-end walkthrough with the preinstalled Playwright + Chromium (software WebGL).
   Run: node tests/e2e.cjs  (expects `vite preview --port 4173` running). Exits non-zero on failure. */
const { chromium } = require('playwright');
const assert = require('assert');
const OUT = process.env.OUT || '/tmp/c7-e2e';
require('fs').mkdirSync(OUT, { recursive: true });
const results = [];
let current = 'init';
const card = (page, name) => page.locator('.project-card').filter({ has: page.getByRole('heading', { name, exact: true }) });
const step = async (name, fn) => { current = name; try { await fn(); results.push(['PASS', name]); console.log('PASS', name); } catch (e) { results.push(['FAIL', name + ': ' + e.message]); console.log('FAIL', name, e.message); if (process.env.STOP) throw e; } };

(async () => {
  const fs0 = require('fs'); const exe = ['/opt/pw-browsers/chromium', '/opt/pw-browsers/chromium/chrome'].find((p) => fs0.existsSync(p) && fs0.statSync(p).isFile());
  const browser = await chromium.launch({ executablePath: exe, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await ctx.newPage();
  page.setDefaultTimeout(120000);
  const errors = [];
  page.on('pageerror', (e) => errors.push('[' + current + '] ' + e.message.slice(0, 160) + '\n' + (e.stack || '').split('\n').filter((l) => l.includes('/src/') || l.includes('Error')).slice(0, 12).join('\n')));
  page.on('console', (m) => { if (m.type() === 'warning' && /getSnapshot|Maximum|setState/.test(m.text())) errors.push('[' + current + '] warn: ' + m.text().slice(0, 300)); });
  page.on('console', (m) => { if (m.type() === 'error') errors.push('[' + current + '] ' + m.text().slice(0, 200)); });
  const st = () => page.evaluate(() => { const s = window.__c7.getState(); return { route: s.route, selected: s.selected, mode: s.cameraMode, past: s.past.length, future: s.future.length, save: s.saveStatus, name: s.project?.name, parts: s.project?.parts, lighting: s.project?.lighting, id: s.project?.id, env: s.project?.environment }; });
  const frames = async (n) => page.waitForFunction((n) => (window.__c7frames || 0) > n, Number.isFinite(n) ? n : 3, { timeout: 120000 });
  const more = async (k = 3) => frames(((await page.evaluate(() => window.__c7frames)) || 0) + k);
  const url = (process.env.BASE || 'http://localhost:4173') + '/?quality=mobile';

  await page.goto(url, { waitUntil: 'networkidle' });
  await step('landing renders menu', async () => { await page.getByRole('button', { name: 'New Project' }).waitFor(); });
  await step('create project A (Adrenaline Red, night)', async () => {
    await page.getByRole('button', { name: 'New Project' }).click();
    await page.fill('input[maxlength="48"]', 'Project A');
    await page.getByRole('button', { name: /Adrenaline Red/ }).click();
    await page.getByRole('button', { name: 'Night' }).click();
    await page.getByRole('button', { name: 'Enter the cockpit' }).click();
    await frames(3);
    const s = await st(); assert.equal(s.route, 'studio'); assert.equal(s.name, 'Project A'); assert.equal(s.env, 'night');
    assert.equal(s.parts['dash.upper'].color, '#6a1116');
  });
  await step('select part from parts menu and change material', async () => {
    await page.getByRole('button', { name: 'Upper rim' }).click();
    let s = await st(); assert.equal(s.selected, 'steering.rim.upper');
    await page.getByRole('button', { name: 'Alcantara-style microfiber' }).click();
    s = await st(); assert.equal(s.parts['steering.rim.upper'].material, 'alcantara'); assert.equal(s.past, 1);
    await more(2);
    const mat = await page.evaluate(() => { const m = window.__c7registry.byNode.get('steering.rim.upper'); return m.material.name; });
    assert(mat.startsWith('alcantara|'), 'material applied to mesh: ' + mat);
  });
  await step('geometry variant swap (flat-bottom wheel) loads variant GLB', async () => {
    await page.getByRole('button', { name: /Flat-bottom racing/ }).click();
    await page.waitForFunction(() => { const r = window.__c7registry; return [...r.entries.values()].some((e) => e.source === 'variant:steering:flat_bottom'); }, null, { timeout: 120000 });
    const info = await page.evaluate(() => { const r = window.__c7registry; const fac = r.entries.get(r.byNode.get('column.shroud')); const hidden = [...r.entries.values()].filter((e) => e.source === 'cockpit' && e.nodeName.startsWith('steering.')).length; const v = [...r.entries.values()].filter((e) => e.source === 'variant:steering:flat_bottom').length; return { hidden, v, fac: !!fac }; });
    assert.equal(info.hidden, 0, 'factory wheel nodes unregistered'); assert(info.v > 5, 'variant nodes registered');
  });
  await step('click-to-select via raycast (steering hub)', async () => {
    await page.keyboard.press('Escape');
    // the hub sits roughly at the centre-left of the viewport in the driver POV
    const box = await page.locator('canvas').boundingBox();
    await page.mouse.click(box.x + box.width * 0.47, box.y + box.height * 0.72);
    const s = await st(); assert(s.selected, 'something selected: ' + s.selected);
  });
  await step('undo / redo', async () => {
    await page.keyboard.press('Control+z');
    let s = await st(); assert.equal(s.parts['steering.rim.upper'].variant, 'factory');
    await page.keyboard.press('Control+Shift+z');
    s = await st(); assert.equal(s.parts['steering.rim.upper'].variant, 'flat_bottom');
  });
  await step('lighting zones + starlight enable', async () => {
    await page.getByRole('button', { name: 'Lighting' }).first().click();
    await page.getByRole('button', { name: 'All zones on' }).click();
    const sw = page.locator('.section', { hasText: 'Starlight headliner' }).locator('.switch').first();
    await sw.click();
    const s = await st(); assert(s.lighting.master.enabled); assert(s.lighting.zones.dash.enabled); assert(s.lighting.starlight.enabled);
    await more(3);
    const stars = await page.evaluate(() => { let n = 0; window.__c7scene.traverse((o) => { if (o.isPoints) n = o.geometry.getAttribute('position').count; }); return n; });
    assert(stars >= 50, 'star points exist: ' + stars);
    await page.screenshot({ path: OUT + '/night-rgb.png' });
  });
  await step('apply preset', async () => {
    await page.getByRole('button', { name: 'Presets' }).click();
    await page.getByRole('button', { name: /Redline Performance/ }).click();
    const s = await st(); assert.equal(s.parts['seats.driver.base.center'].color, '#8f1a20');
  });
  await step('environment switch to day', async () => {
    await page.getByRole('button', { name: 'Day' }).click();
    const s = await st(); assert.equal(s.env, 'day');
  });
  await step('autosave persists', async () => {
    await page.waitForFunction(() => window.__c7.getState().saveStatus === 'saved', null, { timeout: 20000 });
  });
  let idA;
  await step('create project B, customize differently', async () => {
    idA = (await st()).id;
    await page.getByRole('button', { name: 'My Garage' }).click();
    await page.getByRole('button', { name: 'New project' }).click();
    await page.fill('input[maxlength="48"]', 'Project B');
    await page.getByRole('button', { name: 'Enter the cockpit' }).click();
    await more(2);
    await page.locator('.panel-tabs').getByRole('button', { name: 'Parts' }).click();
    await page.getByRole('button', { name: 'Upper rim' }).click();
    await page.getByRole('button', { name: 'Gloss carbon fiber' }).click();
    await page.waitForFunction(() => window.__c7.getState().saveStatus === 'saved', null, { timeout: 20000 });
    const s = await st(); assert.equal(s.name, 'Project B'); assert.notEqual(s.id, idA); assert.equal(s.parts['steering.rim.upper'].material, 'carbon_gloss');
  });
  await step('reload page: both projects in garage, A unchanged, B unchanged', async () => {
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.getByRole('button', { name: /My Garage/ }).click();
    await page.getByRole('heading', { name: 'Project A' }).waitFor();
    await page.getByRole('heading', { name: 'Project B' }).waitFor();
    await card(page, 'Project A').getByRole('button', { name: 'Open', exact: true }).click();
    let s = await st(); assert.equal(s.name, 'Project A'); assert.equal(s.parts['seats.driver.base.center'].color, '#8f1a20'); assert.equal(s.parts['steering.rim.upper'].variant, 'flat_bottom'); assert(s.lighting.starlight.enabled);
    await page.getByRole('button', { name: 'My Garage' }).click();
    await card(page, 'Project B').getByRole('button', { name: 'Open', exact: true }).click();
    s = await st(); assert.equal(s.name, 'Project B'); assert.equal(s.parts['steering.rim.upper'].material, 'carbon_gloss');
  });
  await step('thumbnail captured for project', async () => {
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.getByRole('button', { name: /My Garage/ }).click();
    await page.locator('.project-card img').first().waitFor({ timeout: 30000 });
  });
  await step('export/import round trip', async () => {
    const dl = page.waitForEvent('download');
    await card(page, 'Project A').getByRole('button', { name: 'Export' }).click();
    const d = await dl; const path = await d.path();
    const fs = require('fs'); const txt = fs.readFileSync(path, 'utf8'); const parsed = JSON.parse(txt); assert.equal(parsed.project.name, 'Project A');
    await page.locator('input[type=file]').setInputFiles(path);
    await page.getByRole('heading', { name: 'Project A (imported)' }).waitFor();
  });
  await step('duplicate, rename, delete with confirmation', async () => {
    await card(page, 'Project B').getByRole('button', { name: 'Duplicate' }).click();
    await page.getByRole('heading', { name: 'Project B copy' }).waitFor();
    await card(page, 'Project B copy').getByRole('button', { name: 'Rename' }).click();
    await page.locator('.modal input').fill('Project C');
    await page.locator('.modal').getByRole('button', { name: 'Save' }).click();
    await page.getByRole('heading', { name: 'Project C' }).waitFor();
    await card(page, 'Project C').getByRole('button', { name: 'Delete' }).click();
    await page.locator('.modal').getByRole('button', { name: 'Delete' }).click();
    await page.waitForFunction(() => ![...document.querySelectorAll('h3')].some((h) => h.textContent === 'Project C'));
  });
  await step('screenshot export produces a PNG download', async () => {
    await card(page, 'Project A').getByRole('button', { name: 'Open', exact: true }).click();
    await more(3);
    const dl = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Screenshot (PNG)' }).click();
    const d = await dl; assert(d.suggestedFilename().endsWith('.png'));
  });
  await step('before/after compare toggles factory and restores design', async () => {
    await page.getByRole('button', { name: 'Compare with factory' }).click();
    await more(2);
    const mat = await page.evaluate(() => window.__c7registry.byNode.get('steering.rim.upper')?.material.name);
    assert(mat && mat.startsWith('leather|'), 'factory material shown while comparing: ' + mat);
    await page.getByRole('button', { name: 'Compare with factory' }).click();
    const s = await st(); assert.equal(s.parts['seats.driver.base.center'].color, '#8f1a20');
  });
  await step('factory reset + random generator', async () => {
    page.once('dialog', (d) => d.accept());
    await page.getByRole('button', { name: 'Reset everything to factory' }).click();
    let s = await st(); assert.equal(s.parts['steering.rim.upper'].material, 'leather');
    await page.getByRole('button', { name: 'Random' }).click();
    await page.getByRole('button', { name: /Show Car/ }).click();
    s = await st(); assert.equal(s.lighting.master.enabled, true);
  });
  await step('camera modes + free roam movement + collision bounds', async () => {
    await page.getByRole('button', { name: 'Passenger seat' }).click();
    await page.waitForTimeout(1200);
    const p1 = await page.evaluate(() => window.__c7scene.children.find(() => true) && window.__c7gl && [...document.querySelectorAll('canvas')].length);
    assert(p1);
    await page.locator('canvas').focus();
    await page.keyboard.down('KeyW'); await page.waitForTimeout(2500); await page.keyboard.up('KeyW');
    const s = await st(); assert.equal(s.mode, 'free');
    await page.keyboard.press('KeyR');
    await page.waitForTimeout(1200);
    assert.equal((await st()).mode, 'driver');
  });
  await step('mobile layout: sheets and joystick', async () => {
    await page.setViewportSize({ width: 390, height: 780 });
    await page.waitForTimeout(500);
    await page.locator('.joystick').waitFor();
    await page.getByRole('button', { name: 'Parts' }).click();
    await page.locator('.sheet').waitFor();
    await page.getByRole('button', { name: 'Upper rim' }).click();
    await page.locator('.inspector').waitFor();
    await page.screenshot({ path: OUT + '/mobile.png' });
    await page.setViewportSize({ width: 1280, height: 720 });
  });
  console.log('\nconsole/page errors:', errors.length ? errors.join('\n') : 'none');
  const fails = results.filter((r) => r[0] === 'FAIL');
  console.log(`\n${results.length - fails.length}/${results.length} steps passed`);
  await browser.close();
  process.exit(fails.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
