"""Short vertical clips: 1080x1920 mp4 (H.264 + silent AAC) and a cover jpg."""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

from .common import Brand, SpecError, background, mix, numbered_card, pill, text_layer

W, H, FPS = 1080, 1920, 30
MARGIN = 90
CONTENT_W = W - MARGIN * 2
# Keep text clear of the platform UI: top bar and the bottom caption/buttons area.
SAFE_TOP, SAFE_BOTTOM = 300, 1480
FADE_IN, FADE_OUT, SLIDE = 0.45, 0.3, 50
DEFAULT_DURATION = {"title": 3.0, "list": 5.0, "cta": 2.5}


@dataclass
class Element:
    rgb: Image.Image
    alpha: Image.Image
    x: int
    y: int
    t_in: float


def _stack(layers, gaps, align="center"):
    """Vertically centre a column of (layer, t_in) in the safe area."""
    total = sum(l.height for l, _ in layers) + sum(gaps[: len(layers) - 1])
    y = SAFE_TOP + max(0, (SAFE_BOTTOM - SAFE_TOP - total) // 2)
    out = []
    for i, (layer, t_in) in enumerate(layers):
        x = (W - layer.width) // 2 if align == "center" else MARGIN
        out.append(Element(layer.convert("RGB"), layer.getchannel("A"), x, y, t_in))
        y += layer.height + (gaps[i] if i < len(gaps) else 0)
    return out


def build_scene(brand: Brand, colors: dict, scene: dict, where: str) -> list[Element]:
    kind = scene.get("type", "title")
    duration = scene_duration(scene)
    if kind == "title":
        if not scene.get("text"):
            raise SpecError(f"{where}: title scene needs \"text\"")
        layers = []
        if scene.get("eyebrow"):
            layers.append((pill(brand, scene["eyebrow"], 36, colors["primary"], colors["on_primary"]), 0.0))
        layers.append((text_layer(brand, scene["text"], "heading", 104, CONTENT_W, colors["ink"],
                                  max_h=640, min_size=56, align="center", line_gap=1.14), 0.15))
        if scene.get("sub"):
            layers.append((text_layer(brand, scene["sub"], "body", 46, CONTENT_W - 60, colors["muted"],
                                      max_h=300, align="center", line_gap=1.3), 0.55))
        return _stack(layers, [44, 44])
    if kind == "list":
        items = scene.get("items") or []
        if not items:
            raise SpecError(f"{where}: list scene needs \"items\"")
        layers = []
        if scene.get("heading"):
            layers.append((text_layer(brand, scene["heading"], "heading", 76, CONTENT_W, colors["ink"],
                                      max_h=280, min_size=48, line_gap=1.14), 0.0))
        step = min(0.8, max(0.25, (duration - 1.8) / len(items)))
        for i, item in enumerate(items):
            layers.append((numbered_card(brand, colors, i + 1, item, None, CONTENT_W), 0.4 + i * step))
        return _stack(layers, [50] + [26] * len(items), align="left")
    if kind == "cta":
        text = scene.get("text") or brand.cta
        layers = [(brand.wordmark(colors, 150), 0.0)]
        if text:
            layers.append((text_layer(brand, text, "heading", 76, CONTENT_W, colors["ink"],
                                      max_h=420, min_size=48, align="center", line_gap=1.16), 0.25))
        sub = scene.get("sub") or brand.handle
        if sub:
            layers.append((text_layer(brand, sub, "body", 44, CONTENT_W, colors["muted"], align="center"), 0.55))
        return _stack(layers, [70, 36])
    raise SpecError(f"{where}: unknown scene type {kind!r} (use title, list or cta)")


def scene_duration(scene: dict) -> float:
    return float(scene.get("duration", DEFAULT_DURATION.get(scene.get("type", "title"), 3.0)))


def _ease(t: float) -> float:
    t = min(1.0, max(0.0, t))
    return 1 - (1 - t) ** 3


def compose(bg: Image.Image, elements: list[Element], t: float, duration: float, last: bool) -> Image.Image:
    frame = bg.copy()
    out = 1.0 if last else 1 - min(1.0, max(0.0, (t - (duration - FADE_OUT)) / FADE_OUT))
    for e in elements:
        a_in = _ease((t - e.t_in) / FADE_IN)
        a = a_in * out
        if a <= 0.004:
            continue
        mask = e.alpha if a >= 0.996 else e.alpha.point(lambda v, a=a: int(v * a))
        frame.paste(e.rgb, (e.x, e.y + round((1 - a_in) * SLIDE)), mask)
    return frame


def _progress(frame: Image.Image, colors: dict, durations: list[float], index: int, t: float):
    """Story-style segmented progress bar across the top."""
    d = ImageDraw.Draw(frame)
    n, gap, x0, y, h = len(durations), 10, 60, 84, 8
    seg = (W - x0 * 2 - gap * (n - 1)) / n
    track = mix(colors["bg_top"], colors["ink"], 0.18)
    for i in range(n):
        x = x0 + i * (seg + gap)
        d.rounded_rectangle((x, y, x + seg, y + h), h // 2, fill=track)
        frac = 1.0 if i < index else (min(1.0, t / durations[i]) if i == index else 0.0)
        if frac > 0:
            d.rounded_rectangle((x, y, x + max(h, seg * frac), y + h), h // 2, fill=colors["ink"])


def render_clip(brand: Brand, spec: dict, out_dir: Path, where: str) -> Path:
    if not shutil.which("ffmpeg"):
        raise SpecError("ffmpeg is not installed (needed to encode clips)")
    scenes = spec.get("scenes") or []
    if not scenes:
        raise SpecError(f"{where}: clip needs a non-empty \"scenes\" list")
    colors = brand.theme(spec.get("theme"))
    plain = background((W, H), colors)
    marked = plain.copy()
    mark = brand.wordmark(colors, 60)
    marked.paste(mark, (60, 130), mark)

    built = [build_scene(brand, colors, s, f"{where} scene {i + 1}") for i, s in enumerate(scenes)]
    durations = [scene_duration(s) for s in scenes]

    out_dir.mkdir(parents=True, exist_ok=True)
    mp4 = out_dir / f"{spec['id']}.mp4"
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(mp4),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for i, (scene, elements, dur) in enumerate(zip(scenes, built, durations)):
            bg = plain if scene.get("type") == "cta" else marked
            for f in range(round(dur * FPS)):
                t = f / FPS
                frame = compose(bg, elements, t, dur, last=i == len(scenes) - 1)
                _progress(frame, colors, durations, i, t)
                proc.stdin.write(frame.tobytes())
        proc.stdin.close()
    except BrokenPipeError:
        pass
    err = proc.stderr.read().decode()
    if proc.wait() != 0:
        raise SpecError(f"{where}: ffmpeg failed: {err.strip()}")

    # Cover: the "cover" scene if given, else the first scene, fully revealed.
    cover_scene = spec.get("cover")
    cover_els = build_scene(brand, colors, {"type": "title", **cover_scene}, f"{where} cover") if cover_scene else built[0]
    compose(marked, cover_els, 99.0, 1.0, last=True).save(out_dir / f"{spec['id']}.jpg", quality=92)
    return mp4
