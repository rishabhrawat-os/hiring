#!/usr/bin/env python3
"""Build install/<skill>.zip for each skill, for upload in Customize > Skills or a
Claude chat. Byte-for-byte reproducible. --check exits 1 if a zip is out of date."""
import io, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "plugins/hr-hiring/skills"
OUT = ROOT / "install"
NAMES = ["jd-builder", "resume-screener"]


def build(name):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted((SKILLS / name).rglob("*")):
            if p.is_dir() or "__pycache__" in p.parts or p.name == ".DS_Store":
                continue
            info = zipfile.ZipInfo(f"{name}/{p.relative_to(SKILLS / name).as_posix()}", (1980, 1, 1, 0, 0, 0))
            info.external_attr = 0o644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, p.read_bytes())
    return buf.getvalue()


def frontmatter_problems(name):
    """claude.ai rejects a skill whose name or description has < or >, or a description over 200 characters."""
    head = (SKILLS / name / "SKILL.md").read_text().split("---")[1]
    out = []
    for line in head.strip().splitlines():
        key, _, val = line.partition(":")
        if key in ("name", "description") and ("<" in val or ">" in val):
            out.append(f"{name}: {key} contains < or >")
        if key == "description" and len(val.strip()) > 200:
            out.append(f"{name}: description is {len(val.strip())} characters (max 200)")
    return out


def main():
    check = "--check" in sys.argv
    stale = []
    bad = [msg for name in NAMES for msg in frontmatter_problems(name)]
    if bad:
        print("FAIL " + "; ".join(bad))
        sys.exit(1)
    OUT.mkdir(exist_ok=True)
    for name in NAMES:
        data, path = build(name), OUT / f"{name}.zip"
        if check:
            if not path.exists() or path.read_bytes() != data:
                stale.append(path.name)
        else:
            path.write_bytes(data)
            print(f"wrote install/{path.name} ({len(data) // 1024} KB)")
    if stale:
        print("FAIL out of date: " + ", ".join(stale) + " (run python3 tools/build_skill_zips.py)")
        sys.exit(1)


if __name__ == "__main__":
    main()
