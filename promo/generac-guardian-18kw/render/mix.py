# Soundtrack: processed narration + ducked CC0 music bed + two synthesized hits, normalized to -14 LUFS.
import json, subprocess, os
S=os.environ["SCRATCH"]; here=os.path.dirname(os.path.abspath(__file__))
cfg=json.load(open(f"{here}/mix.json")); dur=cfg["duration"]; vo=cfg["vo"]; music=f"{S}/music/{cfg['music']}"
out=f"{here}/../audio/soundtrack.wav"; inputs=[]; fl=[]
for i,(name,t0) in enumerate(vo):
    inputs+=["-i",f"{S}/gvo/{name}.wav"]; ms=int(t0*1000)
    fl.append(f"[{i}]aresample=48000,highpass=f=80,equalizer=f=3000:t=q:w=1.2:g=2,acompressor=threshold=-22dB:ratio=3.5:attack=4:release=120:makeup=3,adelay={ms}|{ms},apad=whole_dur={dur}[v{i}]")
n=len(vo); fl.append("".join(f"[v{i}]" for i in range(n))+f"amix=inputs={n}:duration=first:normalize=0,asplit=2[vo][vosc]")
inputs+=["-i",music]; off=cfg["music_offset"]
fl.append(f"[{n}]aresample=48000,atrim={off}:{dur+off},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1.5,afade=t=out:st={dur-3.5}:d=3.5,volume=0.9[mus]")
fl.append("[mus][vosc]sidechaincompress=threshold=0.05:ratio=4:attack=15:release=650:makeup=1:level_sc=1.3[musd]")
fl.append(f"[musd]volume={cfg['music_vol']}[musd2]")
# hits: a low thump when the lights come on (19.35 s) and a soft whoosh at the product reveal (23.5 s)
fl.append(f"aevalsrc='0.6*sin(2*PI*55*t)*exp(-t*6)+0.25*sin(2*PI*110*t)*exp(-t*9)':d=1.2:s=48000,adelay=19350|19350,apad=whole_dur={dur},volume=0.9[h1]")
fl.append(f"anoisesrc=d=0.8:c=pink:r=48000:a=0.5,afade=t=in:st=0:d=0.35,afade=t=out:st=0.35:d=0.45,lowpass=f=2600,highpass=f=300,adelay=23300|23300,apad=whole_dur={dur},volume=0.22,aformat=channel_layouts=stereo[h2]")
fl.append("[musd2][vo][h1][h2]amix=inputs=4:duration=first:normalize=0,alimiter=limit=0.95:attack=5:release=60,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
cmd=["ffmpeg","-y","-v","error"]+inputs+["-filter_complex",";".join(fl),"-map","[out]","-ar","48000","-ac","2","-c:a","pcm_s16le",out]
subprocess.run(cmd,check=True)
def lufs(f):
    r=subprocess.run(["ffmpeg","-i",f,"-af","ebur128","-f","null","-"],capture_output=True,text=True).stderr
    return float([l for l in r.splitlines() if "I:" in l and "LUFS" in l][-1].split("I:")[1].split("LUFS")[0])
# second pass: trim to exactly -14 LUFS integrated (single-pass loudnorm lands low on a mix this dynamic)
g=-14.0-lufs(out); tmp=out+".tmp.wav"; os.rename(out,tmp)
subprocess.run(["ffmpeg","-y","-v","error","-i",tmp,"-af",f"volume={g:.2f}dB,alimiter=limit=0.89:attack=5:release=80:level=false","-c:a","pcm_s16le",out],check=True); os.remove(tmp)
print(f"gain {g:+.2f} dB -> {lufs(out):.1f} LUFS, wrote {out}")
