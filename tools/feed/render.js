const { chromium } = require('/home/claude/ig/node_modules/playwright-core');
const fs=require('fs');
(async()=>{const exe=['/opt/pw-browsers/chromium-1243/chrome-linux64/chrome','/opt/pw-browsers/chromium/chrome-linux/chrome','/opt/pw-browsers/chromium-1194/chrome-linux/chrome'].find(fs.existsSync);
const b=await chromium.launch({executablePath:exe}); const D='/home/claude/ig/redesign/html', P='/home/claude/ig/redesign/png';
for(const f of fs.readdirSync(D).sort()){const reel=f.startsWith('R_');
const p=await b.newPage({viewport:reel?{width:1080,height:1920}:{width:1160,height:1430}});
await p.goto('file://'+D+'/'+f); await p.evaluate(()=>document.fonts.ready);
const over=await p.evaluate(()=>{let m=0;document.querySelectorAll('.content,.slide').forEach(c=>{m=Math.max(m,c.scrollHeight-c.clientHeight)});const s=document.querySelector('.slide').getBoundingClientRect();document.querySelectorAll('.content *').forEach(e=>{const r=e.getBoundingClientRect();if(r.bottom>s.bottom-120||r.top<s.top+150)m=Math.max(m,1)});return m});
if(over>0)console.log('OVERFLOW',f,over);
await p.screenshot({path:P+'/'+f.replace('.html','.png'),clip:reel?{x:0,y:0,width:1080,height:1920}:{x:40,y:40,width:1080,height:1350}}); await p.close();}
await b.close();})();
