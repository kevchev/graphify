#!/usr/bin/env python3
"""Assemble the @ChevStats "Every Malik Nabers target, Week 5" videos.

Inputs
  overlays/            title/end cards, counter_01..20, donut_target_share, weekly_targets (from the pack)
  clips.json           {"targets":[{"n":1,"file":"clips/t01.mp4","in":0.0,"out":4.0}, ...]}
                       `file` is your screen recording; `in`/`out` are optional trim points (seconds).
                       One long recording with 20 in/out pairs works too.
Cuts
  x        16:9, ~60 s, every target with the counter, donut + weekly cards, narration + captions
  youtube  16:9, full-length clips, three narrated pauses
  shortA   9:16, the game-tying TD (target 15)
  shortB   9:16, all 11 catches, rapid cuts
Usage
  python3 assemble.py --cut all --clips clips.json --out output
  python3 assemble.py --cut x --placeholders        # preview with generated stand-in footage
Environment
  KOKORO_DIR  path to kokoro-en-v0_19 (for narration); MUSIC  path to a music file (optional)
"""
import argparse, json, os, subprocess, sys, shutil, hashlib
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OV = os.path.join(HERE, "overlays"); FONTS = os.path.join(HERE, "fonts")
BG, PANEL, INK, SUB, HOT, COOL, MUTED = "#0D1320", "#111A2B", "#F3F5F9", "#A9B3C7", "#FF6A1F", "#3FB8F5", "#56627A"
FPS = 30

# ---- play list (quarter, clock, result, yards) straight from the pack's shot list ----
PLAYS = [
 (1,"Q1","7:55","Winston short right to Nabers",7,True,False),(2,"Q1","2:35","Deep left to Nabers",20,True,False),
 (3,"Q2","0:24","Incomplete short left (hit his hands)",0,False,False),(4,"Q2","0:20","Incomplete deep right",0,False,False),
 (5,"Q3","6:45","Incomplete short middle",0,False,False),(6,"Q3","4:09","Short right, out of bounds at WAS 11",6,True,False),
 (7,"Q3","1:36","Incomplete short middle",0,False,False),(8,"Q4","9:30","Short right",12,True,False),
 (9,"Q4","8:15","Incomplete deep left",0,False,False),(10,"Q4","4:25","Short right",6,True,False),
 (11,"Q4","3:56","Short right",3,True,False),(12,"Q4","3:25","Incomplete deep right",0,False,False),
 (13,"Q4","3:18","Short left",16,True,False),(14,"Q4","2:00","Incomplete deep right",0,False,False),
 (15,"Q4","1:48","Deep middle, 17-yard touchdown. Ties the game.",17,True,True),(16,"OT","9:27","Incomplete short left",0,False,False),
 (17,"OT","9:24","Incomplete short right",0,False,False),(18,"OT","5:29","Short middle",8,True,False),
 (19,"OT","4:40","Deep middle",28,True,False),(20,"OT","4:01","Short right",-2,True,False),
]
CATCHES = [p[0] for p in PLAYS if p[5]]

