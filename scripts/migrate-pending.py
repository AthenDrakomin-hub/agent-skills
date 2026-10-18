#!/usr/bin/env python3
"""One-time migration of the PENDING.md backlog into skills/ (Option A).

Daily-evolve.ps1 refuses to silently drop Chinese-named skills but also
cannot guess ASCII slugs for them. This script closes the loop:

  1. Reads $SlugMap from scripts/daily-evolve.ps1 (single source of truth —
     add a mapping there, the migration picks it up automatically).
  2. Reads PENDING.md (both the legacy 3-column and the new 5-column format).
  3. For each row: resolves slug, locates the source directory, enforces the
     same 80..500-line + frontmatter gates as daily-evolve, copies into
     skills/<slug>/, rewrites the frontmatter (name -> ASCII slug, optional
     `label:` carrying the Chinese title), strips personal agents/ config.
  4. Removes migrated/stale rows from PENDING.md; keeps the rest with an
     actionable reason (what to add to $SlugMap, where the source is).

Stale rows (slug already exists under skills/) are dropped — that skill was
already normalized into the repo, the backlog entry just wasn't pruned.

Sources: PENDING.md carries the author's Windows absolute paths. When those
do not exist (e.g. running inside a container), pass --stage DIR where every
source directory has been copied flat, named by its original folder name:

    mkdir -p agent-skills/pending-sources
    # copy the 45 source skill dirs into pending-sources/ (Windows side)
    python3 scripts/migrate-pending.py --stage pending-sources

Options:
  --repo-root DIR   repo root (default: parent of the dir containing this script)
  --stage DIR       staging dir with flat copies of the source skill dirs
  --min-lines N     quality gate floor (default 80, 0 disables)
  --max-lines N     quality gate ceiling (default 500, 0 disables)
  --allow-no-source accept a row even when its source dir cannot be found
                    (the row is then only validated for slug resolution)
  --dry-run         do everything except copy/rewrite/PENDING/git
  --push            run `git push origin main` after committing
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

CJK = re.compile(r"[\u4e00-\u9fff]")
NAME_RE = re.compile(r"[a-z][a-z0-9-]*[a-z0-9]")


# --------------------------------------------------------------------------
# $SlugMap extraction (single source of truth lives in daily-evolve.ps1)
# --------------------------------------------------------------------------
def parse_slug_map(ps1: Path) -> dict[str, str]:
    txt = ps1.read_text(encoding="utf-8-sig")
    m = re.search(r"\$SlugMap\s*=\s*@{(.*?)^}", txt, re.S | re.M)
    if not m:
        return {}
    return dict(re.findall(r"^\s*'([^']+)'\s*=\s*'([^']+)'", m.group(1), re.M))


# --------------------------------------------------------------------------
# PENDING.md
# --------------------------------------------------------------------------
def load_pending(md: Path) -> list[dict]:
    """Parse either legacy 3-col (Name|Reason|Source) or new 5-col
    (Name|Slug|Label|Reason|Source) tables. Returns row dicts."""
    if not md.exists():
        return []
    rows: list[dict] = []
    header: list[str] | None = None
    for line in md.read_text(encoding="utf-8-sig").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-") for c in cells):
            continue
        by_name = {h: c for h, c in zip(header, cells)}
        if "name" not in by_name or "source" not in by_name:
            continue
        rows.append({
            "name": by_name.get("name", ""),
            "slug": by_name.get("slug", "-"),
            "label": by_name.get("label", "-"),
            "reason": by_name.get("reason", ""),
            "source": by_name.get("source", ""),
        })
    return rows


def write_pending(md: Path, kept: list[dict]) -> None:
    if not kept:
        if md.exists():
            md.unlink()
        return
    lines = [
        "# Pending Skills (need manual normalization)",
        "",
        "| Name | Slug | Label | Reason | Source |",
        "|---|---|---|---|---|",
    ]
    for p in kept:
        lines.append(
            f"| {p['name']} | {p.get('slug') or '-'} | {p.get('label') or '-'} "
            f"| {p['reason']} | {p['source']} |"
        )
    md.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")


# --------------------------------------------------------------------------
# slug resolution
# --------------------------------------------------------------------------
def resolve_slug(row: dict, slug_map: dict[str, str], fm: dict[str, str]) -> tuple[str | None, str | None]:
    """Returns (slug, label). label None => no Chinese title to carry.
    slug None => unresolvable. PENDING's label column uses '-' as a
    placeholder for 'none', which must normalize to None (a literal
    `label: -` in frontmatter is a no-op value, not a title)."""
    raw_label = row.get("label")
    label = None if raw_label in (None, "", "-") else raw_label
    if row.get("slug") not in (None, "", "-"):
        return row["slug"], label
    name = fm.get("name") or row["name"]
    if name in slug_map:
        # Chinese source name with no explicit label: carry the name itself.
        return slug_map[name], label or name
    if not CJK.search(name):
        s = re.sub(r"-{2,}", "-", re.sub(r"[ ./_]", "-", name.lower())).strip("-")
        if NAME_RE.fullmatch(s):
            return s, label  # ASCII: no label unless one was given
    return None, label


# --------------------------------------------------------------------------
# source location
# --------------------------------------------------------------------------
def source_basename(source: str) -> str:
    s = source.rstrip("\\/").replace("\\", "/")
    return s.rsplit("/", 1)[-1]


def locate_source(row: dict, stage: Path | None) -> Path | None:
    src = Path(row["source"])
    if src.is_dir():
        return src
    if stage is not None:
        cand = stage / source_basename(row["source"])
        if cand.is_dir():
            return cand
        cand2 = stage / row["name"]
        if cand2.is_dir():
            return cand2
    return None


# --------------------------------------------------------------------------
# frontmatter rewrite (mirrors daily-evolve.ps1 exactly)
# --------------------------------------------------------------------------
def rewrite_frontmatter(dst_md: Path, slug: str, label: str | None) -> None:
    txt = dst_md.read_text(encoding="utf-8")
    txt = re.sub(r"(?m)^name:.*$", f"name: {slug}", txt, count=1)
    if label and label != slug:
        txt = re.sub(
            rf"(?m)^name: {re.escape(slug)}\r?$",
            f"name: {slug}\nlabel: {label}",
            txt,
            count=1,
        )
    dst_md.write_text(txt, encoding="utf-8")


def frontmatter_of(md: Path) -> dict[str, str]:
    txt = md.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", txt, re.S)
    fm: dict[str, str] = {}
    if m:
        for line in m.group(1).splitlines():
            if line.strip() and not line.startswith((" ", "\t")) and ":" in line:
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--stage", default=None, help="dir with flat copies of source skill dirs")
    ap.add_argument("--min-lines", type=int, default=80)
    ap.add_argument("--max-lines", type=int, default=500)
    ap.add_argument("--allow-no-source", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--push", action="store_true")
    args = ap.parse_args()

    if args.repo_root:
        repo = Path(args.repo_root).resolve()
    else:
        repo = Path(__file__).resolve().parent.parent
    pending_md = repo / "PENDING.md"
    skills_dir = repo / "skills"
    slug_map = parse_slug_map(repo / "scripts" / "daily-evolve.ps1")
    stage = Path(args.stage).resolve() if args.stage else None

    existing = {p.name for p in skills_dir.iterdir() if p.is_dir() and (p / "SKILL.md").exists()} if skills_dir.exists() else set()

    print(f"repo root : {repo}")
    print(f"slug map  : {len(slug_map)} mappings (from daily-evolve.ps1)")
    print(f"stage dir : {stage if stage else '(none)'}")
    print(f"skills/   : {len(existing)} installed")

    rows = load_pending(pending_md)
    kept: list[dict] = []
    migrated: list[str] = []
    stale: list[str] = []

    for row in rows:
        tag = f"{row['name']} -> "
        # 1) slug?
        src_dir = locate_source(row, stage)
        fm = frontmatter_of(src_dir / "SKILL.md") if src_dir else {}
        slug, label = resolve_slug(row, slug_map, fm)
        if slug is None:
            kept.append({**row, "slug": None, "label": label,
                         "reason": f"unmapped name '{row['name']}' — add it to $SlugMap in daily-evolve.ps1"
                                   + ("" if src_dir else " (source missing)")})
            print(f"  KEEP    {tag}(no slug mapping)")
            continue
        # 2) already in repo?
        if slug in existing:
            stale.append(row["name"])
            print(f"  STALE   {tag}{slug} (already in skills/ — dropping row)")
            continue
        # 3) source?
        if src_dir is None:
            reason = "source missing (--allow-no-source recorded only)" if args.allow_no_source else \
                     f"source not found: {row['source']}" + (f" (stage: {stage / source_basename(row['source'])})" if stage else "")
            kept.append({**row, "slug": slug, "label": label, "reason": reason})
            print(f"  KEEP{'*' if args.allow_no_source else ''}    {tag}{reason}")
            continue
        # 4) quality gates (same thresholds as daily-evolve)
        md = src_dir / "SKILL.md"
        if not md.exists():
            kept.append({**row, "slug": slug, "label": label, "reason": "No SKILL.md in source"})
            print(f"  KEEP    {tag}no SKILL.md")
            continue
        lines = md.read_text(encoding="utf-8").count("\n") + 1
        fm = fm or frontmatter_of(md)
        if not fm.get("name"):
            kept.append({**row, "slug": slug, "label": label, "reason": "Missing name in frontmatter"})
            print(f"  KEEP    {tag}missing frontmatter name")
            continue
        if args.min_lines and lines < args.min_lines:
            kept.append({**row, "slug": slug, "label": label,
                         "reason": f"too thin: {lines} lines (min {args.min_lines})"})
            print(f"  KEEP    {tag}too thin ({lines} lines)")
            continue
        if args.max_lines and lines > args.max_lines:
            kept.append({**row, "slug": slug, "label": label,
                         "reason": f"{lines} lines exceeds {args.max_lines}"})
            print(f"  KEEP    {tag}over line limit ({lines} lines)")
            continue
        # 5) migrate
        dst = skills_dir / slug
        if dst.exists():
            stale.append(row["name"])
            print(f"  STALE   {tag}{slug} (dir already present)")
            continue
        if not args.dry_run:
            shutil.copytree(src_dir, dst, symlinks=False)
            agents = dst / "agents"
            if agents.exists():
                shutil.rmtree(agents)
            rewrite_frontmatter(dst / "SKILL.md", slug, label)
        migrated.append(row["name"])
        print(f"  {'OK(dry)' if args.dry_run else 'MIGRATE'} {tag}{slug}"
              + (f"  [label: {label}]" if label and label != slug else ""))

    # prune PENDING.md
    if not args.dry_run:
        write_pending(pending_md, kept)
        if migrated or stale:
            subprocess.run(["git", "add", "-A", str(pending_md), str(skills_dir)], cwd=repo, check=False)
            subprocess.run(["git", "commit", "-m",
                           f"migrate-pending: {len(migrated)} migrated, {len(stale)} stale rows dropped "
                           f"({len(kept)} still pending)"], cwd=repo, check=False)
            if args.push:
                subprocess.run(["git", "push", "origin", "main"], cwd=repo, check=False)

    print(f"\nsummary: migrated={len(migrated)} stale_dropped={len(stale)} still_pending={len(kept)}")
    if kept:
        print("still pending:")
        for p in kept:
            print(f"  - {p['name']}: {p['reason']}")
    if not args.dry_run:
        print("\nnext step: npx -y skills add ./ --list   (CI gate check)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
