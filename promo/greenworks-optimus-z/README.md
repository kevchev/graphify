# Greenworks Commercial OptimusZ — 10-Year Anniversary Promo Video

A 1080p / 30 fps / 81-second promotional video for the OptimusZ Series 9 zero-turn mowers,
built around the Greenworks Commercial 10-year anniversary instant-savings offer.

**Deliverable:** `output/optimusz-10-year-promo.mp4` (H.264 + AAC, 1920×1080, stereo, −14 LUFS)

## What the video says (and where each claim comes from)

| Claim in video | Source |
|---|---|
| Up to $10,000 instant anniversary savings on select 48", 52", 60" and 72" OptimusZ ride-on and stand-on mowers; average commercial zero-turn price reduced from ≈$29,000 to ≈$19,000 | Greenworks Commercial press release, PR Newswire, Feb 12 2026 (“Greenworks Commercial Celebrates 10 Years with Up to $10,000 in Instant Savings on OPTIMUS Zero-Turn Mowers”) |
| 60" OptimusZ Series 9 (24 kWh): normally $28,999, anniversary price $19,999 | Pro Tool Reviews, “Greenworks Commercial Celebrates 10 Years with Massive Savings”, May 5 2026 (in partnership with Greenworks Commercial) |
| 65 HP equivalent, constant 19,000 FPM blade-tip speed, 16 mph forward / 12 mph reverse, 5-year / 2,000-hour warranty | Pro Tool Reviews comparison table; greenworkscommercial.com product and collection pages |
| Up to 21 acres and 8 hours on a single charge (24 kWh LFP), recharge in as little as 5 hours with super charger | greenworkscommercial.com OZ960R product page and OptimusZ collection page |
| 2,000-hour cost comparison: $840 vs $12,120 energy/fuel, $250 vs $5,000 maintenance (≈$16,000 lower total cost) | Pro Tool Reviews, May 2026 (3 kWh/hr @ $0.14/kWh vs 1.5 gal/hr @ $4.04/gal, EIA pricing) |
| Pricing excludes Hawaii and Alaska; see dealer for details | greenworkscommercial.com product pages |

The offer was announced as limited-time. Confirm current eligibility and pricing with Greenworks
Commercial before publishing.

## Assets and rights

- Product renders, the “10 Years” key art and lifestyle photography are Greenworks Commercial's own
  marketing imagery captured from greenworkscommercial.com (page renders; the image CDN was not
  reachable from the build environment). Product cutouts were upscaled 2–3× with EDSR and
  alpha-keyed. Use of this imagery assumes you are promoting Greenworks product as a dealer or
  partner — confirm with your Greenworks rep.
- Music: “The Champion” from the effacestudios Royalty-Free-Music-Pack (CC0 1.0, public domain).
- Narration: synthesized with Kokoro-82M (Apache-2.0) via sherpa-onnx, voice `am_michael`.
- Fonts: Barlow / Barlow Condensed (SIL OFL) from Google Fonts.

## How it is built

```
render/composition.html   deterministic motion-graphics timeline (window.seek(t) sets every style)
render/render.js          Playwright screenshots one PNG per frame; supports frame ranges for parallel workers
render/stills.js          renders review stills at chosen times
render/keyout.py          alpha-keys white-background product renders and crops to content
render/mix.py + mix.json  narration placement, EQ/compression, ducked music bed, loudness normalization
assets/img, assets/fonts  source imagery (SR = super-resolved, cut = keyed) and font files
audio/soundtrack.wav      final mixed soundtrack
```

Rebuild:

```bash
node render/render.js render/composition.html frames 30 81          # frames (or split ranges across workers)
SCRATCH=<dir with vo/ and music/> python3 render/mix.py             # soundtrack
ffmpeg -framerate 30 -i frames/f%05d.png -i audio/soundtrack.wav \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest output/optimusz-10-year-promo.mp4
```

## Scene list

| Time | Scene | Narration |
|---|---|---|
| 0:00 | Open on “10 Years” key art | Ten years ago, Greenworks Commercial set out to replace gas. For good. |
| 0:07 | Hero — OptimusZ Series 9 | Today, the OptimusZ Series 9 is the proof. |
| 0:11 | Power stats (65 HP · 19,000 FPM · 16 mph) | Sixty-five horsepower of instant electric torque… |
| 0:21 | Runtime (21 acres · 8 hours) | Up to twenty-one acres, and eight hours of mowing, on a single charge. |
| 0:27 | No fuel / fumes / maintenance + warranty | No fuel. No fumes. Almost no maintenance… |
| 0:35 | Lineup 48"–72", ride-on & stand-on | Ride-on or stand-on. Forty-eight to seventy-two inches… |
| 0:42 | 2,000-hour cost comparison | And over two thousand hours, the electric advantage adds up… |
| 0:50 | Offer — up to $10,000 instant savings | Now, to celebrate ten years… |
| 0:59 | Price example — $28,999 → $19,999 | The sixty inch Series 9. Normally… Now nineteen thousand, nine ninety-nine. |
| 1:07 | Limited time / find a dealer | Instant savings, right at the dealer. For a limited time only. |
| 1:12 | Close — logo, URL, disclaimer | Ten years of charging the industry. One serious reason to switch… |