# ---- narration (X cut lines are verbatim from script.md; YouTube pause lines expand its bullet notes) ----
VO = {
 "x_intro":  "Malik Nabers saw twenty targets on Sunday. Here's every one.",
 "x_t1":     "It started normal. Two early catches.",
 "x_t3":     "Then a pile of misses, including two deep balls that hit his hands before half.",
 "x_donut":  "By the end he had thirty-eight and a half percent of the Giants' targets, and almost half their air yards.",
 "x_t8":     "Thirteen of the twenty came in the fourth quarter or overtime, capped by the seventeen-yard touchdown that tied it.",
 "x_t16":    "And they kept feeding him in overtime.",
 "x_end":    "Career high. Most targets by a Giant since Odell in twenty-sixteen. Next up: the Saints.",
 "yt_intro": "Malik Nabers saw twenty targets against the Commanders on Sunday, a career high. Here is every single one of them, in order, with the count on screen.",
 "yt_donut": "Let's pause here. Seven targets in, and the Giants are already leaning on one receiver. By the end of the night it was twenty of fifty-two targets, thirty-eight and a half percent, plus two hundred forty-five of the team's five hundred eight air yards. Isaiah Likely was next with thirteen.",
 "yt_td":    "That was target fifteen: the seventeen-yard touchdown that tied the game. Thirteen of his twenty targets came in the fourth quarter or overtime. When the Giants needed a play, there was only one place the ball was going.",
 "yt_weekly":"Twenty targets is a career high, up from eighteen, and the most by any Giant since Odell Beckham in December twenty-sixteen. Three quiet games to open the year, ninety-six scoreless yards. Then two hundred thirty-three yards and two touchdowns over the last two. For fantasy, he is a locked-in W R one in Week six at home against the Saints.",
}
CAPTION = {
 "x_intro":"Malik Nabers saw 20 targets on Sunday. Here's every one.", "x_t1":"It started normal. Two early catches.",
 "x_t3":"Then a pile of misses, including two deep balls that hit his hands before half.",
 "x_donut":"38.5% of the Giants' targets · almost half their air yards",
 "x_t8":"13 of the 20 came in the 4th quarter or OT, capped by the 17-yd TD that tied it.",
 "x_t16":"And they kept feeding him in overtime.", "x_end":"Career high. Most by a Giant since Odell in 2016. Next: the Saints.",
 "shortA":"Target 15 of 20 tied the game.", "shortB":"All 11 catches · 121 yards · 1 TD",
}

def run(cmd, quiet=True):
    r = subprocess.run(cmd, capture_output=quiet, text=True)
    if r.returncode: print(" ".join(cmd)); print(r.stderr[-3000:]); sys.exit(1)
    return r
def probe(f):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type","-of","json",f],capture_output=True,text=True)
    j = json.loads(r.stdout or "{}"); has_a = any(s.get("codec_type")=="audio" for s in j.get("streams",[]))
    return float(j.get("format",{}).get("duration",0) or 0), has_a
def font(name, size): return ImageFont.truetype(os.path.join(FONTS, name+".ttf"), size)

# ---- generated PNGs ----
def caption_png(text, aspect, work):
    key = hashlib.md5((text+aspect).encode()).hexdigest()[:10]; out = os.path.join(work, f"cap_{key}.png")
    if os.path.exists(out): return out
    W, H = (1920,1080) if aspect=="16x9" else (1080,1920)
    im = Image.new("RGBA",(W,H),(0,0,0,0)); d = ImageDraw.Draw(im)
    fs = 46 if aspect=="16x9" else 44; ft = font("Barlow-600", fs); maxw = (W-240) if aspect=="16x9" else (W-120)
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur+" "+w).strip()
        if d.textlength(t, font=ft) > maxw and cur: lines.append(cur); cur = w
        else: cur = t
    lines.append(cur); lh = int(fs*1.28); bh = lh*len(lines)+44; bw = max(d.textlength(l,font=ft) for l in lines)+80
    y0 = 60 if aspect=="16x9" else 470; x0 = (W-bw)/2
    d.rounded_rectangle((x0,y0,x0+bw,y0+bh),16,fill=(13,19,32,225),outline=(31,42,63,255),width=2)
    d.rectangle((x0,y0+14,x0+8,y0+bh-14),fill=HOT)
    for i,l in enumerate(lines): d.text((W/2,y0+22+i*lh+lh/2),l,font=ft,fill=INK,anchor="mm")
    im.save(out); return out

