#!/usr/bin/env python3
"""Enrich _reviews/ files with Open Library metadata: covers, descriptions, subjects, etc."""

import csv
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REVIEWS_DIR = REPO_ROOT / "_reviews"
COVERS_DIR = REPO_ROOT / "assets" / "images" / "books"
CSV_PATH = REPO_ROOT / "goodreads_library_export.csv"

OL_BOOKS_API = "https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
OL_SEARCH_API = "https://openlibrary.org/search.json?title={title}&author={author}&limit=1"
OL_WORKS_API = "https://openlibrary.org/works/{key}.json"
OL_COVER_URL = "https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
OL_COVER_ISBN_URL = "https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"


def slugify(title: str) -> str:
    """Convert a book title to the same slug used by import_goodreads.py."""
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def fetch_json(url: str) -> dict | None:
    """Fetch JSON from a URL, returning None on failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DreslanBookEnricher/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        print(f"  Warning: fetch failed for {url}: {e}")
        return None


def download_cover(url: str, filename: str) -> str | None:
    """Download a cover image, returning the relative path or None."""
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    dest = COVERS_DIR / filename
    if dest.exists():
        return f"/assets/images/books/{filename}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DreslanBookEnricher/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()
            # Open Library returns a 1x1 pixel for missing covers
            if len(data) < 1000:
                return None
            dest.write_bytes(data)
            return f"/assets/images/books/{filename}"
    except (urllib.error.URLError, TimeoutError):
        return None


def clean_isbn(raw: str) -> str:
    """Extract ISBN from Goodreads CSV format like =\"0385689225\"."""
    return raw.strip().replace('="', "").replace('"', "").strip()


def lookup_by_isbn(isbn: str) -> dict | None:
    """Look up book data via Open Library ISBN API."""
    url = OL_BOOKS_API.format(isbn=isbn)
    data = fetch_json(url)
    if not data:
        return None
    key = f"ISBN:{isbn}"
    return data.get(key)


def lookup_by_search(title: str, author: str) -> dict | None:
    """Search Open Library by title+author, return work-level data."""
    encoded_title = urllib.request.quote(title)
    encoded_author = urllib.request.quote(author)
    url = OL_SEARCH_API.format(title=encoded_title, author=encoded_author)
    data = fetch_json(url)
    if not data or not data.get("docs"):
        return None
    doc = data["docs"][0]
    result: dict = {}

    # Get cover
    cover_id = doc.get("cover_i")
    if cover_id:
        result["cover_id"] = cover_id

    # Get work key for description
    work_key = doc.get("key", "")
    if work_key:
        work_id = work_key.replace("/works/", "")
        result["work_id"] = work_id

    result["first_publish_year"] = doc.get("first_publish_year")
    result["subject"] = doc.get("subject", [])

    return result


def get_work_description(work_id: str) -> str | None:
    """Fetch description from the works API."""
    url = OL_WORKS_API.format(key=work_id)
    data = fetch_json(url)
    if not data:
        return None
    desc = data.get("description")
    if isinstance(desc, dict):
        return desc.get("value")
    if isinstance(desc, str):
        return desc
    return None


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter and body from a markdown file."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    fm_lines = parts[1].strip().split("\n")
    fm: dict = {}
    for line in fm_lines:
        if ": " in line:
            key, val = line.split(": ", 1)
            key = key.strip()
            val = val.strip().strip('"')
            if key == "rating":
                try:
                    fm[key] = int(val)
                except ValueError:
                    fm[key] = val
            else:
                fm[key] = val
    return fm, parts[2]


def write_frontmatter(fm: dict, body: str) -> str:
    """Serialize frontmatter dict + body back to markdown."""
    lines = ["---"]
    # Preserve key order
    key_order = ["layout", "status", "title", "author", "rating", "date_read", "cover",
                 "description", "subjects", "pages", "publisher", "first_published"]
    written = set()
    for key in key_order:
        if key in fm:
            lines.append(format_fm_line(key, fm[key]))
            written.add(key)
    for key, val in fm.items():
        if key not in written:
            lines.append(format_fm_line(key, val))
    lines.append("---")
    return "\n".join(lines) + body


def format_fm_line(key: str, val: object) -> str:
    """Format a single frontmatter key-value line."""
    if isinstance(val, int):
        return f"{key}: {val}"
    if isinstance(val, list):
        if not val:
            return f"{key}: []"
        items = "\n".join(f'  - "{v}"' for v in val)
        return f"{key}:\n{items}"
    # Quote strings
    val_str = str(val)
    if '"' in val_str:
        val_str = val_str.replace('"', '\\"')
    return f'{key}: "{val_str}"'


