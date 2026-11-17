"""Upload rendered files in out/<app>/ (plus the app's captions.md) to Cloudflare R2.

Uses the Cloudflare REST API, so it needs CLOUDFLARE_API_TOKEN (a token with
"Workers R2 Storage: Edit"). CLOUDFLARE_ACCOUNT_ID is optional; it is looked up if unset.
"""
from __future__ import annotations

import json
import mimetypes
import os
import urllib.error
import urllib.parse
import urllib.request

from .common import APPS, OUT, SpecError

API = "https://api.cloudflare.com/client/v4"
DEFAULT_BUCKET = "app-social-content"


def _call(method: str, url: str, token: str, data: bytes | None = None, content_type: str | None = None) -> dict:
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if content_type:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as e:
        raise SpecError(f"Cloudflare API {method} {url.split('/client/v4')[-1]}: {e.code} {e.read()[:300].decode(errors='replace')}") from e
    except urllib.error.URLError as e:
        raise SpecError(f"could not reach Cloudflare API: {e.reason}") from e


def _account(token: str) -> str:
    if os.environ.get("CLOUDFLARE_ACCOUNT_ID"):
        return os.environ["CLOUDFLARE_ACCOUNT_ID"]
    accounts = _call("GET", f"{API}/accounts", token).get("result") or []
    if len(accounts) != 1:
        raise SpecError(f"token sees {len(accounts)} Cloudflare accounts; set CLOUDFLARE_ACCOUNT_ID")
    return accounts[0]["id"]


def upload(app: str, bucket: str = DEFAULT_BUCKET) -> list[str]:
    """Upload out/<app>/** to <bucket>/<app>/..., returning the object keys."""
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        raise SpecError("set CLOUDFLARE_API_TOKEN to upload to R2")
    files = [(p, f"{app}/{p.relative_to(OUT / app).as_posix()}") for p in sorted((OUT / app).rglob("*")) if p.is_file()]
    if not files:
        raise SpecError(f"nothing in out/{app}/ to upload; run: python -m engine render {app}")
    captions = APPS / app / "captions.md"
    if captions.exists():
        files.append((captions, f"{app}/captions.md"))
    base = f"{API}/accounts/{_account(token)}/r2/buckets/{bucket}/objects/"
    keys = []
    for path, key in files:
        ctype = mimetypes.guess_type(path.name)[0] or ("text/markdown" if path.suffix == ".md" else "application/octet-stream")
        _call("PUT", base + urllib.parse.quote(key), token, path.read_bytes(), ctype)
        print(f"  r2://{bucket}/{key}")
        keys.append(key)
    return keys
