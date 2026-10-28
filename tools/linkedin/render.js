const { chromium } = require('/home/claude/ig/node_modules/playwright-core');
const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1243/chrome-linux64/chrome'});
const D='/home/claude/ig/li/html',P='/home/claude/ig/li/png';
for(const f of fs.readdirSync(D).sort()){const p=await b.newPage({viewport:{width:1160,height:1430}});
await p.goto('file://'+D+'/'+f); await p.evaluate(()=>document.fonts.ready);
const o=await p.evaluate(()=>{const c=document.querySelector('.content');const ft=document.querySelector('.foot').getBoundingClientRect();const cr=c.getBoundingClientRect();let m=c.scrollHeight-c.clientHeight;let bot=0;c.querySelectorAll('*').forEach(e=>{bot=Math.max(bot,e.getBoundingClientRect().bottom)});return {m,gap:ft.top-bot,top:[...c.children][0].getBoundingClientRect().top-document.querySelector('.top').getBoundingClientRect().bottom}});
console.log(f,JSON.stringify(o));
await p.screenshot({path:P+'/'+f.replace('.html','.png'),clip:{x:40,y:40,width:1080,height:1350}});await p.close();}
await b.close();})();
