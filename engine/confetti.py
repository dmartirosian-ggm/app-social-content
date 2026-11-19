"""Confetti effects. Pass the app's own palette as `colors`."""
import math

from .anim import clamp, rng


def _piece(i, col, w, h):
    if i % 3 == 0:
        return f'<circle cx="0" cy="0" r="{w * 0.55:.1f}" fill="{col}"/>'
    return f'<rect x="{-w / 2:.1f}" y="{-h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="{col}"/>'


def burst(t, start, cx, cy, colors, n=46, seed=7, spread=520):
    """Confetti burst from (cx, cy) starting at time `start` (seconds)."""
    if t < start:
        return ""
    r = rng(seed)
    dt = t - start
    out = []
    for i in range(n):
        ang = -math.pi / 2 + (r() - 0.5) * math.pi * 1.25
        speed = spread * (0.55 + r() * 0.75)
        vx, vy = math.cos(ang) * speed, math.sin(ang) * speed * 1.25
        x = cx + vx * dt
        y = cy + vy * dt + 0.5 * 1500 * dt * dt
        rot = (r() * 360 + dt * (200 + r() * 400) * (1 if i % 2 else -1))
        w, h = 14 + r() * 10, 22 + r() * 14
        fade = clamp(1.6 - dt) if dt > 0.6 else 1.0
        out.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})" opacity="{fade:.2f}">'
                   f'{_piece(i, colors[i % len(colors)], w, h)}</g>')
    return "".join(out)


def rain(t, start, colors, w=1080, n=52, seed=3):
    """Confetti falling from the top edge across the whole frame, starting at `start` (seconds)."""
    if t < start:
        return ""
    r = rng(seed)
    dt = t - start
    out = []
    for i in range(n):
        x0 = r() * w
        y0 = -40 - r() * 520
        v = 780 + r() * 620
        sway = 30 + r() * 40
        ph = r() * 6.28
        x = x0 + math.sin(ph + dt * 5) * sway
        y = y0 + v * dt
        rot = r() * 360 + dt * (240 + r() * 360) * (1 if i % 2 else -1)
        cw, ch = 14 + r() * 10, 24 + r() * 14
        out.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.1f})">'
                   f'{_piece(i, colors[i % len(colors)], cw, ch)}</g>')
    return "".join(out)