def placeholder_png(n, work):
    out = os.path.join(work, f"ph_{n:02d}.png")
    if os.path.exists(out): return out
    _, q, clk, desc, yds, catch, td = PLAYS[n-1]
    im = Image.new("RGB",(1920,1080),"#0F2415"); d = ImageDraw.Draw(im)
    for y in range(0,1080,6): d.line((0,y,1920,y),fill="#0C1F12")             # faint scanlines
    for x in range(160,1920,160): d.line((x,0,x,1080),fill="#1D3A26",width=3)  # yard lines
    for x in range(160,1920,160): d.text((x+14,30),f"{abs(50-(x//160)*10) or 50}",font=font("BarlowCondensed-700",40),fill="#2E5538")
    d.rounded_rectangle((520,300,1400,560),24,fill=(13,19,32,235),outline="#1F2A3F",width=3)
    d.text((960,345),"FOOTAGE PLACEHOLDER",font=font("BarlowCondensed-700",34),fill=SUB,anchor="mm")
    d.text((960,410),f"{q}  {clk}",font=font("BarlowCondensed-800",70),fill=INK,anchor="mm")
    res = "TOUCHDOWN" if td else ("CATCH" if catch else "INCOMPLETE")
    d.text((960,480),f"{res}{f'  {yds:+d} yds' if catch else ''}",font=font("BarlowCondensed-800",54),fill=HOT if td else (COOL if catch else SUB),anchor="mm")
    d.text((960,530),desc,font=font("Barlow-500",30),fill=SUB,anchor="mm")
    d.text((960,620),"Drop in your screen-recorded clip for this target",font=font("Barlow-500",28),fill="#6F7C95",anchor="mm")
    im.save(out); return out

# ---- segment builders (every segment: same codec params so concat is clean) ----
ENC = ["-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p","-r",str(FPS),"-c:a","aac","-ar","48000","-ac","2","-b:a","160k"]
def vid_layout(aspect):
    if aspect=="16x9": return "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=#0D1320,setsar=1"
    # 9:16: clip letterboxed at 1080 wide in the middle of a 1080x1920 navy canvas
    return "scale=1080:608:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:656:color=#0D1320,setsar=1"

def ov_place(png, aspect):
    """Return (scale filter prefix, y) for an overlay PNG on the given canvas."""
    if aspect == "16x9": return "", "0"
    w, h = Image.open(png).size
    if h == 1920: return "", "0"                     # already a 9:16 full-frame overlay (captions, cards)
    # 16:9 lower-third counter on a 9:16 canvas: enlarge so the box fills the width, park it under the clip
    return "scale=1900:-1,crop=1080:ih:0:0,", "519"

def seg_from_clip(src, tin, dur, overlays, out, aspect, clip_gain=1.0):
    d_src, has_a = probe(src)
    cmd = ["ffmpeg","-y","-v","error"]
    if tin: cmd += ["-ss",f"{tin:.3f}"]
    cmd += ["-t",f"{dur:.3f}","-i",src]
    for o in overlays: cmd += ["-framerate",str(FPS),"-loop","1","-t",f"{dur:.3f}","-i",o]
    fl = [f"[0:v]{vid_layout(aspect)},fps={FPS}[v0]"]; last="v0"
    for i,o in enumerate(overlays,1):
        oscale, y = ov_place(o, aspect)
        fl.append(f"[{i}:v]{oscale}format=rgba[o{i}]")
        fl.append(f"[{last}][o{i}]overlay=0:{y}:shortest=1[v{i}]"); last=f"v{i}"
    fl.append(f"[{last}]tpad=stop_mode=clone:stop_duration={dur:.3f},trim=0:{dur:.3f},setpts=PTS-STARTPTS[vout]")
    if has_a: fl.append(f"[0:a]volume={clip_gain},apad=whole_dur={dur:.3f},atrim=0:{dur:.3f},asetpts=PTS-STARTPTS[aout]")
    else: fl.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{dur:.3f}[aout]")
    run(cmd+["-filter_complex",";".join(fl),"-map","[vout]","-map","[aout]","-t",f"{dur:.3f}"]+ENC+[out])

