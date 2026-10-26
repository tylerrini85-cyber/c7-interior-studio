/* Captures the ten reference views required by the spec (docs/renders-web/*.png) from the running app.
   Run: PW_MODULE=<playwright> Q=high node tests/render-views.cjs  (expects vite preview on :4173). */
const { chromium } = require(process.env.PW_MODULE || 'playwright');
const fs = require('fs');
const OUT = process.env.OUT || 'docs/renders-web';
fs.mkdirSync(OUT, { recursive: true });
// three.js coords: x right, y up, z toward the rear. yaw 0 looks toward -z (forward); positive yaw turns left.
const VIEWS = {
  '01-driver-pov': { pos: [-0.37, 0.92, 0.12], yaw: 0, pitch: -0.12, fov: 75 },
  '02-passenger-pov': { pos: [0.37, 0.92, 0.12], yaw: 0, pitch: -0.12, fov: 75 },
  '03-dash-front': { pos: [0.0, 0.95, 0.45], yaw: 0, pitch: -0.18, fov: 70 },
  '04-wheel-closeup': { pos: [-0.37, 0.80, 0.0], yaw: 0, pitch: -0.25, fov: 50 },
  '05-center-console': { pos: [0.0, 1.0, 0.35], yaw: 0, pitch: -0.75, fov: 65 },
  '06-driver-seat': { pos: [0.5, 0.95, -0.05], yaw: 1.25, pitch: -0.45, fov: 65 },
  '07-passenger-seat': { pos: [-0.5, 0.95, -0.05], yaw: -1.25, pitch: -0.45, fov: 65 },
  '08-door-panel': { pos: [-0.05, 0.75, -0.05], yaw: 1.45, pitch: -0.15, fov: 75 },
  '09-headliner': { pos: [-0.2, 0.85, 0.0], yaw: 0, pitch: 1.25, fov: 85 },
  '10-rear-view': { pos: [-0.2, 0.92, -0.1], yaw: Math.PI, pitch: -0.1, fov: 85 },
};
(async () => {
  const q = process.env.Q || 'high';
  const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  page.setDefaultTimeout(240000);
  await page.goto('http://localhost:4173/?quality=' + q, { waitUntil: 'networkidle' });
  await page.getByRole('button', { name: 'New Project' }).click();
  if (process.env.ENV) await page.getByRole('button', { name: process.env.ENV }).click();
  await page.getByRole('button', { name: 'Enter the cockpit' }).click();
  await page.waitForFunction(() => (window.__c7frames || 0) > 3, null, { timeout: 240000 });
  if (process.env.PRESET) { await page.getByRole('button', { name: 'Presets' }).click(); await page.getByRole('button', { name: new RegExp(process.env.PRESET) }).click(); }
  await page.keyboard.press('KeyH');
  for (const [name, v] of Object.entries(VIEWS)) {
    await page.evaluate((v) => window.__c7cam.set(v.pos, v.yaw, v.pitch, v.fov), v);
    const f = await page.evaluate(() => window.__c7frames);
    await page.waitForFunction((f) => window.__c7frames > f + 3, f, { timeout: 240000 });
    await page.screenshot({ path: `${OUT}/${name}.png`, timeout: 240000 });
    console.log('captured', name);
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
