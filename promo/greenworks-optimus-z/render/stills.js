// Render one still per listed time for review: node stills.js composition.html outdir t1 t2 ...
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const path=require('path'), fs=require('fs');
(async()=>{const [,,comp,outdir,...ts]=process.argv; fs.mkdirSync(outdir,{recursive:true});
 const b=await chromium.launch({args:['--disable-gpu','--font-render-hinting=none','--force-color-profile=srgb']}); const p=await b.newPage({viewport:{width:1920,height:1080}});
 p.on('pageerror',e=>console.error('PAGE ERROR',e.message));
 await p.goto('file://'+path.resolve(comp),{waitUntil:'load'}); await p.evaluate(()=>window.ready);
 await p.evaluate(async()=>{await Promise.all(Array.from(document.images).filter(i=>!i.complete).map(i=>new Promise(r=>{i.onload=r;i.onerror=r;})));});
 for(const t of ts){await p.evaluate(t=>window.seek(t),+t); await p.screenshot({path:path.join(outdir,`t${(+t).toFixed(2)}.png`)});}
 await b.close(); console.log('ok');})();
