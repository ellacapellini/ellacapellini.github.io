#!/usr/bin/env python3
"""Create a new page from the template of the right section.

    python3 new.py research "Title of the project"
    python3 new.py courses  "Bayesian Statistics"
    python3 new.py videos   "A lecture worth watching"   (also: books, papers; these go to resources/)

The file is created with today's date already filled in. Open it, edit the few lines at the
top, and write below them. Nothing else to register: the section's list page picks it up.
"""
import datetime
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parent
SECTIONS = {                      # kind: (folder, template)
    "research": ("research", "_template.qmd"),
    "courses": ("courses", "_template.qmd"),
    "videos": ("resources", "_template-video.qmd"),
    "books": ("resources", "_template-book.qmd"),
    "papers": ("resources", "_template-paper.qmd"),
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
    folder_name, template_name = SECTIONS[section]
    folder = ROOT / folder_name
    template = folder / template_name
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
