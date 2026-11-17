"""Shared helpers: brand loading, colours, text fitting, shapes."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
APPS = ROOT / "apps"
OUT = ROOT / "out"
ENGINE_FONTS = Path(__file__).resolve().parent / "fonts"

DEFAULT_FONTS = {
    "heading": "Inter-ExtraBold.otf",
    "bold": "Inter-Bold.otf",
    "body": "Inter-Medium.otf",
}
REQUIRED_COLORS = ("bg_top", "bg_bottom", "ink", "muted", "primary", "on_primary", "accent", "card")


class SpecError(Exception):
    """A brand config or spec file is missing something or malformed."""


def hex_rgb(value: str) -> tuple[int, int, int]:
    v = value.lstrip("#")
    if len(v) != 6:
        raise SpecError(f"colour must be #RRGGBB, got {value!r}")
    return tuple(int(v[i : i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t: float):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise SpecError(f"{path.relative_to(ROOT)}: invalid JSON ({e})") from e


class Brand:
    def __init__(self, app: str):
        self.app = app
        self.dir = APPS / app
        cfg_path = self.dir / "brand.json"
        if not cfg_path.exists():
            raise SpecError(f"no brand config at apps/{app}/brand.json")
        self.cfg = load_json(cfg_path)
        self.name = self.cfg.get("name", app)
        self.cta = self.cfg.get("cta", "")
        self.cta_sub = self.cfg.get("cta_sub", "")
        self.handle = self.cfg.get("handle", "")
        self._fonts: dict = {}
        self.theme()  # validate default colours up front

    def theme(self, name: str | None = None) -> dict:
        """Base colours, optionally overridden by a named theme, as RGB tuples."""
        colors = dict(self.cfg.get("colors", {}))
        if name and name != "default":
            themes = self.cfg.get("themes", {})
            if name not in themes:
                raise SpecError(f"apps/{self.app}/brand.json has no theme {name!r}")
            colors.update(themes[name])
        missing = [k for k in REQUIRED_COLORS if k not in colors]
        if missing:
            raise SpecError(f"apps/{self.app}/brand.json colours missing: {', '.join(missing)}")
        return {k: hex_rgb(v) for k, v in colors.items()}

    def font(self, role: str, size: int) -> ImageFont.FreeTypeFont:
        key = (role, size)
        if key not in self._fonts:
            fname = {**DEFAULT_FONTS, **self.cfg.get("fonts", {})}[role]
            for base in (self.dir, ENGINE_FONTS):
                if (base / fname).exists():
                    self._fonts[key] = ImageFont.truetype(str(base / fname), size)
                    break
            else:
                raise SpecError(f"font {fname!r} not found in apps/{self.app}/ or engine/fonts/")
        return self._fonts[key]

    def wordmark(self, colors: dict, height: int) -> Image.Image:
        """Logo (or a lettered tile if there is no logo file) followed by the app name."""
        logo_file = self.cfg.get("logo")
        if logo_file:
            path = self.dir / logo_file
            if not path.exists():
                raise SpecError(f"logo {logo_file!r} not found in apps/{self.app}/")
            mark = Image.open(path).convert("RGBA")
            mark = mark.resize((round(mark.width * height / mark.height), height), Image.LANCZOS)
        else:
            mark = rounded((height, height), round(height * 0.28), colors["primary"])
            f = self.font("heading", round(height * 0.62))
            ImageDraw.Draw(mark).text(
                (height / 2, height / 2), self.name[:1].upper(), font=f, fill=colors["on_primary"], anchor="mm"
            )
        if self.cfg.get("logo_is_wordmark"):
            return mark
        f = self.font("heading", round(height * 0.66))
        tw = round(f.getlength(self.name))
        gap = round(height * 0.3)
        out = Image.new("RGBA", (mark.width + gap + tw + 4, height), (0, 0, 0, 0))
        out.alpha_composite(mark, (0, 0))
        name = Image.new("RGBA", out.size, colors["ink"] + (0,))
        ImageDraw.Draw(name).text((mark.width + gap, height / 2), self.name, font=f, fill=colors["ink"], anchor="lm")
        out.alpha_composite(name)
        return out


# ---------- shapes ----------

def rounded(size, radius: int, color, scale: int = 3) -> Image.Image:
    """Anti-aliased rounded rectangle as an RGBA layer."""
    w, h = size
    mask = Image.new("L", (w * scale, h * scale), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w * scale - 1, h * scale - 1), radius * scale, fill=255)
    layer = Image.new("RGBA", size, tuple(color) + (0,))
    layer.putalpha(mask.resize(size, Image.LANCZOS))
    return layer


def background(size, colors: dict) -> Image.Image:
    """Vertical gradient with two soft accent circles."""
    w, h = size
    grad = Image.linear_gradient("L").resize(size)
    bg = Image.composite(Image.new("RGB", size, colors["bg_bottom"]), Image.new("RGB", size, colors["bg_top"]), grad)
    bg = bg.convert("RGBA")
    blobs = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(blobs)
    r1, r2 = round(w * 0.42), round(w * 0.55)
    d.ellipse((w - r1, -r1 * 0.6, w + r1, r1 * 1.4), fill=colors["accent"] + (46,))
    d.ellipse((-r2, h - r2 * 0.9, r2 * 0.8, h + r2 * 0.9), fill=colors["primary"] + (30,))
    bg.alpha_composite(blobs)
    return bg.convert("RGB")


# ---------- text ----------

def wrap(text: str, font, max_w: int) -> list[str]:
    lines: list[str] = []
    for para in str(text).split("\n"):
        cur = ""
        for word in para.split():
            trial = f"{cur} {word}".strip()
            if cur and font.getlength(trial) > max_w:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        lines.append(cur)
    return lines


def text_layer(brand: Brand, text: str, role: str, size: int, max_w: int, fill, *,
               max_h: int | None = None, min_size: int = 28, align: str = "left",
               line_gap: float = 1.2) -> Image.Image:
    """Wrapped text on a transparent layer, shrunk until it fits max_w x max_h."""
    while True:
        font = brand.font(role, size)
        lines = wrap(text, font, max_w)
        line_h = round(size * line_gap)
        widest = max(font.getlength(line) for line in lines)
        fits = widest <= max_w and (max_h is None or line_h * len(lines) <= max_h)
        if fits or size <= min_size:
            break
        size -= 2
    width = max_w if align != "left" else max(1, round(widest) + 2)
    layer = Image.new("RGBA", (width, line_h * len(lines)), tuple(fill) + (0,))
    d = ImageDraw.Draw(layer)
    for i, line in enumerate(lines):
        y = i * line_h + line_h / 2
        if align == "center":
            d.text((width / 2, y), line, font=font, fill=fill, anchor="mm")
        else:
            d.text((0, y), line, font=font, fill=fill, anchor="lm")
    return layer


def pill(brand: Brand, text: str, size: int, bg, fg) -> Image.Image:
    font = brand.font("bold", size)
    label = text.upper()
    pad_x, h = round(size * 0.8), round(size * 1.9)
    w = round(font.getlength(label)) + pad_x * 2
    layer = rounded((w, h), h // 2, bg)
    ImageDraw.Draw(layer).text((w / 2, h / 2), label, font=font, fill=fg, anchor="mm")
    return layer


def numbered_card(brand: Brand, colors: dict, n: int, title: str, note: str | None, width: int, *,
                  height: int | None = None, title_size: int = 46, note_size: int = 32) -> Image.Image:
    """Rounded card: number badge on the left, title (and optional note) on the right."""
    pad = round(title_size * 0.7)
    badge = round(title_size * 1.7)
    text_w = width - badge - pad * 3
    budget = None if height is None else height - 28  # content is centred, so little padding is needed
    note_l = text_layer(brand, note, "body", note_size, text_w, colors["muted"],
                        max_h=None if budget is None else budget // 2) if note else None
    used = (note_l.height + 6) if note_l else 0
    title_l = text_layer(brand, title, "bold", title_size, text_w, colors["ink"],
                         max_h=None if budget is None else budget - used, line_gap=1.15)
    content_h = title_l.height + used
    h = height or max(badge, content_h) + pad * 2
    card = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    card.alpha_composite(rounded((width, h), round(pad * 1.1), colors["card"]))
    b = rounded((badge, badge), badge // 2, colors["primary"])
    ImageDraw.Draw(b).text((badge / 2, badge / 2), str(n), font=brand.font("heading", round(badge * 0.5)),
                           fill=colors["on_primary"], anchor="mm")
    card.alpha_composite(b, (pad, (h - badge) // 2))
    y = (h - content_h) // 2
    card.alpha_composite(title_l, (pad * 2 + badge, y))
    if note_l:
        card.alpha_composite(note_l, (pad * 2 + badge, y + title_l.height + 6))
    return card
