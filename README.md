# app-social-content

One place to hold and generate social content for all the apps
(Spark, Ayah Daily, Linedrive, Texas State Park Travelers, Pale Pages, Beau).

## Layout

- `engine/` — shared Python renderer, driven by JSON specs
  - short vertical clips: 1080x1920 mp4 (silent audio track) plus a cover jpg
  - Pinterest pins: 1000x1500 png
- `apps/<app>/` — one folder per app
  - `brand.json` — name, call to action (`cta`, `cta_sub`), colours, themes, fonts, logo
  - `clips/*.json` — one spec per clip
  - `pins/*.json` — one spec per pin
  - `captions.md` — captions keyed by spec id
- `out/<app>/` — rendered files (gitignored)

## Render

Needs Python 3.10+, Pillow (`pip install -r requirements.txt`) and `ffmpeg` on the PATH.

```bash
python -m engine render spark                 # everything for one app
python -m engine render spark --pins          # only pins (or --clips)
python -m engine render spark --only habit-01-two-choices
python -m engine render all                   # every app
python -m engine list
```

## Add an app

1. Copy `apps/spark` to `apps/<app>`.
2. Edit `brand.json`: name, `cta`, colours. To use a real logo, put the png in the app folder and set
   `"logo": "logo.png"` (add `"logo_is_wordmark": true` if the image already contains the name).
   Custom fonts work the same way: drop the font file in the app folder and name it under `fonts`.
3. Replace the specs in `clips/` and `pins/`, and rewrite `captions.md`.
4. Run `python -m engine render <app>`.

## Spec reference

**brand.json colours** (all required, `#RRGGBB`): `bg_top`, `bg_bottom`, `ink`, `muted`, `primary`,
`on_primary`, `accent`, `card`. A named entry under `themes` overrides any of them; a spec opts in with
`"theme": "night"`.

**Clip** — `id` (defaults to the file name), optional `theme`, `scenes`, optional `cover`.
Scene types:

| type | fields |
| --- | --- |
| `title` | `text`, optional `eyebrow`, `sub`, `duration` (default 3s) |
| `list` | `items` (strings), optional `heading`, `duration` (default 5s) |
| `cta` | optional `text` (defaults to the brand `cta`), `sub`, `duration` (default 2.5s) |

`cover` takes the same fields as a `title` scene; without it the cover is the first scene.

**Pin** — `id`, optional `theme`, `title`, optional `eyebrow`, `subtitle`, `footer`, and `steps`:
a list of `{"title", "note"}` (or plain strings). Text shrinks to fit; around 4 to 7 steps reads best.

Fonts: Inter (SIL Open Font License) is bundled in `engine/fonts/` as the default. Spark uses its own
site fonts, Fredoka and Nunito (both SIL Open Font License), from `apps/spark/fonts/`.
