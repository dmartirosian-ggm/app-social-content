# Galaxy Growth Media

Short vertical videos for Galaxy Growth Media's own Facebook, Instagram, TikTok and YouTube.
The look follows galaxygrowthmedia.com: white, navy text, blue #1A5FE8 and purple #914EFD,
Montserrat headings and DM Sans body text, and the logo from the site header.

Unlike Spark, GGM's videos are made with Remotion (React), in `remotion/`. `clip.py` reads
the JSON files in `clips/`, renders each one with Remotion and writes the usual MP4 and cover
JPG to `out/ggm/clips/`, so the review page and upload work the same as for every app.

Two formats:

- `Ugc`: a laptop on a desk, filmed like a phone video, showing a client's real numbers on a
  white dashboard, with plain TikTok-style captions. Props: client, chart title and period,
  months, values, three number tiles, and the captions with their frame timing (30 fps).
- `TipLight`: a contractor tip in steps on a white background, then the website.

Use only numbers read from the GGM dashboard, and name the months they cover.

```
python apps/ggm/clip.py
```

Needs Node.js 18 or newer and ffmpeg. The first run installs the npm packages.
