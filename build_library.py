#!/usr/bin/env python3
"""Turn my Zotero library into a card hub + one page per top-level folder.

The library lives in the Mycelium_Zotero repo, which refreshes library.json from Zotero every
morning. This script reads it and writes, in the same style as build_topics.py:

    resources/library.qmd             the hub, one card per top-level Zotero folder
    resources/library/<folder>.qmd    one page per folder: its subfolders as sections, papers and books listed

Run from the project root (the publish workflow does this for you before every build):

    python3 build_library.py                      # reads the live library.json from GitHub
    python3 build_library.py path/to/library.json # or a local copy (or another URL)

Don't edit the generated files by hand; change things in Zotero.

Card images: drop  resources/assets/topics/library-<folder-name>.jpg  (the script prints the exact
names it looks for). Folders without one fall back to resources/assets/library.jpg.
"""
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RES = ROOT / "resources"
OUT = RES / "library"

DEFAULT_SOURCE = "https://raw.githubusercontent.com/ellacapellini/Mycelium_Zotero/main/library.json"
BIB_URL = "https://raw.githubusercontent.com/ellacapellini/Mycelium_Zotero/main/library.bib"
REPO_URL = "https://github.com/ellacapellini/Mycelium_Zotero"

ORDER = []        # pin cards to the front, e.g. ["Neural Dynamics & TRF Modelling"]; the rest are A to Z
PEEK_MAX = 5      # how many items the hover preview lists
SUBS_IN_META = 3  # how many subfolder names the card shows under its title
FENCE = "`" * 3


# ---------------------------------------------------------------- helpers
def slugify(text):
    text = text.lower().replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-") or "folder"


def plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


def md(text):
    """Make Zotero text safe for Markdown/pandoc (titles can hold $, *, _, [ ] and HTML tags)."""
    text = re.sub(r"</?(i|b|em|strong|sub|sup|span|p)[^>]*>", "", text or "")
    text = html.escape(text, quote=False)
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"([\\`*_\[\]$|#~^])", r"\\\1", text)


def year(item):
    m = re.search(r"\d{4}", item.get("date", ""))
    return m.group(0) if m else ""


def authors(item):
    people = [c for c in item.get("creators", []) if c.get("creatorType") in ("author", "editor")]
    names = []
    for c in people:
        if c.get("lastName"):
            first = c.get("firstName", "")
            names.append(c["lastName"] + (f", {first[0]}." if first else ""))
        elif c.get("name"):
            names.append(c["name"])
    return "; ".join(names[:3]) + (" et al." if len(names) > 3 else "")


def link(item):
    if item.get("DOI"):
        return "https://doi.org/" + item["DOI"].strip()
    return item.get("url", "").strip()


def venue(item):
    for k in ("publicationTitle", "bookTitle", "proceedingsTitle", "repository", "publisher"):
        if item.get(k):
            return item[k]
    return ""


def item_line(item):
    title = md(item.get("title") or "(untitled)")
    url = link(item)
    head = f"[{title}]({url})" if url else f"*{title}*"
    tail = [md(authors(item)), md(year(item)), (f"*{md(venue(item))}*" if venue(item) else "")]
    line = f"- {head}" + "".join(f", {t}" for t in tail if t)
    abstract = md(item.get("abstractNote", ""))
    if abstract:
        line += f"\n  <details><summary>Abstract</summary>{abstract}</details>"
    return line


def sort_items(items):
    return sorted(items, key=lambda i: (year(i) or "0", i.get("title", "")), reverse=True)


