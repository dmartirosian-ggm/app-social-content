"""Spark "tiny habit of the day" clip template.

One JSON file per clip goes in, a 7-second 1080x1920 MP4 (plus a cover JPG) comes out.

    python apps/spark/clip.py apps/spark/clips/01-brush-teeth.json     (or no file: render them all)

Every frame is a function of time t (seconds), drawn as SVG and rasterised with CairoSVG,
then piped to ffmpeg. The soundtrack (soft pad, a pluck per star, a chime) is synthesised,
so there is nothing to license.

Clip JSON:
{
  "slug": "01-brush-teeth",
  "habit": "Brush teeth",              # big title, same wording as the app's habit
  "icon": "tooth",                     # any habit icon from the app (see brand.ICON_TINT)
  "tip": "One sentence a parent would say.",
  "done": "Line shown when the week fills up.",
  "child": {"name": "Mia", "color": "#FFB4A2"},
  "days_done": 7                       # optional, stars that fill (default 7)
}
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand import (APP_NAME, APP_TAGLINE, C, CONFETTI, ICON_TINT, STORE_LINE, avatar, card, icon, pill,  # noqa: E402
                   smiley_star, star)

from engine import audio, cli, confetti, render  # noqa: E402
from engine.anim import back_out, bump, clamp, ease_in_out, ease_out, mix, pop, prog  # noqa: E402
from engine.svg import group, svg_doc, text, text_block  # noqa: E402

W, H, FPS, DUR = 1080, 1920, 30, 7.0
DAYS = ["M", "T", "W", "T", "F", "S", "S"]

# timeline (seconds)
T_STAR0, T_STAR_GAP = 1.6, 0.3
T_DONE = 3.85
T_END = 5.4


def star_time(i):
    return T_STAR0 + i * T_STAR_GAP


def frame_svg(t, p):
    tint = C[ICON_TINT.get(p["icon"], "butter")]
    bg = mix(tint, "#FFFFFF", 0.5)
    days_done = p.get("days_done", 7)
    out = []

    # soft background blobs
    out.append(f'<circle cx="940" cy="180" r="260" fill="{tint}" opacity="0.9"/>')
    out.append(f'<circle cx="120" cy="1650" r="320" fill="{tint}" opacity="0.9"/>')

    # pill
    a = ease_out(prog(t, 0.05, 0.35))
    out.append(group(pill(540, 250, "Tiny habit of the day", 38, icon_name="sparkle", icon_color="#E0A800"),
                     y=(1 - a) * -40, opacity=a))

    # icon tile
    s = pop(prog(t, 0.15, 0.5))
    tile = card(540 - 125, 345, 250, 250, r=64) + icon(p["icon"], 540, 470, 160, C["ink"], 1.9)
    out.append(group(tile, scale=s, origin=(540, 470), opacity=clamp(s * 3)))

    # title
    a = ease_out(prog(t, 0.3, 0.4))
    title_svg, title_bottom = text_block(540, 650, p["habit"], "Fredoka", 700, 96, C["ink"], 920, 1.1)
    out.append(group(title_svg, y=(1 - a) * 30, opacity=a))

    # tip, then the "done" line
    tip_top = title_bottom + 28
    a_tip = ease_out(prog(t, 0.65, 0.45)) * (1 - ease_in_out(prog(t, T_DONE - 0.05, 0.3)))
    tip_svg, _ = text_block(540, tip_top, p["tip"], "Nunito", 600, 46, C["inkSoft"], 880, 1.32)
    out.append(group(tip_svg, y=(1 - ease_out(prog(t, 0.65, 0.45))) * 24, opacity=a_tip))
    a_done = ease_out(prog(t, T_DONE + 0.3, 0.4))
    if a_done > 0:
        done_svg, _ = text_block(540, tip_top + 6, p["done"], "Fredoka", 600, 58, C["success"], 900, 1.2)
        out.append(group(done_svg, y=(1 - a_done) * 24, opacity=a_done))

    # week card
    a = ease_out(prog(t, 1.15, 0.5))
    cx0, cy0, cw, ch = 70, 1090, 940, 400
    filled = sum(1 for i in range(days_done) if t >= star_time(i) + 0.05)
    inner = [card(cx0, cy0, cw, ch, r=48)]
    child = p.get("child", {"name": "Mia", "color": "#FFB4A2"})
    inner.append(avatar(cx0 + 78, cy0 + 78, 36, child["name"][0].upper(), child["color"]))
    inner.append(text(cx0 + 132, cy0 + 93, child["name"], "Nunito", 800, 42, C["ink"], anchor="start"))
    inner.append(text(cx0 + cw - 50, cy0 + 92, f"{filled} of 7 stars", "Nunito", 800, 38,
                      C["success"] if filled == 7 else C["muted"], anchor="end"))
    inner.append(f'<rect x="{cx0 + 40}" y="{cy0 + 140}" width="{cw - 80}" height="3" rx="1.5" fill="{C["line"]}"/>')
    col_w = (cw - 60) / 7
    for i, d in enumerate(DAYS):
        x = cx0 + 30 + col_w * (i + 0.5)
        inner.append(text(x, cy0 + 205, d, "Nunito", 800, 34, C["muted"]))
        inner.append(star(x, cy0 + 300, 100, empty=True))
        if i < days_done:
            ps = prog(t, star_time(i), 0.38)
            if ps > 0:
                sc = back_out(ps, 2.6)
                rot = (1 - ps) * -40
                inner.append(group(star(x, cy0 + 300, 100), scale=sc, rotate=rot, origin=(x, cy0 + 300)))
    # gentle bounce of the whole card when the week completes
    b = bump(prog(t, T_DONE, 0.4), 0.035) if days_done == 7 else 0.0
    out.append(group("".join(inner), y=(1 - a) * 500, opacity=clamp(a * 2), scale=1 + b, origin=(540, cy0 + ch / 2)))

    if days_done == 7 and not p.get("_cover"):
        out.append(confetti.rain(t, T_DONE - 0.1, CONFETTI, seed=len(p["habit"])))

    # end card: butter circle wipe
    pe = prog(t, T_END, 0.5)
    if pe > 0:
        r = ease_in_out(pe) * 1250
        out.append(f'<circle cx="540" cy="900" r="{r:.1f}" fill="{C["butter"]}"/>')
        ps = pop(prog(t, T_END + 0.25, 0.55))
        out.append(group(smiley_star(540, 690, 400), scale=ps, origin=(540, 690), opacity=clamp(ps * 3),
                         rotate=(1 - clamp(ps)) * -20))
        a = ease_out(prog(t, T_END + 0.45, 0.4))
        endtxt = (
            text(540, 1040, APP_NAME, "Fredoka", 700, 140, C["ink"])
            + text(540, 1125, APP_TAGLINE, "Fredoka", 600, 58, C["inkSoft"])
        )
        out.append(group(endtxt, y=(1 - a) * 30, opacity=a))
        a2 = ease_out(prog(t, T_END + 0.7, 0.4))
        out.append(group(pill(540, 1250, STORE_LINE, 44, fill=C["ink"], color=C["white"], pad_x=44,
                              pad_y=24), y=(1 - a2) * 30, opacity=a2))

    return svg_doc(W, H, "".join(out), bg)


# ---------------------------------------------------------------- audio
def soundtrack(path, p):
    buf, t = audio.timeline(DUR)
    buf += audio.pad(t, DUR)
    # a pluck per star, climbing a pentatonic scale
    notes = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5, 1174.66]
    for i in range(p.get("days_done", 7)):
        audio.add(buf, star_time(i) + 0.06, audio.tone(notes[i], 0.6, 0.18), 0.22)
    if p.get("days_done", 7) == 7:
        for k, f in enumerate((1046.5, 1318.5, 1568.0, 2093.0)):
            audio.add(buf, T_DONE + k * 0.07, audio.tone(f, 1.2, 0.45, ((1, 1.0), (2.76, 0.2))), 0.12)
    # end card: two soft notes
    audio.add(buf, T_END + 0.3, audio.tone(783.99, 1.4, 0.5), 0.12)
    audio.add(buf, T_END + 0.42, audio.tone(1046.5, 1.6, 0.6), 0.12)
    audio.write_wav(path, buf)


# ---------------------------------------------------------------- main
def make(p, out_dir):
    slug = p["slug"]
    mp4 = os.path.join(out_dir, f"{slug}.mp4")
    os.makedirs(out_dir, exist_ok=True)
    wav = os.path.join(out_dir, f".{slug}.wav")
    soundtrack(wav, p)
    try:
        render.save_mp4(frame_svg, p, mp4, DUR, FPS, wav=wav)
    finally:
        os.remove(wav)
    # cover: the moment the week is full
    render.save_jpg(frame_svg(T_DONE + 1.0, {**p, "_cover": True}), os.path.join(out_dir, f"{slug}-cover.jpg"))
    return mp4


if __name__ == "__main__":
    specs, out = cli.parse(__file__, "clips")
    for p in specs:
        print("rendered", make(p, out))
