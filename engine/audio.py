"""Soundtracks made in code (soft pads, plucks, chimes), so there is nothing to license."""
import wave

import numpy as np

SR = 44100


def timeline(dur):
    """Empty mono buffer for a clip `dur` seconds long, plus its time axis."""
    buf = np.zeros(int(SR * dur))
    return buf, np.arange(len(buf)) / SR


def tone(freq, dur, decay, harmonics=((1, 1.0), (2, 0.35), (3, 0.12))):
    """A plucked note that dies away over `decay` seconds."""
    n = int(SR * dur)
    t = np.arange(n) / SR
    env = np.exp(-t / decay) * np.minimum(1, t / 0.004)
    return sum(a * np.sin(2 * np.pi * freq * h * t) for h, a in harmonics) * env


def add(buf, start, sig, gain):
    """Mix `sig` into `buf` starting at `start` seconds."""
    i = int(start * SR)
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def pad(t, dur, freqs=((261.63, 1.0), (329.63, 0.7), (392.0, 0.6), (523.25, 0.25)), gain=0.035):
    """Soft chord that swells in and fades out at the end (C major by default)."""
    sig = sum(np.sin(2 * np.pi * f * t) * a for f, a in freqs)
    env = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 0.6) * (0.85 + 0.15 * np.sin(2 * np.pi * 0.5 * t))
    return sig * env * gain


def write_wav(path, buf, drive=1.7, ceiling=0.85):
    """Gentle limiter, then 16-bit mono WAV."""
    buf = np.tanh(buf * drive) * ceiling
    pcm = (buf * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
