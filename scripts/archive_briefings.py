#!/usr/bin/env python3
"""Migrate old JSON-only briefings.js to lossless daily Markdown archives."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from news_archive import archive_briefing, load_archived_briefings, parse_briefings_js


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--input", type=Path, help="Default: ROOT/data/briefings.js")
    parser.add_argument("--rebuild-js", type=Path, help="Optional derived browser export destination")
    args = parser.parse_args()
    source = args.input or args.root / "data" / "briefings.js"
    briefings = parse_briefings_js(source.read_text(encoding="utf-8"))
    for briefing in briefings:
        archive_briefing(args.root, briefing, input_status="historical-input-unavailable", overwrite=False)
    archived = load_archived_briefings(args.root)
    by_date = {item["date"]: item for item in archived}
    if any(by_date.get(item["date"]) != item for item in briefings):
        raise RuntimeError("Briefing migration failed its lossless round-trip check")
    if args.rebuild_js:
        # Existing frontends expect this identifier; the generator may choose its
        # own export wrapper when using load_archived_briefings directly.
        args.rebuild_js.parent.mkdir(parents=True, exist_ok=True)
        args.rebuild_js.write_text(
            "window.MORNING_BRIEFINGS = " + json.dumps(archived, ensure_ascii=False, separators=(",", ":")) + ";\n",
            encoding="utf-8",
        )
    print(json.dumps({"migrated": len(briefings), "archived": len(archived), "lossless": True}))


if __name__ == "__main__":
    main()
