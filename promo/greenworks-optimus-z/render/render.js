// Deterministic frame renderer: loads composition.html, calls window.seek(t) per frame, screenshots.
// Usage: node render.js <composition.html> <outdir> <fps> <duration_s> [start_frame] [end_frame]
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const path = require('path'); const fs = require('fs');
(async () => {
  const [,, comp, outdir, fpsS, durS, sfS, efS] = process.argv;
  const fps = +fpsS, dur = +durS; const total = Math.round(fps * dur);
  const sf = sfS ? +sfS : 0, ef = efS ? +efS : total;
  fs.mkdirSync(outdir, { recursive: true });
  const browser = await chromium.launch({ args: ['--disable-gpu', '--font-render-hinting=none', '--force-color-profile=srgb', '--disable-lcd-text'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => { console.error('PAGE ERROR', e.message); });
  page.on('console', m => { if (m.type() === 'error') console.error('CONSOLE', m.text()); });
  await page.goto('file://' + path.resolve(comp), { waitUntil: 'load' });
  await page.evaluate(() => window.ready);
  await page.evaluate(async () => { await Promise.all(Array.from(document.images).filter(i => !i.complete).map(i => new Promise(r => { i.onload = r; i.onerror = r; }))); });
  const t0 = Date.now();
  for (let f = sf; f < ef; f++) {
    await page.evaluate(t => window.seek(t), f / fps);
    await page.screenshot({ path: path.join(outdir, `f${String(f).padStart(5, '0')}.png`), type: 'png' });
    if ((f - sf) % 100 === 0) console.log(`frame ${f}/${total} ${(Date.now() - t0) / 1000}s`);
  }
  await browser.close();
  console.log('done', ef - sf, 'frames in', (Date.now() - t0) / 1000, 's');
})();
