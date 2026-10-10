# Build the final soundtrack: processed narration + ducked CC0 music bed, loudness-normalized.
import json, subprocess, sys, re, os
S=os.environ.get("SCRATCH"); here=os.path.dirname(os.path.abspath(__file__))
cfg=json.load(open(f"{here}/mix.json")); dur=cfg["duration"]
vo=cfg["vo"]; music=f"{S}/music/{cfg['music']}"
out=f"{here}/../audio/soundtrack.wav"
inputs=[]; fl=[]
for i,(name,t0) in enumerate(vo):
    inputs+=["-i",f"{S}/vo/{name}.wav"]
    ms=int(t0*1000)
    fl.append(f"[{i}]aresample=48000,highpass=f=75,equalizer=f=3200:t=q:w=1.2:g=2,acompressor=threshold=-22dB:ratio=3.5:attack=4:release=120:makeup=3,adelay={ms}|{ms},apad=whole_dur={dur}[v{i}]")
n=len(vo)
fl.append("".join(f"[v{i}]" for i in range(n))+f"amix=inputs={n}:duration=first:normalize=0,volume=1.0,asplit=2[vo][vosc]")
inputs+=["-i",music]
fl.append(f"[{n}]aresample=48000,atrim=4.4:{dur+4.4},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1.2,afade=t=out:st={dur-4.0}:d=4.0,volume=0.9[mus]")
fl.append("[mus][vosc]sidechaincompress=threshold=0.045:ratio=4.5:attack=12:release=700:makeup=1:level_sc=1.4[musd]")
fl.append("[musd]volume=0.5[musd2]")
fl.append("[musd2][vo]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95:attack=5:release=60,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
cmd=["ffmpeg","-y","-v","error"]+inputs+["-filter_complex",";".join(fl),"-map","[out]","-ar","48000","-ac","2","-c:a","pcm_s16le",out]
subprocess.run(cmd,check=True)
# report levels
r=subprocess.run(["ffmpeg","-i",out,"-af","volumedetect,ebur128","-f","null","-"],capture_output=True,text=True).stderr
print("\n".join(l for l in r.splitlines() if "mean_volume" in l or "max_volume" in l or "I:" in l and "LUFS" in l)[:600])
print("wrote",out)
