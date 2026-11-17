"""CLI: python -m engine render|upload <app> ...  (see README)"""
from __future__ import annotations

import argparse
import sys

from .clips import render_clip
from .common import APPS, OUT, ROOT, Brand, SpecError, load_json
from .pins import render_pin
from .upload import DEFAULT_BUCKET, upload

KINDS = {"clips": render_clip, "pins": render_pin}


def apps() -> list[str]:
    return sorted(p.parent.name for p in APPS.glob("*/brand.json"))


def render(app: str, kinds: list[str], only: list[str]) -> int:
    brand = Brand(app)
    done, seen = 0, set()
    for kind in kinds:
        for path in sorted((brand.dir / kind).glob("*.json")):
            where = str(path.relative_to(ROOT))
            spec = load_json(path)
            spec.setdefault("id", path.stem)
            if only and spec["id"] not in only:
                continue
            if (kind, spec["id"]) in seen:
                raise SpecError(f"{where}: duplicate id {spec['id']!r}")
            seen.add((kind, spec["id"]))
            out = KINDS[kind](brand, spec, OUT / app / kind, where)
            print(f"  {out.relative_to(ROOT)}")
            done += 1
    return done


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m engine")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="list apps that have a brand config")
    r = sub.add_parser("render", help="render an app's clips and pins into out/<app>/")
    r.add_argument("app", help="app folder name under apps/, or 'all'")
    r.add_argument("--clips", action="store_true", help="render only clips")
    r.add_argument("--pins", action="store_true", help="render only pins")
    r.add_argument("--only", nargs="+", default=[], metavar="ID", help="render only these spec ids")
    u = sub.add_parser("upload", help="upload out/<app>/ and captions.md to Cloudflare R2")
    u.add_argument("app", help="app folder name under apps/, or 'all'")
    u.add_argument("--bucket", default=DEFAULT_BUCKET, help=f"R2 bucket (default: {DEFAULT_BUCKET})")
    args = parser.parse_args()

    if args.cmd == "list":
        print("\n".join(apps()))
        return 0
    if args.cmd == "upload":
        try:
            n = 0
            for app in apps() if args.app == "all" else [args.app]:
                print(f"{app}:")
                n += len(upload(app, args.bucket))
        except SpecError as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        print(f"uploaded {n} file(s)")
        return 0
    kinds = [k for k in KINDS if getattr(args, k)] or list(KINDS)
    targets = apps() if args.app == "all" else [args.app]
    try:
        total = 0
        for app in targets:
            print(f"{app}:")
            total += render(app, kinds, args.only)
    except SpecError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if not total:
        print("error: nothing matched", file=sys.stderr)
        return 1
    print(f"rendered {total} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
