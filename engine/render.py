"""Turn SVG into files: PNG/JPG stills, and MP4 video (frames piped to ffmpeg)."""
import io
import os
import subprocess
from multiprocessing import Pool

import cairosvg
from PIL import Image


def svg_to_png(svg):
    return cairosvg.svg2png(bytestring=svg.encode("utf-8"))


def save_png(svg, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=path)
    return path


def save_jpg(svg, path, quality=92):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    Image.open(io.BytesIO(svg_to_png(svg))).convert("RGB").save(path, quality=quality)
    return path


def _frame(args):
    frame_svg, t, params = args
    return svg_to_png(frame_svg(t, params))


def save_mp4(frame_svg, params, path, dur, fps=30, wav=None, workers=None):
    """frame_svg(t, params) -> svg string. It must be a top-level function so worker
    processes can find it. `wav` is an optional soundtrack file."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-i", "-"]
    if wav:
        cmd += ["-i", wav]
    cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium"]
    if wav:
        cmd += ["-c:a", "aac", "-b:a", "160k", "-shortest"]
    cmd += ["-movflags", "+faststart", path]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(dur * fps)
    with Pool(workers or os.cpu_count()) as pool:
        for png in pool.imap(_frame, [(frame_svg, i / fps, params) for i in range(n)], chunksize=4):
            ff.stdin.write(png)
    ff.stdin.close()
    if ff.wait() != 0:
        raise RuntimeError(f"ffmpeg failed for {path}")
    return path
