"""Publish rendered files to the public Cloudflare R2 bucket.

    python -m engine.upload            # every app that has files in out/
    python -m engine.upload spark      # one app
    python -m engine.upload spark --bucket other-bucket

Uploads out/<app>/** to <bucket>/<app>/..., plus apps/<app>/captions.md, and prints the
public URL of each file. With no app named, it also publishes the review dashboard
(out/index.html, from python -m engine.dashboard) as index.html. Every run refreshes
apps.json, the list of apps in the bucket that the dashboard shows. Needs CLOUDFLARE_API_TOKEN (a Cloudflare API token with
"Workers R2 Storage: Edit"). CLOUDFLARE_ACCOUNT_ID is optional; it is looked up if unset.
"""
import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
API = "https://api.cloudflare.com/client/v4"
BUCKET = "app-social-content"
PUBLIC_BASE = {"app-social-content": "https://pub-7639d3eca7d54cc4b5733370bb923e14.r2.dev"}


def _call(method, url, token, data=None, content_type=None):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if content_type:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        where = url.split("/client/v4")[-1]
        sys.exit(f"error: Cloudflare API {method} {where}: {e.code} {e.read()[:300].decode(errors='replace')}")
    except urllib.error.URLError as e:
        sys.exit(f"error: could not reach the Cloudflare API: {e.reason}")


def _account(token):
    if os.environ.get("CLOUDFLARE_ACCOUNT_ID"):
        return os.environ["CLOUDFLARE_ACCOUNT_ID"]
    accounts = _call("GET", f"{API}/accounts", token).get("result") or []
    if len(accounts) != 1:
        sys.exit(f"error: token sees {len(accounts)} Cloudflare accounts; set CLOUDFLARE_ACCOUNT_ID")
    return accounts[0]["id"]


def apps_in_bucket(account, bucket, token):
    """Names of every app that has a manifest.json in the bucket, whichever branch put it there."""
    apps, cursor = set(), None
    while True:
        url = f"{API}/accounts/{account}/r2/buckets/{bucket}/objects?per_page=1000"
        if cursor:
            url += "&cursor=" + urllib.parse.quote(cursor)
        page = _call("GET", url, token)
        for obj in page.get("result") or []:
            parts = obj.get("key", "").split("/")
            if len(parts) == 2 and parts[1] == "manifest.json":
                apps.add(parts[0])
        info = page.get("result_info") or {}
        cursor = info.get("cursor")
        if not cursor or not info.get("is_truncated"):
            return sorted(apps)


def files_for(app):
    """(local path, bucket key) for everything rendered for one app, plus its captions."""
    out_dir = os.path.join(ROOT, "out", app)
    pairs = []
    for folder, _, names in sorted(os.walk(out_dir)):
        for name in sorted(names):
            if name.startswith("."):
                continue
            path = os.path.join(folder, name)
            pairs.append((path, f"{app}/{os.path.relpath(path, out_dir).replace(os.sep, '/')}"))
    captions = os.path.join(ROOT, "apps", app, "captions.md")
    if pairs and os.path.exists(captions):
        pairs.append((captions, f"{app}/captions.md"))
    return pairs


def main():
    ap = argparse.ArgumentParser(description="Upload rendered files to Cloudflare R2.")
    ap.add_argument("apps", nargs="*", help="app names (default: every folder in out/)")
    ap.add_argument("--bucket", default=BUCKET)
    a = ap.parse_args()
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        sys.exit("error: set CLOUDFLARE_API_TOKEN to upload to R2")
    out_root = os.path.join(ROOT, "out")
    apps = a.apps or (sorted(d for d in os.listdir(out_root) if os.path.isdir(os.path.join(out_root, d)))
                      if os.path.isdir(out_root) else [])
    pairs = [pair for app in apps for pair in files_for(app)]
    if not pairs:
        sys.exit("error: nothing to upload; render first (python apps/<app>/clip.py and pin.py)")
    dashboard = os.path.join(out_root, "index.html")  # written by: python -m engine.dashboard
    if not a.apps and os.path.exists(dashboard):
        pairs.append((dashboard, "index.html"))
    account = _account(token)
    base = f"{API}/accounts/{account}/r2/buckets/{a.bucket}/objects/"
    public = PUBLIC_BASE.get(a.bucket, f"r2://{a.bucket}")
    for path, key in pairs:
        ctype = mimetypes.guess_type(path)[0] or ("text/markdown" if path.endswith(".md") else "application/octet-stream")
        if ctype.startswith("text/"):
            ctype += "; charset=utf-8"
        with open(path, "rb") as f:
            _call("PUT", base + urllib.parse.quote(key), token, f.read(), ctype)
        print(f"{public}/{key}")
    # The dashboard reads this to know which apps exist, across every branch that has published.
    listing = json.dumps({"apps": apps_in_bucket(account, a.bucket, token)}).encode()
    _call("PUT", base + "apps.json", token, listing, "application/json")
    print(f"uploaded {len(pairs)} file(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
