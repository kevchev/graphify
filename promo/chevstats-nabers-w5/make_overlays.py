"""Nabers Week 5 'every target' video graphics. Data: nflverse pbp (pulled Oct 12, 2026 7:40 AM PT), cross-checked
with Giants.com/CBS (20 tgt, 11-121-1) and Pro-Football-Reference (OBJ 20 tgt, Dec 22 2016)."""
import pandas as pd, math, os
from PIL import Image, ImageDraw, ImageFont
F = "/workspace/fantasy/charts/fonts/"
def f(n, s): return ImageFont.truetype(F + n, s)
HEAD, HSB, COND, SEMI, BOLD, REG = ["BarlowCondensed-ExtraBold.ttf", "BarlowCondensed-Bold.ttf", "BarlowCondensed-SemiBold.ttf",
                                    "Barlow-SemiBold.ttf", "Barlow-Bold.ttf", "Barlow-Regular.ttf"]
BG, PANEL, GRID, INK, SUB, FAINT, MUTED = "#0D1320", "#111A2B", "#1F2A3F", "#F3F5F9", "#A9B3C7", "#6F7C95", "#56627A"
HOT, COOL = "#FF6A1F", "#3FB8F5"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "overlays")
p = pd.read_parquet("/workspace/fantasy/charts/data/w5/pbp.parquet")
n = p[(p.week == 5) & (p.posteam == "NYG") & (p.receiver_player_name == "M.Nabers") & (p.play_type == "pass")].sort_values("play_id")
assert len(n) == 20 and n.complete_pass.sum() == 11 and n.receiving_yards.sum() == 121

def chev(d, x, y, h):
    w = h * 0.55
    for k, c in enumerate([HOT, COOL]):
        xo = x + k * w * 0.85
        d.polygon([(xo, y), (xo + w * .5, y + h / 2), (xo, y + h), (xo + w * .38, y + h), (xo + w * .88, y + h / 2), (xo + w * .38, y)], fill=c)
    return x + w * 1.95
def handle(d, x, y, s=30):
    x = chev(d, x, y + 4, s * 0.8) + 10
    d.text((x, y), "@ChevStats", font=f(HSB, s), fill=INK)

# 1) running target counter, lower third (one PNG per target)
rec = yds = 0
for i, r in enumerate(n.itertuples(), 1):
    q = "OT" if r.qtr == 5 else f"Q{int(r.qtr)}"
    if r.complete_pass == 1:
        rec += 1; yds += int(r.receiving_yards)
        res = "TOUCHDOWN  +17" if r.pass_touchdown == 1 else f"CATCH  {int(r.receiving_yards):+d}"
        col = HOT if r.pass_touchdown == 1 else COOL
    else:
        res, col = "INCOMPLETE", FAINT
    im = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0, y0, w, h = 70, 820, 820, 190
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 18, fill=PANEL + "EB", outline=GRID, width=2)
    d.rectangle((x0, y0 + 18, x0 + 10, y0 + h - 18), fill=HOT)
    d.text((x0 + 40, y0 + 18), "TARGET", font=f(COND, 30), fill=SUB)
    d.text((x0 + 38, y0 + 46), f"{i}", font=f(HEAD, 110), fill=HOT)
    tw = d.textlength(f"{i}", font=f(HEAD, 110))
    d.text((x0 + 48 + tw, y0 + 98), "/ 20", font=f(HSB, 48), fill=INK)
    xr = x0 + 330
    d.text((xr, y0 + 22), f"{q}  {r.time.lstrip('0') if not r.time.startswith('00') else r.time[1:]}", font=f(COND, 30), fill=SUB)
    d.text((xr, y0 + 58), res, font=f(HEAD, 54), fill=col)
    d.text((xr, y0 + 128), f"Running: {rec} rec, {yds} yds", font=f(SEMI, 28), fill=INK)
    # 20 pips
    for k in range(20):
        cx = x0 + 40 + k * 38
        d.rounded_rectangle((cx, y0 + h - 14, cx + 30, y0 + h - 8), 3, fill=HOT if k < i else MUTED)
    handle(d, 1560, 1000, 32)
    im.save(f"{OUT}/counter_{i:02d}.png")

