"""Galaxy Growth Media videos, made with Remotion.

GGM's videos are built in React with Remotion (apps/ggm/remotion/), not with the shared
SVG engine, because the laptop and dashboard look needs CSS layout and 3D. This script is
the bridge: it reads the JSON specs like every other app and writes the same outputs
(out/ggm/clips/<slug>.mp4 and <slug>-cover.jpg), so the dashboard and upload work as usual.

    python apps/ggm/clip.py                                   # every GGM video
    python apps/ggm/clip.py apps/ggm/clips/01-wheel-rush-miami.json

Needs Node.js 18 or newer and ffmpeg. The first run installs the npm packages and
Remotion's headless Chrome.

Clip JSON:
{
  "title": "Shown on the review page",
  "composition": "Ugc" or "TipLight",
  "props": { ...the composition's props, see remotion/src/UgcResults.tsx and TipLight.tsx }
}
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
from engine import cli  # noqa: E402

PROJECT = os.path.join(HERE, "remotion")


def run(cmd, **kw):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, **kw)


def ensure_packages():
    if os.path.isdir(os.path.join(PROJECT, "node_modules", "remotion")):
        return
    npm = shutil.which("npm") or sys.exit("error: npm not found; install Node.js 18 or newer")
    run([npm, "ci", "--no-audit", "--no-fund"], cwd=PROJECT)


def render(spec, out_dir):
    slug = spec["slug"]
    mp4 = os.path.join(out_dir, slug + ".mp4")
    cover = os.path.join(out_dir, slug + "-cover.jpg")
    npx = shutil.which("npx") or sys.exit("error: npx not found; install Node.js 18 or newer")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(spec["props"], f)
        props = f.name
    try:
        run([npx, "remotion", "render", "src/index.ts", spec["composition"], mp4,
             f"--props={props}", "--codec=h264", "--log=warn"], cwd=PROJECT)
    finally:
        os.unlink(props)
    # Cover: a frame a few seconds in, once the dashboard or the first step is on screen.
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "4", "-i", mp4, "-frames:v", "1", "-q:v", "3", cover])
    print(mp4)


def main():
    specs, out_dir = cli.parse(__file__, "clips")
    os.makedirs(out_dir, exist_ok=True)
    ensure_packages()
    for spec in specs:
        render(spec, out_dir)


if __name__ == "__main__":
    main()
