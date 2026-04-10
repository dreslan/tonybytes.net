#!/usr/bin/env python3
"""One-time import of Goodreads CSV export into Jekyll _reviews/ and _data/reading_list.yml."""

import csv
import re
import sys
from pathlib import Path


def slugify(title: str) -> str:
    """Convert a book title to a URL-safe filename slug."""
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def star_rating(rating_str: str) -> int:
    """Parse rating string to int, defaulting to 0 if missing."""
    try:
        return int(rating_str)
    except (ValueError, TypeError):
        return 0


def build_review(row: dict) -> str:
    """Build a Jekyll review markdown file from a Goodreads CSV row."""
    title = row.get("Title", "").strip()
    author = row.get("Author", "").strip()
    rating = star_rating(row.get("My Rating", "0"))
    date_read = row.get("Date Read", "").strip()
    review_text = row.get("My Review", "").strip()

    # Goodreads uses YYYY/MM/DD — convert to YYYY-MM-DD
    if date_read:
        date_read = date_read.replace("/", "-")
    else:
        # Fall back to Date Added if no Date Read
        date_added = row.get("Date Added", "").strip()
        date_read = date_added.replace("/", "-") if date_added else "1970-01-01"

    frontmatter = f"""---
layout: review
title: "{title.replace('"', '\\"')}"
author: "{author.replace('"', '\\"')}"
rating: {rating}
date_read: {date_read}
---"""

    if review_text:
        return f"{frontmatter}\n\n{review_text}\n"
    return f"{frontmatter}\n"


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <goodreads_export.csv>", file=sys.stderr)
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"File not found: {csv_path}", file=sys.stderr)
        sys.exit(1)

    repo_root = Path(__file__).resolve().parent.parent
    reviews_dir = repo_root / "_reviews"
    data_dir = repo_root / "_data"
    reviews_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)

    reading_list: list[dict[str, str]] = []
    review_count = 0
    has_review_count = 0

    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("Title", "").strip()
            author = row.get("Author", "").strip()
            shelf = row.get("Exclusive Shelf", "").strip()

            if not title:
                continue

            if shelf == "to-read":
                reading_list.append({"title": title, "author": author})
                continue

            if shelf in ("read", "currently-reading"):
                slug = slugify(title)
                review_path = reviews_dir / f"{slug}.md"

                # Handle duplicate slugs
                counter = 2
                while review_path.exists():
                    review_path = reviews_dir / f"{slug}-{counter}.md"
                    counter += 1

                review_path.write_text(build_review(row), encoding="utf-8")
                review_count += 1

                if row.get("My Review", "").strip():
                    has_review_count += 1

    # Write reading list YAML
    reading_list_path = data_dir / "reading_list.yml"
    with reading_list_path.open("w", encoding="utf-8") as f:
        for book in reading_list:
            title = book["title"].replace('"', '\\"')
            author = book["author"].replace('"', '\\"')
            f.write(f'- title: "{title}"\n  author: "{author}"\n\n')

    print(f"Imported {review_count} books to _reviews/ ({has_review_count} with reviews)")
    print(f"Imported {len(reading_list)} books to _data/reading_list.yml")


if __name__ == "__main__":
    main()
