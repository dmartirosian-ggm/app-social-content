"""Timing, easing and small math helpers. Every frame is a function of time t (seconds)."""
import math


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, start, dur):
    """0..1 progress of an animation that starts at `start` and lasts `dur` (same units as t)."""
    return clamp((t - start) / dur) if dur > 0 else (1.0 if t >= start else 0.0)


def ease_out(p):
    return 1 - (1 - p) ** 3


def ease_in_out(p):
    return 3 * p * p - 2 * p * p * p


def back_out(p, s=1.9):
    p = p - 1
    return p * p * ((s + 1) * p + s) + 1


def pop(p):
    """Scale for a 'pop in': 0 -> overshoot -> 1."""
    return 0.0 if p <= 0 else back_out(p)


def bump(p, amount):
    """A single soft bounce: 0 -> amount -> 0 as p goes 0..1."""
    return math.sin(clamp(p) * math.pi) * amount


def mix(c1, c2, p):
    """Blend two #RRGGBB colors; p=0 gives c1, p=1 gives c2."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * p):02X}" for x, y in zip(a, b))


def rng(seed):
    """Tiny deterministic random generator so every render of a clip is identical."""
    state = [seed * 2654435761 % 2**32 or 1]

    def r():
        state[0] = (1103515245 * state[0] + 12345) % 2**31
        return state[0] / 2**31

    return r
