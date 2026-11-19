"""Command line shared by every app's clip.py / pin.py.

    python apps/<app>/clip.py                       # render every spec in apps/<app>/clips/
    python apps/<app>/clip.py apps/<app>/clips/01-x.json [more.json ...]
    python apps/<app>/clip.py ... --out some/folder # default: out/<app>/clips/

Rendered files go in out/, which git ignores.
"""
import argparse
import glob
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def parse(script_file, kind):
    """Returns (specs, out_dir). `kind` is the spec folder name: "clips" or "pins"."""
    app_dir = os.path.dirname(os.path.abspath(script_file))
    app = os.path.basename(app_dir)
    ap = argparse.ArgumentParser(description=f"Render {app} {kind}.")
    ap.add_argument("specs", nargs="*", help=f"JSON spec files (default: all of apps/{app}/{kind}/*.json)")
    ap.add_argument("--out", default=os.path.join(ROOT, "out", app, kind), help="output folder")
    a = ap.parse_args()
    paths = a.specs or sorted(glob.glob(os.path.join(app_dir, kind, "*.json")))
    if not paths:
        ap.error(f"no specs found in apps/{app}/{kind}/")
    specs = []
    for path in paths:
        with open(path) as f:
            p = json.load(f)
        p.setdefault("slug", os.path.splitext(os.path.basename(path))[0])
        specs.append(p)
    return specs, a.out
