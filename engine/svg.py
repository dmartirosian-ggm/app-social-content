"""SVG building blocks: text with real line wrapping, transforms, the document wrapper.

Text is measured with the app's own font files, so call register_fonts() once from the
app's brand module before using text_width / wrap / text_block.
"""
import os
from functools import lru_cache
from xml.sax.saxutils import escape

from PIL import ImageFont

_FONTS = {}  # (family, weight) -> path to .ttf


def register_fonts(font_dir, files):
    """files: {("Fredoka", 700): "fredoka-latin-700-normal.ttf", ...}"""
    for key, name in files.items():
        _FONTS[key] = os.path.join(font_dir, name)
    _font.cache_clear()


@lru_cache(maxsize=None)
def _font(family, weight, size):
    try:
        path = _FONTS[(family, weight)]
    except KeyError:
        raise KeyError(f"font {family} {weight} is not registered; add it to the app's brand.py") from None
    return ImageFont.truetype(path, size)


def text_width(s, family, weight, size):
    return _font(family, weight, size).getlength(s)


def wrap(s, family, weight, size, max_w):
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_width(trial, family, weight, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text(x, y, s, family, weight, size, fill, anchor="middle", opacity=1.0, extra=""):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-weight="{weight}" '
        f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" opacity="{opacity:.3f}" {extra}>'
        f"{escape(s)}</text>"
    )


def text_block(cx, top, s, family, weight, size, fill, max_w, line_h=1.22, opacity=1.0, anchor="middle"):
    """Wrapped text; `top` is the top of the first line. "\\n" forces a break. Returns (svg, bottom_y)."""
    lines = [ln for part in s.split("\n") for ln in wrap(part, family, weight, size, max_w)]
    out, lh = [], size * line_h
    for i, ln in enumerate(lines):
        base = top + size * 0.82 + i * lh
        out.append(text(cx, base, ln, family, weight, size, fill, anchor, opacity))
    return "".join(out), top + len(lines) * lh


def group(inner, x=0, y=0, scale=1.0, opacity=1.0, rotate=0.0, origin=None):
    """Wrap svg in a transform. If origin=(ox,oy), scale/rotate happen around it."""
    if origin:
        ox, oy = origin
        tf = f"translate({x + ox:.2f} {y + oy:.2f}) rotate({rotate:.2f}) scale({scale:.4f}) translate({-ox:.2f} {-oy:.2f})"
    else:
        tf = f"translate({x:.2f} {y:.2f}) rotate({rotate:.2f}) scale({scale:.4f})"
    return f'<g transform="{tf}" opacity="{opacity:.3f}">{inner}</g>'


def path_icon(paths, cx, cy, size, color, stroke=2.0, box=24.0):
    """Line icon drawn from SVG path markup on a `box` x `box` grid (Lucide-style icons)."""
    s = size / box
    return (
        f'<g transform="translate({cx - size / 2:.2f} {cy - size / 2:.2f}) scale({s:.4f})" fill="none" '
        f'stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">'
        f"{paths}</g>"
    )


def svg_doc(w, h, inner, bg):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<rect width="{w}" height="{h}" fill="{bg}"/>{inner}</svg>'
    )
