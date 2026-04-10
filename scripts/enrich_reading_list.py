#!/usr/bin/env python3
"""Enrich _data/reading_list.yml with Open Library metadata: covers, descriptions."""

import csv
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = REPO_ROOT / "_data" / "reading_list.yml"
COVERS_DIR = REPO_ROOT / "assets" / "images" / "books"
CSV_PATH = REPO_ROOT / "goodreads_library_export.csv"

OL_BOOKS_API = "https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
OL_SEARCH_API = "https://openlibrary.org/search.json?title={title}&author={author}&limit=1"
OL_WORKS_API = "https://openlibrary.org/works/{key}.json"
OL_COVER_URL = "https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
OL_COVER_ISBN_URL = "https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"


def slugify(title: str) -> str:
    """Convert a book title to a URL-safe slug."""
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def clean_isbn(raw: str) -> str:
    """Extract ISBN from Goodreads CSV format."""
    return raw.strip().replace('="', "").replace('"', "").strip()


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
            if len(data) < 1000:
                return None
            dest.write_bytes(data)
            return f"/assets/images/books/{filename}"
    except (urllib.error.URLError, TimeoutError):
        return None


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


def build_isbn_map() -> dict[str, tuple[str, str]]:
    """Build a map of title -> (isbn, isbn13) from the Goodreads CSV."""
    isbn_map: dict[str, tuple[str, str]] = {}
    if not CSV_PATH.exists():
        return isbn_map
    with CSV_PATH.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            title = row.get("Title", "").strip()
            isbn = clean_isbn(row.get("ISBN", ""))
            isbn13 = clean_isbn(row.get("ISBN13", ""))
            if title:
                isbn_map[title] = (isbn, isbn13)
    return isbn_map


def enrich_book(book: dict, isbn: str, isbn13: str) -> bool:
    """Enrich a single reading list entry. Returns True if modified."""
    if book.get("cover") or book.get("description"):
        return False

    title = book.get("title", "")
    author = book.get("author", "")
    slug = slugify(title)
    print(f"  Enriching: {title}")

    cover_path = None
    description = None

    # Try ISBN lookup first
    isbn_to_use = isbn13 or isbn
    if isbn_to_use:
        url = OL_BOOKS_API.format(isbn=isbn_to_use)
        data = fetch_json(url)
        if data:
            entry = data.get(f"ISBN:{isbn_to_use}")
            if entry:
                cover_url = None
                if entry.get("cover"):
                    cover_url = entry["cover"].get("large") or entry["cover"].get("medium")
                if not cover_url:
                    cover_url = OL_COVER_ISBN_URL.format(isbn=isbn_to_use)
                cover_path = download_cover(cover_url, f"{slug}.jpg")

                # Get description from work
                identifiers = entry.get("identifiers", {})
                ol_keys = identifiers.get("openlibrary", [])
                if ol_keys:
                    edition_url = f"https://openlibrary.org/books/{ol_keys[0]}.json"
                    edition_data = fetch_json(edition_url)
                    if edition_data and edition_data.get("works"):
                        work_key = edition_data["works"][0]["key"].replace("/works/", "")
                        description = get_work_description(work_key)

    # Fallback: search by title+author
    if not cover_path or not description:
        encoded_title = urllib.request.quote(title)
        encoded_author = urllib.request.quote(author)
        url = OL_SEARCH_API.format(title=encoded_title, author=encoded_author)
        search_data = fetch_json(url)
        if search_data and search_data.get("docs"):
            doc = search_data["docs"][0]
            if not cover_path:
                cover_id = doc.get("cover_i")
                if cover_id:
                    cover_url = OL_COVER_URL.format(cover_id=cover_id)
                    cover_path = download_cover(cover_url, f"{slug}.jpg")
            if not description:
                work_key = doc.get("key", "").replace("/works/", "")
                if work_key:
                    description = get_work_description(work_key)

    changed = False
    if cover_path:
        book["cover"] = cover_path
        changed = True
    if description:
        desc = description.replace("\r\n", " ").replace("\n", " ").strip()
        if len(desc) > 300:
            desc = desc[:297] + "..."
        book["description"] = desc
        changed = True

    return changed


def main() -> None:
    reading_list = yaml.safe_load(DATA_PATH.read_text(encoding="utf-8")) or []
    isbn_map = build_isbn_map()

    print(f"Found {len(reading_list)} books in reading list")
    enriched = 0

    for book in reading_list:
        title = book.get("title", "")
        isbn, isbn13 = isbn_map.get(title, ("", ""))
        try:
            if enrich_book(book, isbn, isbn13):
                enriched += 1
        except Exception as e:
            print(f"  Error enriching {title}: {e}")
        time.sleep(1)

    # Write back
    with DATA_PATH.open("w", encoding="utf-8") as f:
        yaml.dump(reading_list, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"\nDone: {enriched} enriched out of {len(reading_list)}")


if __name__ == "__main__":
    main()
