"""Pinterest pins: 1000x1500 png with a title block and numbered step cards."""
from __future__ import annotations

from pathlib import Path

from .common import Brand, SpecError, background, numbered_card, pill, text_layer

W, H = 1000, 1500
MARGIN = 70
CONTENT_W = W - MARGIN * 2
FOOTER_H = 150
MAX_CARD_H, CARD_GAP = 200, 22


def render_pin(brand: Brand, spec: dict, out_dir: Path, where: str) -> Path:
    steps = spec.get("steps") or []
    if not spec.get("title") or not steps:
        raise SpecError(f"{where}: pin needs \"title\" and a non-empty \"steps\" list")
    colors = brand.theme(spec.get("theme"))
    canvas = background((W, H), colors).convert("RGBA")

    y = 80
    if spec.get("eyebrow"):
        p = pill(brand, spec["eyebrow"], 30, colors["primary"], colors["on_primary"])
        canvas.alpha_composite(p, (MARGIN, y))
        y += p.height + 30
    title = text_layer(brand, spec["title"], "heading", 88, CONTENT_W, colors["ink"],
                       max_h=300, min_size=52, line_gap=1.12)
    canvas.alpha_composite(title, (MARGIN, y))
    y += title.height + 16
    if spec.get("subtitle"):
        sub = text_layer(brand, spec["subtitle"], "body", 36, CONTENT_W, colors["muted"], max_h=100, line_gap=1.3)
        canvas.alpha_composite(sub, (MARGIN, y))
        y += sub.height + 16
    y += 24

    room = H - FOOTER_H - y
    card_h = min(MAX_CARD_H, (room - CARD_GAP * (len(steps) - 1)) // len(steps))
    if card_h < 96:
        raise SpecError(f"{where}: too many steps ({len(steps)}) to fit on one pin")
    y += (room - card_h * len(steps) - CARD_GAP * (len(steps) - 1)) // 2
    for i, step in enumerate(steps):
        if isinstance(step, str):
            step = {"title": step}
        card = numbered_card(brand, colors, i + 1, step["title"], step.get("note"), CONTENT_W,
                             height=card_h, title_size=44, note_size=30)
        canvas.alpha_composite(card, (MARGIN, y))
        y += card_h + CARD_GAP

    mark = brand.wordmark(colors, 64)
    fy = H - FOOTER_H + (FOOTER_H - mark.height) // 2
    canvas.alpha_composite(mark, (MARGIN, fy))
    footer = spec.get("footer", brand.cta)
    if footer:
        fw = CONTENT_W - mark.width - 40
        f = text_layer(brand, footer, "body", 28, fw, colors["muted"], max_h=80, min_size=20, line_gap=1.25)
        canvas.alpha_composite(f, (W - MARGIN - f.width, H - FOOTER_H + (FOOTER_H - f.height) // 2))

    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{spec['id']}.png"
    canvas.convert("RGB").save(path, optimize=True)
    return path