def build_isbn_map() -> dict[str, tuple[str, str]]:
    """Build a map of slugified title -> (isbn, isbn13) from the Goodreads CSV."""
    isbn_map: dict[str, tuple[str, str]] = {}
    if not CSV_PATH.exists():
        return isbn_map

    with CSV_PATH.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            title = row.get("Title", "").strip()
            isbn = clean_isbn(row.get("ISBN", ""))
            isbn13 = clean_isbn(row.get("ISBN13", ""))
            if title:
                isbn_map[slugify(title)] = (isbn, isbn13)
    return isbn_map


def enrich_book(review_path: Path, isbn: str, isbn13: str) -> bool:
    """Enrich a single review file with Open Library data. Returns True if modified."""
    content = review_path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    # Skip if already enriched
    if fm.get("description") or fm.get("cover"):
        return False

    title = fm.get("title", "")
    author = fm.get("author", "")
    slug = review_path.stem
    print(f"  Enriching: {title}")

    cover_path = None
    description = None
    subjects: list[str] = []
    pages = None
    publisher = None
    first_published = None

    # Try ISBN lookup first
    isbn_to_use = isbn13 or isbn
    if isbn_to_use:
        data = lookup_by_isbn(isbn_to_use)
        if data:
            # Cover
            cover_url = None
            if data.get("cover"):
                cover_url = data["cover"].get("large") or data["cover"].get("medium")
            if not cover_url:
                cover_url = OL_COVER_ISBN_URL.format(isbn=isbn_to_use)
            cover_path = download_cover(cover_url, f"{slug}.jpg")

            # Subjects (take top 5 relevant ones)
            raw_subjects = data.get("subjects", [])
            subjects = [s.get("name", s) if isinstance(s, dict) else s
                        for s in raw_subjects[:5]]

            # Pages
            pages = data.get("number_of_pages")

            # Publisher
            pubs = data.get("publishers", [])
            if pubs:
                publisher = pubs[0].get("name", pubs[0]) if isinstance(pubs[0], dict) else pubs[0]

            # Published date
            first_published = data.get("publish_date")

            # Description from work
            work_url = data.get("url", "")
            # Extract work key if available
            identifiers = data.get("identifiers", {})
            ol_keys = identifiers.get("openlibrary", [])
            if ol_keys:
                # Need to go from edition to work
                edition_url = f"https://openlibrary.org/books/{ol_keys[0]}.json"
                edition_data = fetch_json(edition_url)
                if edition_data and edition_data.get("works"):
                    work_key = edition_data["works"][0]["key"].replace("/works/", "")
                    description = get_work_description(work_key)

    # Fallback: search by title+author
    if not cover_path or not description:
        search_data = lookup_by_search(title, author)
        if search_data:
            # Cover from search
            if not cover_path and search_data.get("cover_id"):
                cover_url = OL_COVER_URL.format(cover_id=search_data["cover_id"])
                cover_path = download_cover(cover_url, f"{slug}.jpg")

            # Description from work
            if not description and search_data.get("work_id"):
                description = get_work_description(search_data["work_id"])

            # Subjects from search
            if not subjects and search_data.get("subject"):
                subjects = search_data["subject"][:5]

            # First published from search
            if not first_published and search_data.get("first_publish_year"):
                first_published = str(search_data["first_publish_year"])

    # Update frontmatter
    changed = False
    if cover_path:
        fm["cover"] = cover_path
        changed = True
    if description:
        # Clean up description - single line, no quotes issues
        description = description.replace("\r\n", " ").replace("\n", " ").strip()
        # Truncate very long descriptions
        if len(description) > 500:
            description = description[:497] + "..."
        fm["description"] = description
        changed = True
    if subjects:
        fm["subjects"] = subjects
        changed = True
    if pages:
        fm["pages"] = int(pages)
        changed = True
    if publisher:
        fm["publisher"] = publisher
        changed = True
    if first_published:
        fm["first_published"] = str(first_published)
        changed = True

    if changed:
        review_path.write_text(write_frontmatter(fm, body), encoding="utf-8")

    return changed


def main() -> None:
    isbn_map = build_isbn_map()
    review_files = sorted(REVIEWS_DIR.glob("*.md"))

    print(f"Found {len(review_files)} review files")
    enriched = 0
    skipped = 0
    failed = 0

    for path in review_files:
        slug = path.stem
        isbn, isbn13 = isbn_map.get(slug, ("", ""))

        try:
            if enrich_book(path, isbn, isbn13):
                enriched += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  Error enriching {slug}: {e}")
            failed += 1

        # Rate limit: Open Library asks for max 1 req/sec
        time.sleep(1)

    print(f"\nDone: {enriched} enriched, {skipped} skipped, {failed} failed")


if __name__ == "__main__":
    main()