# ---------------------------------------------------------------- loading
def read_source(src):
    if re.match(r"https?://", src):
        with urllib.request.urlopen(src, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    return json.loads(Path(src).read_text(encoding="utf-8"))


class Node:
    def __init__(self, name):
        self.name, self.children, self.items = name, [], []

    def everything(self):
        seen, out = set(), []

        def walk(n):
            for i in n.items:
                if i["key"] not in seen:
                    seen.add(i["key"])
                    out.append(i)
            for c in n.children:
                walk(c)

        walk(self)
        return out


def build_tree(data):
    """Return the top-level Nodes. Understands library.json with a `collections` list (folder keys),
    and older exports where each item carries its folders as 'Parent/Child' paths."""
    nodes, top = {}, []
    if "collections" in data:
        for c in data["collections"]:
            nodes[c["key"]] = Node(c["name"])
        for c in data["collections"]:
            (nodes[c["parent"]].children if c.get("parent") in nodes else top).append(nodes[c["key"]])
        for it in data["items"]:
            for k in it.get("collections", []):
                if k in nodes:
                    nodes[k].items.append(it)
    else:
        def get(path):
            if path not in nodes:
                nodes[path] = Node(path.split("/")[-1])
                (nodes[path.rsplit("/", 1)[0]].children if "/" in path else top).append(nodes[path])
            return nodes[path]

        for it in data["items"]:
            for p in it.get("collections", []):
                parts = p.split("/")
                for i in range(1, len(parts) + 1):
                    get("/".join(parts[:i]))
                nodes[p].items.append(it)

    def order(ns, first=()):
        ns.sort(key=lambda n: (first.index(n.name) if n.name in first else len(first), n.name.lower()))
        for n in ns:
            order(n.children)

    order(top, ORDER)
    unfiled = [i for i in data["items"] if not i.get("collections")]
    return top, unfiled


# ---------------------------------------------------------------- pages
def section(node, depth, lines):
    """Write a folder's own items, then its subfolders as ##/###/#### sections."""
    for it in sort_items(node.items):
        lines.append(item_line(it))
    for child in node.children:
        lines += ["", f"{'#' * min(depth, 5)} {md(child.name)}", ""]
        section(child, depth + 1, lines)


def write_topic(node, slug):
    n = len(node.everything())
    lines = []
    section(node, 2, lines)
    title = node.name.replace('"', '\\"')
    page = (
        f'---\ntitle: "{title}"\n'
        f'description: "{plural(n, "item")}"\n'
        f"toc: true\ntoc-depth: 3\n---\n\n"
        f"[← Library](../library.qmd)\n\n" + "\n".join(lines).strip("\n") + "\n"
    )
    (OUT / f"{slug}.qmd").write_text(page, encoding="utf-8")


def card(node, slug):
    items = sort_items(node.everything())
    peek = "".join(f"<li>{html.escape(re.sub(r'<[^>]+>', '', i.get('title', '')))}</li>" for i in items[:PEEK_MAX])
    if len(items) > PEEK_MAX:
        peek += f'<li class="more">and {len(items) - PEEK_MAX} more</li>'
    subs = [c.name for c in node.children]
    shown = ", ".join(subs[:SUBS_IN_META]) + (f" +{len(subs) - SUBS_IN_META} more" if len(subs) > SUBS_IN_META else "")
    meta = plural(len(items), "item") + (" · " + shown if subs else "")
    img = f"assets/topics/library-{slug}.jpg"
    return (
        f'<a class="topic-card" href="library/{slug}.html">\n'
        f'  <div class="topic-media"><div class="topic-img" '
        f"style=\"background-image: url('{img}'), url('assets/library.jpg');\"></div></div>\n"
        f'  <div class="topic-body">\n'
        f'    <span class="topic-title">{html.escape(node.name)}</span>\n'
        f'    <span class="topic-meta">{html.escape(meta)}</span>\n'
        f'    <div class="topic-peek"><ul>{peek}</ul></div>\n'
        f"  </div>\n</a>"
    )


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SOURCE
    try:
        data = read_source(src)
    except Exception as e:  # keep the old site rather than publish an empty library
        sys.exit(f"Could not read the library from {src}: {e}")
    top, unfiled = build_tree(data)
    if not top:
        sys.exit("The library has no folders (collections); refusing to publish an empty page.")

    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.qmd"):  # folders deleted in Zotero disappear from the site
        old.unlink()
    (RES / "assets" / "topics").mkdir(parents=True, exist_ok=True)

    cards, images, used = [], [], set()
    for node in top:
        slug, k = slugify(node.name), 2
        while slug in used:
            slug, k = f"{slugify(node.name)}-{k}", k + 1
        used.add(slug)
        write_topic(node, slug)
        cards.append(card(node, slug))
        images.append(f"resources/assets/topics/library-{slug}.jpg")

    total = len({i["key"] for n in top for i in n.everything()})
    hub = (
        '---\ntitle: "Library"\n'
        'description: "Everything I read, half-read and plan to read, grouped by folder."\n'
        "image: assets/library.jpg\ntoc: false\ncss: ../styles/topic-cards.css\n---\n\n"
        f"My [Zotero](https://www.zotero.org) library, {total} papers and books, redrawn from the "
        f"[Mycelium]({REPO_URL}) repository every morning. Open a folder to see what grows inside. "
        f"[BibTeX]({BIB_URL}) for the whole lot.\n\n"
        f"{FENCE}{{=html}}\n<div class=\"topic-grid\">\n" + "\n".join(cards) + f"\n</div>\n{FENCE}\n"
    )
    (RES / "library.qmd").write_text(hub, encoding="utf-8")

    print(f"- library: hub + {len(top)} folder pages, {total} items")
    if unfiled:
        print(f"- {len(unfiled)} items are in no folder yet, so they are not shown (file them in Zotero)")
    print("\nOptional card images (missing ones fall back to resources/assets/library.jpg):")
    for i in images:
        print("  ", i)


if __name__ == "__main__":
    main()
