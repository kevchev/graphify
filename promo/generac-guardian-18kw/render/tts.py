# Narration with Kokoro-82M via sherpa-onnx. Usage: KOKORO_DIR=<model dir> python3 tts.py <outdir>
import sys, os, json, numpy as np, soundfile as sf, sherpa_onnx
kd=os.environ["KOKORO_DIR"]; out=sys.argv[1]; os.makedirs(out,exist_ok=True)
here=os.path.dirname(os.path.abspath(__file__))
lines=json.load(open(f"{here}/../audio/narration-script.json"))
cfg=sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
    model=f"{kd}/model.onnx",voices=f"{kd}/voices.bin",tokens=f"{kd}/tokens.txt",data_dir=f"{kd}/espeak-ng-data"),num_threads=4,provider="cpu"),max_num_sentences=1)
tts=sherpa_onnx.OfflineTts(cfg); durs={}
for k,l in lines.items():
    a=tts.generate(l["say"],sid=6,speed=0.98); x=np.array(a.samples,dtype=np.float32)
    idx=np.where(np.abs(x)>0.01)[0]; x=x[max(0,idx[0]-1200):idx[-1]+2400]
    sf.write(f"{out}/{k}.wav",x,a.sample_rate); durs[k]=round(len(x)/a.sample_rate,2); print(k,durs[k])
json.dump(durs,open(f"{out}/durations.json","w"),indent=1)
