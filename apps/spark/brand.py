"""Spark's look: colors, fonts, icons and the small shapes its clips and pins share.

Colors, fonts and icons are copied from the Spark app itself
(src/theme/tokens.ts, src/components/icons.tsx, src/components/stars.tsx),
so the videos and pins look like the app.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from engine.svg import path_icon, register_fonts, text, text_width  # noqa: E402

APP_NAME = "Spark"
APP_TAGLINE = "Chore & Reward Chart"
STORE_LINE = "Free on the App Store"

C = {
    "ink": "#1F2A44",
    "inkSoft": "#3B4A6B",
    "muted": "#55627D",
    "ground": "#F3F6FB",
    "card": "#FFFFFF",
    "line": "#E4E9F2",
    "border": "#D9E0EC",
    "ringEmpty": "#C9D2E2",
    "spark": "#FFC93C",
    "success": "#2E9E6A",
    "sky": "#DCEBFF",
    "peach": "#FFE3D8",
    "butter": "#FFF1C7",
    "mint": "#D9F2E6",
    "lilac": "#E9E2FF",
    "white": "#FFFFFF",
}
CHILD_COLORS = ["#FFB4A2", "#A8DADC", "#FFC93C", "#7FD1AE", "#C9B8FF"]
CONFETTI = ["#FFC93C", "#FFB4A2", "#A8DADC", "#7FD1AE", "#C9B8FF", "#2E9E6A"]

# icon name -> tint, as in the app's HABIT_ICONS catalog
ICON_TINT = {
    "tooth": "sky", "shirt": "peach", "bowl": "butter", "toys": "mint", "hands": "sky",
    "book": "lilac", "potty": "peach", "sleep": "lilac", "shoes": "butter", "bath": "sky",
    "water": "mint", "vegetables": "mint", "backpack": "peach", "kind": "lilac", "star": "butter",
}

with open(os.path.join(HERE, "icons.json")) as f:
    ICONS = json.load(f)

register_fonts(os.path.join(HERE, "fonts"), {
    ("Fredoka", 500): "fredoka-latin-500-normal.ttf",
    ("Fredoka", 600): "fredoka-latin-600-normal.ttf",
    ("Fredoka", 700): "fredoka-latin-700-normal.ttf",
    ("Nunito", 600): "nunito-latin-600-normal.ttf",
    ("Nunito", 700): "nunito-latin-700-normal.ttf",
    ("Nunito", 800): "nunito-latin-800-normal.ttf",
})

STAR_PATH = "M12 2.6l2.9 5.9 6.5.95-4.7 4.6 1.1 6.45L12 17.45 6.2 20.5l1.1-6.45-4.7-4.6 6.5-.95z"
SMILEY_STAR = "M60 10l14.7 29.8 32.9 4.8-23.8 23.2 5.6 32.8L60 85.1 30.6 100.6l5.6-32.8L12.4 44.6l32.9-4.8z"


def icon(name, cx, cy, size, color=C["ink"], stroke=2.0):
    return path_icon(ICONS[name], cx, cy, size, color, stroke)


def star(cx, cy, size, empty=False):
    s = size / 24.0
    fill = "#EEF2F8" if empty else C["spark"]
    stroke = C["ringEmpty"] if empty else C["ink"]
    sw = 1.3 if empty else 1.6
    return (
        f'<g transform="translate({cx - size / 2:.2f} {cy - size / 2:.2f}) scale({s:.4f})">'
        f'<path d="{STAR_PATH}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/></g>'
    )


def smiley_star(cx, cy, size):
    s = size / 120.0
    return (
        f'<g transform="translate({cx - size / 2:.2f} {cy - size / 2:.2f}) scale({s:.4f})">'
        f'<path d="{SMILEY_STAR}" fill="{C["spark"]}" stroke="{C["ink"]}" stroke-width="6" stroke-linejoin="round"/>'
        f'<circle cx="50" cy="56" r="4.5" fill="{C["ink"]}"/><circle cx="70" cy="56" r="4.5" fill="{C["ink"]}"/>'
        f'<path d="M47 67c7 7 19 7 26 0" fill="none" stroke="{C["ink"]}" stroke-width="4.5" stroke-linecap="round"/></g>'
    )


def card(x, y, w, h, r=40, fill=C["card"], shadow=True):
    sh = ""
    if shadow:
        sh = f'<rect x="{x:.1f}" y="{y + 14:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{C["ink"]}" opacity="0.06"/>'
    return sh + f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" fill="{fill}"/>'


def pill(cx, cy, label, size, fill=C["card"], color=C["ink"], weight=800, family="Nunito", pad_x=34, pad_y=18,
         icon_name=None, icon_color=None):
    tw = text_width(label, family, weight, size)
    iw = size * 1.15 if icon_name else 0
    gap = size * 0.35 if icon_name else 0
    w, h = tw + iw + gap + pad_x * 2, size + pad_y * 2
    x0 = cx - w / 2
    out = f'<rect x="{x0:.1f}" y="{cy - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{h / 2:.1f}" fill="{fill}"/>'
    tx = x0 + pad_x
    if icon_name:
        out += icon(icon_name, tx + iw / 2, cy, iw, icon_color or color, 2.2)
        tx += iw + gap
    out += text(tx, cy + size * 0.35, label, family, weight, size, color, anchor="start")
    return out


def avatar(cx, cy, r, letter, color):
    return (
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{color}"/>'
        + text(cx, cy + r * 0.36, letter, "Nunito", 800, int(r * 1.0), C["ink"])
    )
