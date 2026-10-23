const { chromium } = require('/home/claude/ig/node_modules/playwright-core');
const fs=require('fs');
(async()=>{const D=process.argv[2],P=process.argv[3];fs.mkdirSync(P,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1243/chrome-linux64/chrome'});
for(const f of fs.readdirSync(D).sort()){const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+D+'/'+f); await p.evaluate(()=>document.fonts.ready);
const o=await p.evaluate(()=>{const b=document.querySelector('.box');return b.scrollHeight-b.clientHeight});
if(o>0)console.log('OVERFLOW',f,o);
await p.screenshot({path:P+'/'+f.replace('.html','.png')});await p.close();}
await b.close();})();
