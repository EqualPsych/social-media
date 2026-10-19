# usage: mux.py vo.mp3 bed.mp3 out.mp4 endcard_secs frame1.png ... frameN.png  (last png = end card)
import sys,subprocess,re
vo,bed,out,endd=sys.argv[1],sys.argv[2],sys.argv[3],float(sys.argv[4]); fr=sys.argv[5:]
n=len(fr)-1; LEAD=0.3
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',vo]))
log=subprocess.run(['ffmpeg','-i',vo,'-af','silencedetect=n=-35dB:d=0.3','-f','null','-'],capture_output=True,text=True).stderr
st=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',log)]; en=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',log)]
gaps=sorted([(e-s,(s+e)/2) for s,e in zip(st,en) if e<dur-0.2 and s>0.2],reverse=True)[:n-1]
import os
cuts=[float(x) for x in os.environ['CUTS'].split(',')] if os.environ.get('CUTS') else sorted(m for _,m in gaps)
assert len(cuts)==n-1, (cuts,n)
b=[0]+[c+LEAD for c in cuts]+[dur+LEAD+0.6]
lst=''.join(f"file '{f}'\nduration {b[i+1]-b[i]:.3f}\n" for i,f in enumerate(fr[:-1]))+f"file '{fr[-1]}'\nduration {endd}\nfile '{fr[-1]}'\n"
open(out+'.txt','w').write(lst); total=b[-1]+endd
print('cuts',[round(x,2) for x in b],'total',round(total,2))
fc=(f"[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},aresample=44100,aformat=channel_layouts=stereo,apad,asplit=2[vo][sc];"
    f"[2:a]aresample=44100,aformat=channel_layouts=stereo,aloop=loop=-1:size=2e9,volume=-14dB,afade=t=in:d=1.5,afade=t=out:st={total-2.4:.2f}:d=2.4[m];"
    "[m][sc]sidechaincompress=threshold=0.03:ratio=4:attack=50:release=600[md];[vo][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-15:TP=-1.5[a]")
subprocess.run(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',out+'.txt','-i',vo,'-i',bed,'-filter_complex',fc,
 '-map','0:v','-map','[a]','-vf','fps=30,format=yuv420p','-c:v','libx264','-profile:v','high','-crf','20','-c:a','aac','-b:a','160k',
 '-t',f'{total:.2f}','-movflags','+faststart',out],check=True)
