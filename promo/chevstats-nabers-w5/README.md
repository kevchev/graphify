# @ChevStats · "Every Malik Nabers target, Week 5" — assembly kit

Turns the graphics pack (title/end cards, 20 lower-third counters, target-share donut, weekly-targets
chart) plus your screen-recorded clips into four finished videos:

| Cut | Format | Length | What it is |
|---|---|---|---|
| `nabers-w5-every-target-X.mp4` | 16:9 1080p | ~62 s | all 20 targets with the counter, donut pause after target 7, weekly chart before the end card, narration + burned-in captions |
| `nabers-w5-every-target-YouTube.mp4` | 16:9 1080p | 3–4 min | all 20 targets at full length, three narrated pauses (donut after 7, the TD after 15, weekly chart before the end) |
| `nabers-w5-short-A-tying-TD.mp4` | 9:16 | ~11 s | title card → the 17-yd game-tying TD with counter 15 → end card |
| `nabers-w5-short-B-all-catches.mp4` | 9:16 | ~27 s | title card → all 11 catches, rapid cuts → end card |

The `output/` folder currently holds **previews rendered on placeholder footage** (a mock field with the
quarter, clock and play result for each target). Every edit decision, overlay position, caption, narration
line and pause length is final; only the footage is a stand-in.

## What you need to supply: the clips

Per the pack's footage rule, you screen-record the official highlight clips (sources and quarter/clock for
every target are in `week5_clip_sources.md`, section 1). Then describe them in `clips.json`:

```json
{"targets": [
  {"n": 1,  "file": "clips/giants-commanders-highlights.mp4", "in": 12.0, "out": 17.5},
  {"n": 2,  "file": "clips/giants-commanders-highlights.mp4", "in": 31.2, "out": 36.0},
  {"n": 15, "file": "clips/nabers-17yd-td.mp4", "in": 0.0, "out": 9.0}
]}
```

- One entry per target, `n` 1–20. `file` can be one long recording used 20 times with different `in`/`out`,
  or one file per play. `out` is optional (rest of the file).
- Record at 1080p 16:9 if you can; anything else is letterboxed onto the navy canvas.
- Aim for 3–8 s per play in the recording. The X cut trims each play to its slot (3.5 s for the first two,
  1.6 s for the misses, 2 s in the fourth quarter, 4.5 s for the TD). The YouTube cut uses the full trim.

Then:

```bash
pip install sherpa-onnx soundfile          # narration (Kokoro); skip and pass --no-vo to go without
export KOKORO_DIR=/path/to/kokoro-en-v0_19 # https://github.com/k2-fsa/sherpa-onnx/releases/tag/tts-models
export MUSIC=/path/to/bed.mp3              # optional music bed (ducked under narration)
python3 assemble.py --cut all --clips clips.json --out output
```

`--cut x`, `youtube`, `shortA`, `shortB` render one at a time. `--placeholders` reproduces the previews.

## What the script does

1. Each target becomes a segment: clip trimmed, scaled/letterboxed, counter PNG composited, caption added
   (X cut and Shorts only), clip audio kept (lowered under narration in the X cut, near full in the YouTube cut).
2. Stat-card pauses freeze a clean frame from the clip, keep the counter, and add the donut / weekly chart.
3. Title and end cards get a slow push-in and fades.
4. Segments are concatenated, then narration (per line, timed to the script table), clip audio and a ducked
   music bed are mixed and normalized to −14 LUFS.

Narration text lives in the `VO` dict at the top of `assemble.py` (X lines are verbatim from `script.md`; the
three YouTube pause lines expand its bullet notes). Captions are in `CAPTION`. Edit either and re-run.

## Files

```
assemble.py            the whole pipeline
clips.example.json     manifest format
overlays/              graphics from the pack (unchanged)
fonts/                 Barlow / Barlow Condensed TTFs for captions and placeholders
script.md, week5_clip_sources.md, make_overlays.py   the pack's planning files, for reference
output/                rendered videos
```
