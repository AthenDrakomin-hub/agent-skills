#!/usr/bin/env python3
"""
Batch archive Douyin video links to Feishu.

Usage:
    python archive.py --input videos.txt --folder <feishu_folder_token>

Input file format: one Douyin URL per line, optionally followed by a tab and a custom tag override.
"""

import argparse
import sys
from pathlib import Path


def parse_input(filepath: str) -> list[dict]:
    """Parse the input file into a list of {url, tags} entries."""
    entries = []
    path = Path(filepath)
    if not path.exists():
        print(f"Error: input file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t", 1)
        url = parts[0].strip()
        tags = parts[1].strip() if len(parts) > 1 else ""
        entries.append({"url": url, "tags": tags})
    return entries


def validate_url(url: str) -> bool:
    """Basic validation for Douyin share URLs."""
    return url.startswith("https://v.douyin.com/") or url.startswith("https://www.douyin.com/video/")


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch archive Douyin videos to Feishu")
    parser.add_argument("--input", required=True, help="Path to text file with one URL per line")
    parser.add_argument("--folder", required=True, help="Feishu folder token or share link")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate only, do not archive")
    args = parser.parse_args()

    entries = parse_input(args.input)
    print(f"Loaded {len(entries)} video(s) from {args.input}")

    for i, entry in enumerate(entries, 1):
        url = entry["url"]
        if not validate_url(url):
            print(f"  [{i}] SKIP (invalid URL): {url}")
            continue
        print(f"  [{i}] OK: {url}  tags={entry['tags'] or '(auto)'}")
        if not args.dry_run:
            # Placeholder: integrate with video extraction + Feishu API here
            print(f"       -> would archive to folder {args.folder}")

    if args.dry_run:
        print("\nDry run complete. No archives were created.")


if __name__ == "__main__":
    main()
