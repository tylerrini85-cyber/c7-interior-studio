# Reference and source manifest — C7 Interior Studio

Baseline vehicle: **2019 Chevrolet Corvette Stingray Coupe, 3LT, GT seats, 8-speed automatic, Jet Black Napa leather, removable targa roof panel.**
Decided with Tyler on 2026-10-26 (see PROGRESS.md).

## How this manifest was produced

This cloud session's network policy allows package registries and GitHub only. Every automotive, forum, marketplace and
photo host (media.chevrolet.com, corvetteforum.com, corvetteblogger.com, sketchfab.com, cgtrader.com, turbosquid.com,
wikimedia, flickr) is denied at the proxy, so **no reference image could be downloaded or viewed from this environment**.
Research was done with the Anthropic web-search tool, which returns text snippets only. Each entry therefore records
what the text source states, how reliable it is, and which modeling decision it supports. Items marked **APPROX** are my
own approximations from general knowledge of the C7 cockpit and must be validated against photographs Tyler supplies
(see "Photos requested" at the bottom).

Reliability key: **A** = GM press/spec material, **B** = established automotive press, **C** = dealer listing / forum / enthusiast site, **APPROX** = my estimate.

| # | Subject | Source | Model year / trim | Reliability | License / usage | Supports decision |
|---|---------|--------|-------------------|-------------|-----------------|-------------------|
| 1 | Front headroom 38.0 in (37.9), legroom 43.0 in, shoulder room 55.0–55.2 in, hip room 53.7–54.0 in, interior volume 52 cu ft | corvsport.com/?p=106195 ; truedelta.com Chevrolet-Corvette specs 2019 ; iseecars 2019 dimensions | 2019 Stingray | A/B (published GM figures) | facts, not redistributed | Cabin width 1.37–1.40 m at hip/shoulder; roof height over H-point; pedal distance |
| 2 | Exterior: wheelbase 106.7 in, length 176.9 in, width 73.9 in, height 48.6 in | corvetteactioncenter.com 2015 specs PDF; 2014 preliminary specifications | 2014–2019 | A | facts | Overall envelope; roof interior height ≈1.20 m above floor |
| 3 | Steering wheel diameter 14.1 in (358 mm), first Corvette-specific wheel, prominent thumb rests | gardnerweb.com "new corvette revives stingray name"; corvette-mag.com issue 85 "Sports Car Reborn" | 2014 | B | facts | Rim diameter 0.358 m, thumb-rest geometry at 9/3 o'clock |
| 4 | Cluster: 8-inch LCD centered, flanked by analog speedometer (left) and fuel + coolant gauges (right); Tour/Sport/Track themes; Sport = large radial tach with red glow ring; Track = hockey-stick tach, large gear indicator, shift lights | corvetteactioncenter.com 2014 press release 14 "Too Much Information?"; jalopnik.com; motorauthority.com 1086209 | 2014–2019 (unchanged) | A | facts | Cluster layout and the three gauge themes implemented as textures |
| 5 | GT seat (standard) vs Competition Sport seat (deeper bolsters, firmer foam, harness pass-throughs); both magnesium frame; Napa leather on 3LT | corvetteactioncenter.com seats press release; corvetteblogger.com 2013/01/21 seating options; canadiancorvetteforums thread 5483 | 2014–2019 | A/C | facts | GT seat as factory baseline geometry; Competition Sport as geometry variant |
| 6 | 3LT content: custom leather-wrapped instrument panel and doors, sueded microfiber upper interior trim, GT seats in Napa leather | chevrolet.com previous-year corvette stingray; corvsport.com 2020 options; classiccars.com 2019 listing (Jet Black Napa on seats, doors, console, IP) | 2019 3LT | A/C | facts | Material assignment: leather IP/doors/console, suede headliner, A-pillars and upper trim |
| 7 | 2019 interior colors confirmed: Jet Black, Adrenaline Red, Kalahari; Driver Series editions with red/yellow stitching | vms.autorevo.com 2019 Grand Sport 3LT brochures; classiccars.com Boise listing; dupontregistry 2019 Drivers Series | 2019 | C | facts | Factory color presets. Gray and Brownstone not confirmed for 2019 in sources: offered as "factory-inspired" presets, flagged |
| 8 | Console: cupholders with sliding cover, aux power, hidden storage behind the motorized 8-inch MyLink screen, electronic parking brake switch on console, drive-mode selector dial next to shifter | corvetteblogger.com 2013/09/05 closer look interior; palmeter.com C7 facts (pre-launch speculation, low weight) | 2014–2019 | C | facts | Console component layout (screen, HVAC strip, dial, shifter, EPB, cupholders, armrest) |
| 9 | Door panel: curved pull/grab handle, armrest, window + lock switches on armrest, speaker low in door, upper trim and insert; Bose system | aftermarket listings (window-switch covers, speaker trims for 2014–2019) | 2014–2019 | C | facts | Door panel component list only; shape is **APPROX** |
| 10 | Free / CC0 C7 interior 3D model: **none found**. All candidates (3dcadbrowser, renderhub PixelPoint, squir) are royalty-free-with-no-redistribution or editorial-only paid assets | 3dcadbrowser.com, renderhub.com | — | — | not usable (no money, no redistribution) | Geometry is built from scratch in Blender scripts in `tools/blender/` |
| 11 | GM trademarks (crossed flags, Stingray script, Corvette wordmark) | general knowledge of GM trademark policy | — | — | **not licensed**: development placeholders only, in `public/branding/` with a swap path | Emblem placeholders |
| 12 | Driver eye point, seat H-point height, wheel-to-hip distance, dash depth, windshield rake, console height | **APPROX** derived from items 1–3 and typical sports-car packaging | — | APPROX | — | Camera positions and cockpit layout; to be checked against Tyler's photos |

## Photos requested from Tyler (to validate the APPROX items)

Please add JPG/PNG files to `c7-interior-studio/reference/` in the repo (any phone photos of a real C7, or
screenshots you have rights to use for private reference). Most valuable, in order:

1. Driver-seat eye-level view straight ahead (wheel, cluster, windshield).
2. Same from passenger seat.
3. Center console from above, including shifter, dial, cupholders and armrest.
4. Steering wheel straight on, close.
5. Driver seat from the open door, side view and front view.
6. Door panel, full height.
7. Dashboard from passenger side looking left across the car.
8. Headliner and roof panel from inside.
9. Footwell and pedals.
10. Rearward view from the driver seat.

Reference files are for private comparison only and are not shipped in the built app.


## Owner-supplied photo batch 2 (reference/batch2, 66 images)
Collected by the owner from image search in October 2026 and committed to `reference/batch2`. Used for the batch 2
accuracy pass (see VISUAL-ASSESSMENT.md). Personal reference only; not shipped with the app and not redistributed.
