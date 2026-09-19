#!/usr/bin/env python3
"""Create a new page from the template of the right section.

    python3 new.py research "Title of the project"
    python3 new.py blog     "Title of the post"
    python3 new.py courses  "Bayesian Statistics"      (also: videos, books, papers)

The file is created with today's date already filled in. Open it, edit the few lines at the
top, and write below them. Nothing else to register: the section's list page picks it up.
"""
import datetime
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent
SECTIONS = {
    "research": "research",
    "blog": "blog",
    "courses": "notes/courses",
    "videos": "notes/videos",
    "books": "notes/books",
    "papers": "notes/papers",
}


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "untitled"


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in SECTIONS:
        print(__doc__)
        print("Sections:", ", ".join(SECTIONS))
        return 1

    section, title = sys.argv[1], sys.argv[2].strip()
    folder = ROOT / SECTIONS[section]
    template = folder / "_template.qmd"
    if not template.exists():
        print(f"Missing template: {template}")
        return 1

    target = folder / f"{slugify(title)}.qmd"
    if target.exists():
        print(f"{target.relative_to(ROOT)} already exists. Pick another title, or edit that file.")
        return 1

    text = template.read_text(encoding="utf-8")
    text = text.replace("__TITLE__", title.replace('"', '\\"'))
    text = text.replace("__DATE__", datetime.date.today().isoformat())
    target.write_text(text, encoding="utf-8")
    print(f"Created {target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
