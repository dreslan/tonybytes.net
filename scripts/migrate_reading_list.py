#!/usr/bin/env python3
"""Migrate reading list from _data/reading_list.yml into _reviews/ collection with status field.

Also adds status: read to all existing _reviews/ entries that don't have a status.
"""

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
REVIEWS_DIR = REPO_ROOT / "_reviews"
DATA_PATH = REPO_ROOT / "_data" / "reading_list.yml"


def slugify(title: str) -> str:
    """Convert a book title to a URL-safe slug."""
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def add_status_to_existing() -> int:
    """Add status: read to existing review files that lack a status field."""
    count = 0
    for path in REVIEWS_DIR.glob("*.md"):
        content = path.read_text(encoding="utf-8")
        if "status:" in content:
            continue
        # Insert status: read after the layout line
        content = content.replace("layout: review\n", "layout: review\nstatus: read\n", 1)
        path.write_text(content, encoding="utf-8")
        count += 1
    return count


def create_reading_list_entries() -> int:
    """Create _reviews/ files from reading list data."""
    reading_list = yaml.safe_load(DATA_PATH.read_text(encoding="utf-8")) or []
    count = 0

    for book in reading_list:
        title = book.get("title", "")
        author = book.get("author", "")
        slug = slugify(title)
        path = REVIEWS_DIR / f"{slug}.md"

        # Handle duplicate slugs
        counter = 2
        while path.exists():
            path = REVIEWS_DIR / f"{slug}-{counter}.md"
            counter += 1

        cover = book.get("cover", "")
        description = book.get("description", "")

        lines = [
            "---",
            "layout: review",
            "status: reading-list",
            f'title: "{title.replace(chr(34), chr(92)+chr(34))}"',
            f'author: "{author.replace(chr(34), chr(92)+chr(34))}"',
            "rating: 0",
            "date_read:",
        ]
        if cover:
            lines.append(f"cover: {cover}")
        if description:
            desc = description.replace('"', '\\"')
            lines.append(f'description: "{desc}"')
        lines.append("---")
        lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")
        count += 1

    return count


def main() -> None:
    updated = add_status_to_existing()
    print(f"Added status: read to {updated} existing review files")

    created = create_reading_list_entries()
    print(f"Created {created} reading-list entries in _reviews/")


if __name__ == "__main__":
    main()