# 2) target-share donut, right-side card
im = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
x0, y0, w, h = 1180, 150, 680, 760
d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 22, fill=PANEL + "F2", outline=GRID, width=2)
d.text((x0 + 40, y0 + 30), "GIANTS TARGETS  ·  WEEK 5", font=f(COND, 32), fill=SUB)
cx, cy, R = x0 + w / 2, y0 + 360, 220
for start, frac, col in [(0, 20 / 52, HOT), (20 / 52, 32 / 52, MUTED)]:
    d.pieslice((cx - R, cy - R, cx + R, cy + R), -90 + start * 360, -90 + (start + frac) * 360, fill=col)
d.ellipse((cx - R * .62, cy - R * .62, cx + R * .62, cy + R * .62), fill=PANEL)
d.text((cx, cy - 20), "38.5%", font=f(HEAD, 96), fill=HOT, anchor="mm")
d.text((cx, cy + 50), "20 of 52", font=f(SEMI, 34), fill=INK, anchor="mm")
d.text((x0 + 40, y0 + 600), "Nabers also drew 48% of the team's air yards", font=f(SEMI, 30), fill=INK)
d.text((x0 + 40, y0 + 642), "(245 of 508). Next-most: Likely, 13 targets.", font=f(REG, 28), fill=SUB)
handle(d, x0 + 40, y0 + h - 52, 26)
im.save(f"{OUT}/donut_target_share.png")

# 3) weekly targets W1-W5
wk = p[(p.posteam == "NYG") & (p.receiver_player_name == "M.Nabers") & (p.play_type == "pass")].groupby("week").size()
assert list(wk) == [9, 4, 6, 7, 20]
im = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
x0, y0, w, h = 1180, 150, 680, 760
d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 22, fill=PANEL + "F2", outline=GRID, width=2)
d.text((x0 + 40, y0 + 30), "NABERS TARGETS BY WEEK", font=f(COND, 32), fill=SUB)
base, top, bw, gap = y0 + 600, y0 + 130, 90, 30
for j, (k, v) in enumerate(wk.items()):
    bx = x0 + 55 + j * (bw + gap); bh = (base - top) * v / 20
    col = HOT if k == 5 else MUTED
    d.rounded_rectangle((bx, base - bh, bx + bw, base), 8, fill=col)
    d.text((bx + bw / 2, base - bh - 12), str(v), font=f(HEAD, 54 if k == 5 else 40), fill=HOT if k == 5 else INK, anchor="mb")
    d.text((bx + bw / 2, base + 14), f"W{k}", font=f(COND, 30), fill=SUB, anchor="mt")
d.text((x0 + 40, y0 + 668), "Career high (previous best: 18)", font=f(SEMI, 30), fill=INK)
handle(d, x0 + 40, y0 + h - 52, 26)
im.save(f"{OUT}/weekly_targets.png")

# 4) title + end cards, 16:9 and 9:16, opaque
def card(size, lines, name):
    W, H = size; im = Image.new("RGB", size, BG); d = ImageDraw.Draw(im)
    s = W / 1920 if W > H else W / 1080
    y = H * 0.30
    for txt, font, sz, col in lines:
        d.text((W / 2, y), txt, font=f(font, int(sz * s)), fill=col, anchor="mm"); y += sz * s * 1.25
    handle(d, W / 2 - 120 * s, H - 120 * s, int(40 * s))
    im.save(f"{OUT}/{name}.png")
title = [("EVERY TARGET", COND, 60, SUB), ("MALIK NABERS", HEAD, 150, INK), ("20", HEAD, 220, HOT), ("Giants at Commanders  ·  Week 5", SEMI, 44, SUB)]
end = [("20 TARGETS  ·  11-121-1", HEAD, 110, INK), ("Most by a Giant since", SEMI, 50, SUB), ("Odell Beckham Jr. (Dec 2016)", BOLD, 56, HOT),
       ("Last 2 games: 233 yds, 2 TD", SEMI, 50, INK), ("Next: vs. Saints", SEMI, 44, COOL)]
for sz, tag in [((1920, 1080), "16x9"), ((1080, 1920), "9x16")]:
    card(sz, title, f"title_{tag}"); card(sz, end, f"end_{tag}")
print("ok")