def seg_from_still(png, dur, overlays, out, aspect, fade_in=0, fade_out=0, zoom=False):
    cmd = ["ffmpeg","-y","-v","error","-framerate",str(FPS),"-loop","1","-t",f"{dur:.3f}","-i",png]
    for o in overlays: cmd += ["-framerate",str(FPS),"-loop","1","-t",f"{dur:.3f}","-i",o]
    base = vid_layout(aspect) if aspect=="16x9" else "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=#0D1320,setsar=1"
    if zoom: base += f",zoompan=z='min(1.0+0.00035*in,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={'1920x1080' if aspect=='16x9' else '1080x1920'}:fps={FPS}"
    fl = [f"[0:v]{base},fps={FPS}[v0]"]; last="v0"
    for i,o in enumerate(overlays,1):
        oscale, y = ov_place(o, aspect)
        fl.append(f"[{i}:v]{oscale}format=rgba[o{i}]")
        fl.append(f"[{last}][o{i}]overlay=0:{y}:shortest=1[v{i}]"); last=f"v{i}"
    fades = (f",fade=t=in:st=0:d={fade_in}" if fade_in else "") + (f",fade=t=out:st={dur-fade_out:.2f}:d={fade_out}" if fade_out else "")
    fl.append(f"[{last}]trim=0:{dur:.3f},setpts=PTS-STARTPTS{fades}[vout]")
    fl.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{dur:.3f}[aout]")
    run(cmd+["-filter_complex",";".join(fl),"-map","[vout]","-map","[aout]","-t",f"{dur:.3f}"]+ENC+[out])

def last_frame(seg, out):
    run(["ffmpeg","-y","-v","error","-sseof","-0.15","-i",seg,"-frames:v","1","-update","1",out])

# ---- narration ----
_tts = None
def tts(key, text, work):
    out = os.path.join(work, f"vo_{key}.wav")
    if os.path.exists(out): return out
    global _tts
    kd = os.environ.get("KOKORO_DIR")
    if not kd: return None
    if _tts is None:
        import sherpa_onnx
        cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
            model=f"{kd}/model.onnx", voices=f"{kd}/voices.bin", tokens=f"{kd}/tokens.txt", data_dir=f"{kd}/espeak-ng-data"), num_threads=4, provider="cpu"), max_num_sentences=1)
        _tts = sherpa_onnx.OfflineTts(cfg)
    import numpy as np, soundfile as sf
    a = _tts.generate(text, sid=6, speed=1.02); x = np.array(a.samples, dtype=np.float32)
    idx = np.where(np.abs(x) > 0.01)[0]; x = x[max(0, idx[0]-1200): idx[-1]+2400]
    sf.write(out, x, a.sample_rate); return out
def wav_dur(f): return probe(f)[0]

