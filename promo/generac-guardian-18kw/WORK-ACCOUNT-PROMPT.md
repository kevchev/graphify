# Prompt for the Gardenland work account

Paste everything below the line into a new Claude Code session (web or desktop) that has the
`kevchev/graphify` repository attached. Branch `claude/greenworks-optimus-promo-video-cl8pab`
(or `v3` once PR #1 merges) carries the template.

---

Rebuild the Generac Guardian 18kW "El Niño winter" promo for Gardenland Power Equipment at the quality
of the reference cut in this repo, and fix whatever in this environment stopped the last attempt short.

## 1. Environment check first (report before building anything)

Run these and show me a table of results. For anything missing, try to install it, and if the
install fails say exactly which host or permission blocked it. Do not silently fall back.

1. `ffmpeg -version | head -1`
2. Node with Playwright: `node -e "require('playwright')"` then launch Chromium headless once.
   If missing: `npm i playwright` and `npx playwright install chromium`.
3. Python: `python3 -c "import sherpa_onnx, soundfile, cv2, numpy, PIL"`.
   If missing: `pip install sherpa-onnx soundfile opencv-contrib-python numpy pillow`.
4. Speech model: download
   `https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-en-v0_19.tar.bz2`
   and extract it outside the repo. Export `KOKORO_DIR=<that folder>`.
5. Music: clone `https://github.com/effacestudios/Royalty-Free-Music-Pack` (CC0) outside the repo
   and note the path; the template uses `Cinemato.mp3`.
6. Super-resolution (optional): `EDSR_x2.pb` from `https://github.com/Saafke/EDSR_Tensorflow`.
7. Tell me which permission mode this session runs in. If each shell command will prompt me,
   say so now so I can switch the session to auto mode before you start rendering.

If narration cannot be produced here, do not downgrade the brief to "text and music only". Build
every other part of the piece, leave the narration timeline in `mix.json` intact, and give me the
eight lines from `audio/narration-script.json` so a human can record them.

## 2. Use the template, don't start over

The folder `promo/generac-guardian-18kw/` is a finished 51-second cut. Read its `README.md`
first. It contains:

- `render/composition.html`: a deterministic timeline. `window.seek(t)` sets every style for
  time `t`. Every scene, easing, count-up, rain layer, lightning flash, light sweep and wipe is in
  there. Change it; do not replace it with Remotion or slides.
- `render/render.js` and `render/stills.js`: Playwright renderers. Keep the
  `--allow-file-access-from-files` flag or CSS mask images will fail silently.
- `render/prep_assets.py`: derives the dark-house plate, window bloom and rain sprites.
- `render/tts.py`, `render/mix.py`, `render/mix.json`: narration, ducked music bed, hits, and
  a two-pass loudness trim to −14 LUFS.
- `assets/`: plates, product render, logo, fonts.

Rebuild it end to end with the commands in the README's "Rebuild" section. Render frames in
parallel workers (the renderer takes a frame range). Encode with libx264 crf 18, yuv420p, AAC.

## 3. What to improve over the template (in this order, as far as the environment allows)

1. Replace the three Canva plates with real photography if you can get it: a screen-recorded or
   photographed Guardian unit at the Campbell store, or stock storm footage I supply. Never
   fabricate the product; the Generac render in `assets/img` is the only product image allowed
   unless I give you more.
2. Add a 9:16 version (1080×1920) by re-laying out the same composition: text block on top,
   plate or product below, same timing, same narration. Export it as a second MP4.
3. Tighten anything you see in review (section 4). Do not change the on-screen words.

## 4. Review loop (this is the part that was skipped last time)

After every render, extract a contact sheet from the encoded MP4 (one frame every 2 seconds)
and look at it. Also render stills at every cut point and at the middle of every scene. Check for
text overlaps, text cut off at the edges, empty frames, a transition that shows the wrong scene,
and anything that loads wrong (the browser console log from the renderer must be empty).
Fix, re-render only the affected frame range, re-encode, and look again. Then measure loudness
with `ebur128` and confirm −14 LUFS integrated, −1.5 dBTP.

## 5. Frozen facts

Every on-screen word in `README.md`'s claims table is verified and must appear exactly as written.
Uppercase is a style choice, not a rewrite. Keep the disclaimer line on the price scene. Before
airing I still need to confirm NOAA's 12 Nov update, Campbell stock and Generac's MAP policy; list
those in your final message.

## 6. Deliver

- `output/generac-18kw-el-nino-promo.mp4` (16:9) and `output/generac-18kw-el-nino-promo-9x16.mp4`.
- Send me both files directly in the chat, not just a path.
- Commit to a branch and open a draft PR. Update the README's scene table and asset list for
  anything you changed.
- Final message: the environment table from step 1, what you changed, what you could not do and
  why, and the three facts to confirm before airing.
