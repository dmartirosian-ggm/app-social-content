"""Spark routine chart pins (Pinterest, 1000x1500 PNG).

    python apps/spark/pin.py apps/spark/pins/morning-age-3.json     (or no file: render them all)

Pin JSON:
{
  "slug": "morning-age-3",
  "kind": "morning",                    # "morning", "bedtime", "chores" or "afternoon" (sets the colors)
  "title": "Morning routine for a 3 year old",
  "subtitle": "One sentence under the title.",
  "steps": [["Use the potty", "potty"], ["Get dressed", "shirt"], ...]   # label, app icon
}
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brand import APP_NAME, APP_TAGLINE, C, ICON_TINT, STORE_LINE, card, icon, pill, smiley_star, star  # noqa: E402

from engine import cli, render  # noqa: E402
from engine.svg import svg_doc, text, text_block  # noqa: E402

W, H = 1000, 1500
DAYS = ["M", "T", "W", "T", "F", "S", "S"]
THEME = {
    "morning": {"bg": C["butter"], "blob": "#FFE59A", "pill": "Morning routine", "pill_icon": "sun"},
    "bedtime": {"bg": C["lilac"], "blob": "#D9CEFF", "pill": "Bedtime routine", "pill_icon": "sleep"},
    "chores": {"bg": C["mint"], "blob": "#BFE8D4", "pill": "Chore chart", "pill_icon": "check"},
    "afternoon": {"bg": C["peach"], "blob": "#FFCDBC", "pill": "After school", "pill_icon": "backpack"},
}


def pin_svg(p):
    th = THEME[p["kind"]]
    out = [
        f'<circle cx="930" cy="80" r="230" fill="{th["blob"]}"/>',
        f'<circle cx="40" cy="1450" r="260" fill="{th["blob"]}"/>',
        pill(500, 92, th["pill"], 30, icon_name=th["pill_icon"], icon_color=C["ink"]),
    ]
    title_svg, y = text_block(500, 150, p["title"], "Fredoka", 700, 74, C["ink"], 860, 1.08)
    out.append(title_svg)
    sub_svg, y = text_block(500, y + 18, p["subtitle"], "Nunito", 600, 34, C["inkSoft"], 820, 1.3)
    out.append(sub_svg)

    steps = p["steps"]
    top = max(y + 36, 430)
    foot = 1345
    head_h = 84
    row_h = min(132, (foot - 30 - top - head_h) / len(steps))
    card_h = head_h + row_h * len(steps) + 24
    x0, cw = 50, 900
    out.append(card(x0, top, cw, card_h, r=44))

    star_x0, star_x1 = 548, 912
    col = (star_x1 - star_x0) / 7
    for i, d in enumerate(DAYS):
        out.append(text(star_x0 + col * (i + 0.5), top + 58, d, "Nunito", 800, 28, C["muted"]))
    out.append(f'<rect x="{x0 + 32}" y="{top + head_h - 2}" width="{cw - 64}" height="3" rx="1.5" fill="{C["line"]}"/>')

    for r, (label, ic) in enumerate(steps):
        cy = top + head_h + 12 + row_h * (r + 0.5)
        tile = min(86, row_h - 26)
        tint = C[ICON_TINT.get(ic, "butter")]
        out.append(f'<rect x="{x0 + 34}" y="{cy - tile / 2:.1f}" width="{tile:.1f}" height="{tile:.1f}" rx="22" fill="{tint}"/>')
        out.append(icon(ic, x0 + 34 + tile / 2, cy, tile * 0.62, C["ink"], 2.0))
        out.append(text(x0 + 34 + tile + 24, cy + 13, label, "Fredoka", 600, 36, C["ink"], anchor="start"))
        for i in range(7):
            out.append(star(star_x0 + col * (i + 0.5), cy, min(46, col - 6), empty=True))
        if r < len(steps) - 1:
            out.append(f'<rect x="{x0 + 32}" y="{cy + row_h / 2 - 1:.1f}" width="{cw - 64}" height="2" fill="{C["line"]}"/>')

    # footer
    fy = 1400
    out.append(smiley_star(140, fy, 96))
    out.append(text(206, fy - 6, f"Made with {APP_NAME}: {APP_TAGLINE}", "Fredoka", 600, 34, C["ink"], anchor="start"))
    out.append(text(206, fy + 34, STORE_LINE, "Nunito", 700, 28, C["inkSoft"], anchor="start"))
    return svg_doc(W, H, "".join(out), th["bg"])


def make(p, out_dir):
    return render.save_png(pin_svg(p), os.path.join(out_dir, f'{p["slug"]}.png'))


if __name__ == "__main__":
    specs, out = cli.parse(__file__, "pins")
    for p in specs:
        print("rendered", make(p, out))
