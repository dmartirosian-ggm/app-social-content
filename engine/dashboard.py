"""Build the review dashboard: one page showing every rendered clip and pin with its caption.

    python -m engine.dashboard        # writes out/index.html

Reads what is actually in out/<app>/, plus each app's specs and captions.md. The page uses
relative links, so it works opened from disk and from the root of the public bucket, where
engine.upload publishes it as index.html.
"""
import datetime
import html
import json
import os
import re
import subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "out")
CAPTION_HEAD = re.compile(r"^\*\*(.+?)\*\*\s*\(`([^`]+)`\)\s*$")


def captions_for(app):
    """{file name: (heading, caption text)} parsed from apps/<app>/captions.md."""
    path = os.path.join(ROOT, "apps", app, "captions.md")
    found, current = {}, None
    if not os.path.exists(path):
        return found
    with open(path, encoding="utf-8") as f:
        for line in f.read().splitlines():
            m = CAPTION_HEAD.match(line.strip())
            if m:
                current = m.group(2)
                found[current] = [m.group(1), []]
            elif line.startswith("#") or line.lower().startswith("link for every"):
                current = None
            elif current:
                found[current][1].append(line)
    return {name: (head, "\n".join(body).strip()) for name, (head, body) in found.items()}


def spec_for(app, kind, slug):
    path = os.path.join(ROOT, "apps", app, kind, slug + ".json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def collect():
    apps = []
    for app in sorted(os.listdir(OUT)) if os.path.isdir(OUT) else []:
        app_dir = os.path.join(OUT, app)
        if not os.path.isdir(app_dir):
            continue
        caps, items = captions_for(app), []
        for kind, ext in (("clips", ".mp4"), ("pins", ".png")):
            folder = os.path.join(app_dir, kind)
            for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
                if not name.endswith(ext) or name.startswith("."):
                    continue
                slug = name[: -len(ext)]
                spec = spec_for(app, kind, slug)
                head, caption = caps.get(name, ("", ""))
                title = head or spec.get("habit") or str(spec.get("title", "")).replace("\n", " ") or slug
                item = {"kind": kind[:-1], "slug": slug, "title": title, "caption": caption,
                        "src": f"{app}/{kind}/{name}"}
                cover = f"{slug}-cover.jpg"
                if kind == "clips" and os.path.exists(os.path.join(folder, cover)):
                    item["cover"] = f"{app}/{kind}/{cover}"
                items.append(item)
        if items:
            apps.append({"app": app, "items": items})
    return apps


def _git(*args):
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Content review</title>
<style>
:root{--bg:#f6f5f2;--card:#fff;--ink:#1c2233;--muted:#667089;--line:#e3e1db;--accent:#1f2a44;--on-accent:#fff;--chip:#ecebe6}
@media (prefers-color-scheme:dark){:root{--bg:#12151c;--card:#1b202b;--ink:#eef0f5;--muted:#9aa3b8;--line:#2b3242;--accent:#ffc93c;--on-accent:#1c2233;--chip:#252b38}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:14px 16px 10px}
.wrap{max-width:1280px;margin:0 auto}
h1{font-size:20px;margin:0}
.meta{color:var(--muted);font-size:13px;margin-top:2px}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.chip{border:0;border-radius:999px;background:var(--chip);color:var(--ink);padding:7px 14px;font:inherit;font-weight:600;font-size:13px;cursor:pointer}
.chip[aria-pressed=true]{background:var(--accent);color:var(--on-accent)}
.sep{width:1px;background:var(--line);margin:2px 4px}
main{padding:8px 16px 60px}
h2{font-size:17px;margin:26px 0 12px;text-transform:capitalize}
h2 span{color:var(--muted);font-weight:500;font-size:14px;text-transform:none}
.grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}
@media (max-width:560px){.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.body{padding:10px}.caption{font-size:12.5px}main{padding:8px 10px 60px}}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;display:flex;flex-direction:column}
.media{background:#000;display:block;width:100%}
.clip .media{aspect-ratio:9/16}
.pin .media{aspect-ratio:2/3;object-fit:cover;background:var(--chip)}
.body{padding:12px 14px 14px;display:flex;flex-direction:column;gap:8px;flex:1}
.tag{font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.title{font-weight:700;font-size:15px;line-height:1.3}
.file{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;color:var(--muted);word-break:break-all}
.caption{white-space:pre-wrap;font-size:13.5px;color:var(--ink);margin:0;overflow-wrap:anywhere}
.none{color:var(--muted);font-style:italic}
.actions{display:flex;flex-wrap:wrap;gap:6px;margin-top:auto;padding-top:6px}
.btn{border:1px solid var(--line);background:transparent;color:var(--ink);border-radius:8px;padding:6px 10px;font:inherit;font-size:12.5px;font-weight:600;cursor:pointer;text-decoration:none}
.btn:hover{background:var(--chip)}
.empty{color:var(--muted);padding:40px 0;text-align:center}
</style>
</head>
<body>
<header><div class="wrap">
<h1>Content review</h1>
<div class="meta" id="meta"></div>
<div class="filters" id="filters"></div>
</div></header>
<main><div class="wrap" id="main"></div></main>
<script>
const DATA = __DATA__;
const state = {app: "all", kind: "all"};
const el = (tag, attrs = {}, ...kids) => {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) k === "text" ? n.textContent = v : n.setAttribute(k, v);
  n.append(...kids);
  return n;
};
const v = DATA.version ? "?v=" + DATA.version : "";
const abs = rel => new URL(rel, location.href).href.split("?")[0];
function copy(btn, text) {
  const done = () => { const t = btn.textContent; btn.textContent = "Copied"; setTimeout(() => btn.textContent = t, 1200); };
  if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, () => prompt("Copy:", text));
  else prompt("Copy:", text);
}
function card(item) {
  let media;
  if (item.kind === "clip") {
    media = el("video", {class: "media", controls: "", playsinline: "", preload: "none", src: item.src + v});
    if (item.cover) media.setAttribute("poster", item.cover + v);
  } else {
    media = el("a", {href: item.src + v, target: "_blank", rel: "noopener"},
      el("img", {class: "media", loading: "lazy", alt: item.title, src: item.src + v}));
  }
  const cap = item.caption ? el("p", {class: "caption", text: item.caption}) : el("p", {class: "caption none", text: "No caption found in captions.md"});
  const actions = el("div", {class: "actions"});
  if (item.caption) { const b = el("button", {class: "btn", text: "Copy caption"}); b.onclick = () => copy(b, item.caption); actions.append(b); }
  const l = el("button", {class: "btn", text: "Copy link"}); l.onclick = () => copy(l, abs(item.src)); actions.append(l);
  actions.append(el("a", {class: "btn", href: item.src + v, target: "_blank", rel: "noopener", text: "Open"}));
  return el("article", {class: "card " + item.kind}, media,
    el("div", {class: "body"}, el("div", {class: "tag", text: item.kind}), el("div", {class: "title", text: item.title}),
      el("div", {class: "file", text: item.src.split("/").pop()}), cap, actions));
}
function chip(label, group, value) {
  const b = el("button", {class: "chip", "aria-pressed": String(state[group] === value), text: label});
  b.onclick = () => { state[group] = value; render(); };
  return b;
}
function render() {
  const f = document.getElementById("filters"); f.replaceChildren();
  if (DATA.apps.length > 1) {
    f.append(chip("All apps", "app", "all"), ...DATA.apps.map(a => chip(a.app, "app", a.app)), el("span", {class: "sep"}));
  }
  f.append(chip("Everything", "kind", "all"), chip("Clips", "kind", "clip"), chip("Pins", "kind", "pin"));
  const main = document.getElementById("main"); main.replaceChildren();
  let shown = 0;
  for (const a of DATA.apps) {
    if (state.app !== "all" && state.app !== a.app) continue;
    const items = a.items.filter(i => state.kind === "all" || i.kind === state.kind);
    if (!items.length) continue;
    shown += items.length;
    const clips = items.filter(i => i.kind === "clip").length, pins = items.length - clips;
    const counts = [clips && clips + " clip" + (clips > 1 ? "s" : ""), pins && pins + " pin" + (pins > 1 ? "s" : "")].filter(Boolean).join(", ");
    main.append(el("h2", {}, a.app.replace(/-/g, " ") + " ", el("span", {text: counts})), el("div", {class: "grid"}, ...items.map(card)));
  }
  if (!shown) main.append(el("div", {class: "empty", text: "Nothing to show for this filter."}));
}
const total = DATA.apps.reduce((n, a) => n + a.items.length, 0);
document.getElementById("meta").textContent = total + " files · published " + new Date(DATA.built).toLocaleString() + (DATA.commit ? " · " + DATA.branch + " @ " + DATA.commit : "");
render();
</script>
</body>
</html>
"""


def build():
    data = {
        "apps": collect(),
        "built": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "commit": os.environ.get("GITHUB_SHA", "")[:7] or _git("rev-parse", "--short", "HEAD"),
        "branch": os.environ.get("GITHUB_REF_NAME") or _git("rev-parse", "--abbrev-ref", "HEAD"),
    }
    data["version"] = re.sub(r"\D", "", data["built"])[-10:]
    # "</" must not appear inside the inline script, or a caption could end it early.
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(PAGE.replace("__DATA__", payload))
    return path, sum(len(a["items"]) for a in data["apps"])


if __name__ == "__main__":
    path, count = build()
    print(f"dashboard with {count} item(s): {html.escape(path)}")
