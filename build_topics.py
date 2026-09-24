#!/usr/bin/env python3
"""Turn each resource list into a card hub + one page per topic.

Keep editing your lists in resources/_source/<name>.qmd (books, videos,
courses, websites), then run from the project root:

    python3 build_topics.py

It writes:
    resources/<name>.qmd              the hub page with the topic cards
    resources/<name>/<topic>.qmd      one page per "## topic"
Don't edit those generated files by hand; edit _source and re-run.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RES = ROOT / "resources"
SRC = RES / "_source"

PAGES = {  # file name -> singular word used in the counts
    "books": "book",
    "videos": "video",
    "courses": "course",
    "websites": "website",
}
PEEK_MAX = 5  # how many items the hover preview lists
FENCE = "`" * 3


def slugify(text):
    text = text.lower().replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def heal(text):
    """Fix '[text] (url)' -> '[text](url)' and the Stanford typo."""
    text = re.sub(r"\]\s+\((?=https?://)", "](", text)
    return text.replace("Standford", "Stanford")


def plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


def item_title(line):
    m = re.match(r"\[(.+?)\]\(", line)  # [Title](url)
    if m:
        return m.group(1)
    m = re.match(r"\*(.+?)\*", line)  # *Title*, Author
    if m:
        return m.group(1)
    return re.sub(r"[*_`]", "", line).strip()  # plain text


def build(name, unit):
    src = SRC / f"{name}.qmd"
    if not src.exists():
        print(f"- {name}: skipped ({src.relative_to(ROOT)} not found)")
        return []

    text = heal(src.read_text(encoding="utf-8"))
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        sys.exit(f"{src} needs a --- front matter block at the top.")
    fm, body = m.groups()
    parent_title = re.search(r'^title:\s*"?(.*?)"?\s*$', fm, re.M).group(1)

    parts = re.split(r"^## +(.+?)\s*$", body, flags=re.M)
    sections = [(parts[i].strip(), parts[i + 1].strip("\n")) for i in range(1, len(parts), 2)]

    hub_fm = [l for l in fm.splitlines() if not re.match(r"(toc|toc-depth|css)\s*:", l)]
    hub_fm += ["toc: false", "css: ../styles/topic-cards.css"]

    (RES / name).mkdir(exist_ok=True)
    cards, images = [], []

    for title, content in sections:
        slug = slugify(title)
        items = re.findall(r"^- (.+)$", content, re.M)
        subs = re.findall(r"^### +(.+?)\s*$", content, re.M)
        n = len(items)

        # ---- topic page ----
        page = re.sub(r"^### ", "## ", content, flags=re.M)
        page = re.sub(r"\]\((?!https?://|\.\./|#|/|mailto:)([^)\s]+\.qmd)\)", r"](../\1)", page)
        safe = title.replace('"', '\\"')
        topic = (
            f'---\ntitle: "{safe}"\n'
            f'description: "{plural(n, unit)}"\n'
            f"toc: false\n---\n\n"
            f"[← {parent_title}](../{name}.qmd)\n\n{page}\n"
        )
        (RES / name / f"{slug}.qmd").write_text(topic, encoding="utf-8")

        # ---- card on the hub ----
        peek = "".join(f"<li>{html.escape(item_title(i))}</li>" for i in items[:PEEK_MAX])
        if n > PEEK_MAX:
            peek += f'<li class="more">and {n - PEEK_MAX} more</li>'
        meta = plural(n, unit) + (" · " + ", ".join(subs) if subs else "")
        img = f"assets/topics/{name}-{slug}.jpg"
        images.append(f"resources/{img}")
        cards.append(
            f'<a class="topic-card" href="{name}/{slug}.html">\n'
            f'  <div class="topic-media"><div class="topic-img" '
            f"style=\"background-image: url('{img}'), url('assets/{name}.jpg');\"></div></div>\n"
            f'  <div class="topic-body">\n'
            f'    <span class="topic-title">{html.escape(title)}</span>\n'
            f'    <span class="topic-meta">{html.escape(meta)}</span>\n'
            f'    <div class="topic-peek"><ul>{peek}</ul></div>\n'
            f"  </div>\n</a>"
        )

    hub = (
        "---\n" + "\n".join(hub_fm) + "\n---\n\n"
        + f"{FENCE}{{=html}}\n<div class=\"topic-grid\">\n"
        + "\n".join(cards)
        + f"\n</div>\n{FENCE}\n"
    )
    (RES / f"{name}.qmd").write_text(hub, encoding="utf-8")
    print(f"- {name}: hub + {len(sections)} topic pages")
    return images


def main():
    if not SRC.exists():
        sys.exit("Create resources/_source/ and move books/videos/courses/websites.qmd into it first.")
    (RES / "assets" / "topics").mkdir(parents=True, exist_ok=True)
    images = []
    for name, unit in PAGES.items():
        images += build(name, unit)
    print("\nOptional card images (missing ones fall back to the page's own image):")
    for i in images:
        print("  ", i)


if __name__ == "__main__":
    main()