# ---- timeline → video ----
def build(cut, clips, outdir, work, placeholders, music, no_vo):
    aspect = "9x16" if cut.startswith("short") else "16x9"
    T = lambda n: clips[n]  # (file, in, out)
    segs, vo_events, t = [], [], 0.0
    def add(path, dur, vo=None):
        nonlocal t
        if vo and not no_vo: vo_events.append((t, vo))
        segs.append(path); t += dur
    def clip_seg(n, dur, caption=None, gain=0.25):
        f, tin, tout = T(n); dur = min(dur, (tout - tin)) if tout else dur
        ovs = [os.path.join(OV, f"counter_{n:02d}.png")] + ([caption_png(caption, aspect, work)] if caption else [])
        p = os.path.join(work, f"{cut}_t{n:02d}.mp4"); seg_from_clip(f, tin, dur, ovs, p, aspect, gain); return p, dur
    def freeze_seg(n, used, name, dur, overlay, caption=None):
        # grab a clean frame near the end of the portion of target n that was shown, keep its counter, add the card
        f, tin, tout = T(n); at = min(max(tin, tin + used - 0.3), max(0.0, probe(f)[0] - 0.5))
        png = os.path.join(work, f"{cut}_{name}_frame.png")
        run(["ffmpeg","-y","-v","error","-ss",f"{at:.3f}","-i",f,"-frames:v","1","-update","1",png])
        ovs = [os.path.join(OV, f"counter_{n:02d}.png"), os.path.join(OV, overlay)] + ([caption_png(caption, aspect, work)] if caption else [])
        p = os.path.join(work, f"{cut}_{name}.mp4"); seg_from_still(png, dur, ovs, p, aspect); return p
    def card_seg(name, png, dur, fi=0.4, fo=0.4, zoom=True):
        p = os.path.join(work, f"{cut}_{name}.mp4"); seg_from_still(os.path.join(OV, png), dur, [], p, aspect, fi, fo, zoom); return p

    if cut == "x":
        add(card_seg("title", "title_16x9.png", 3.2, 0.5, 0.2), 3.2, "x_intro")
        for n in (1, 2): p, d = clip_seg(n, 3.5, CAPTION["x_t1"]); add(p, d, "x_t1" if n == 1 else None)
        for n in range(3, 8): p, d = clip_seg(n, 1.6, CAPTION["x_t3"]); add(p, d, "x_t3" if n == 3 else None)
        add(freeze_seg(7, 1.6, "donut", 6.0, "donut_target_share.png", CAPTION["x_donut"]), 6.0, "x_donut")
        for n in range(8, 15): p, d = clip_seg(n, 2.0, CAPTION["x_t8"]); add(p, d, "x_t8" if n == 8 else None)
        p, d = clip_seg(15, 4.5, CAPTION["x_t8"]); add(p, d)
        for n in range(16, 21): p, d = clip_seg(n, 2.0, CAPTION["x_t16"]); add(p, d, "x_t16" if n == 16 else None)
        add(freeze_seg(20, 2.0, "weekly", 4.5, "weekly_targets.png", CAPTION["x_end"]), 4.5, "x_end")
        add(card_seg("end", "end_16x9.png", 4.5, 0.3, 0.8), 4.5)
    elif cut == "youtube":
        add(card_seg("title", "title_16x9.png", 4.0, 0.5, 0.3), 4.0, "yt_intro")
        for n in range(1, 21):
            f, tin, tout = T(n); dur = (tout - tin) if tout else max(2.0, probe(f)[0] - tin)
            p, d = clip_seg(n, dur, None, gain=0.9); add(p, d)
            if n == 7: add(freeze_seg(7, d, "donut", 14.0, "donut_target_share.png"), 14.0, "yt_donut")
            if n == 15: add(freeze_seg(15, d, "td", 11.0, "counter_15.png"), 11.0, "yt_td")
        add(freeze_seg(20, d, "weekly", 18.0, "weekly_targets.png"), 18.0, "yt_weekly")
        add(card_seg("end", "end_16x9.png", 6.0, 0.3, 1.0), 6.0)
    elif cut == "shortA":
        add(card_seg("title", "title_9x16.png", 2.0, 0.3, 0.2, zoom=False), 2.0)
        f, tin, tout = T(15); dur = (tout - tin) if tout else max(4.0, probe(f)[0] - tin)
        p, d = clip_seg(15, min(dur, 12.0), CAPTION["shortA"], gain=0.9); add(p, d)
        add(card_seg("end", "end_9x16.png", 3.0, 0.3, 0.8, zoom=False), 3.0)
    elif cut == "shortB":
        add(card_seg("title", "title_9x16.png", 2.0, 0.3, 0.2, zoom=False), 2.0)
        for n in CATCHES: p, d = clip_seg(n, 1.8 if n != 15 else 3.0, CAPTION["shortB"], gain=0.6); add(p, d)
        add(card_seg("end", "end_9x16.png", 3.0, 0.3, 0.8, zoom=False), 3.0)
    total = t
    # concat video (re-encode once for a clean stream)
    lst = os.path.join(work, f"{cut}_list.txt"); open(lst, "w").write("".join(f"file '{s}'\n" for s in segs))
    silent = os.path.join(work, f"{cut}_video.mp4")
    run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",lst,"-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-r",str(FPS),"-c:a","aac","-ar","48000","-ac","2","-b:a","160k",silent])
    # audio: clip sound + narration + ducked music
    inputs = ["-i", silent]; fl = ["[0:a]volume=1.0[clip]"]; n_in = 1; vo_labels = []
    for (t0, key) in vo_events:
        w = tts(key, VO[key], work)
        if not w: continue
        inputs += ["-i", w]; ms = int(t0 * 1000)
        fl.append(f"[{n_in}:a]aresample=48000,highpass=f=75,acompressor=threshold=-20dB:ratio=3:attack=4:release=120:makeup=3,adelay={ms}|{ms},apad=whole_dur={total:.3f},atrim=0:{total:.3f}[vo{n_in}]")
        vo_labels.append(f"[vo{n_in}]"); n_in += 1
    if vo_labels:
        fl.append("".join(vo_labels) + f"amix=inputs={len(vo_labels)}:duration=first:normalize=0,asplit=2[vo][vosc]")
    if music and os.path.exists(music):
        inputs += ["-stream_loop", "-1", "-i", music]
        fl.append(f"[{n_in}:a]aresample=48000,atrim=0:{total:.3f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1.0,afade=t=out:st={max(0,total-3.5):.2f}:d=3.5,volume=0.9[mus0]")
        if vo_labels: fl.append("[mus0][vosc]sidechaincompress=threshold=0.045:ratio=4.5:attack=12:release=700:makeup=1:level_sc=1.4[mus1]"); fl.append("[mus1]volume=0.33[mus]")
        else: fl.append("[mus0]volume=0.3[mus]")
        n_in += 1
    mix_in = ["[clip]"] + (["[vo]"] if vo_labels else []) + (["[mus]"] if music and os.path.exists(music) else [])
    fl.append("".join(mix_in) + f"amix=inputs={len(mix_in)}:duration=first:normalize=0,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    final = os.path.join(outdir, {"x":"nabers-w5-every-target-X.mp4","youtube":"nabers-w5-every-target-YouTube.mp4","shortA":"nabers-w5-short-A-tying-TD.mp4","shortB":"nabers-w5-short-B-all-catches.mp4"}[cut])
    run(["ffmpeg","-y","-v","error"]+inputs+["-filter_complex",";".join(fl),"-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","192k","-movflags","+faststart","-shortest",final])
    print(f"{cut}: {final}  ({total:.1f}s, {len(segs)} segments)")
    return final

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--cut", default="all"); ap.add_argument("--clips", default=os.path.join(HERE, "clips.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "output")); ap.add_argument("--work", default=os.path.join(HERE, "work"))
    ap.add_argument("--placeholders", action="store_true"); ap.add_argument("--no-vo", action="store_true"); ap.add_argument("--music", default=os.environ.get("MUSIC"))
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); os.makedirs(a.work, exist_ok=True)
    if a.placeholders:
        clips = {}
        for n in range(1, 21):
            png = placeholder_png(n, a.work); mp4 = os.path.join(a.work, f"ph_{n:02d}.mp4")
            if not os.path.exists(mp4): seg_from_still(png, 6.0, [], mp4, "16x9", zoom=True)
            clips[n] = (mp4, 0.0, 6.0)
    else:
        j = json.load(open(a.clips)); clips = {}
        for tg in j["targets"]:
            f = tg["file"] if os.path.isabs(tg["file"]) else os.path.join(os.path.dirname(os.path.abspath(a.clips)), tg["file"])
            if not os.path.exists(f): sys.exit(f"missing clip for target {tg['n']}: {f}")
            clips[int(tg["n"])] = (f, float(tg.get("in", 0)), float(tg["out"]) if tg.get("out") is not None else None)
        missing = [n for n in range(1, 21) if n not in clips]
        if missing: sys.exit(f"clips.json is missing targets {missing}")
    cuts = ["x", "youtube", "shortA", "shortB"] if a.cut == "all" else a.cut.split(",")
    for c in cuts: build(c, clips, a.out, a.work, a.placeholders, a.music, a.no_vo)

if __name__ == "__main__": main()
