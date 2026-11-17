#!/usr/bin/env python3
"""Regenerate frontend/public/problems-snapshot.json from the backend seed.

The snapshot lets the site render problems instantly (before the free backend wakes up).
Run after editing backend/src/main/resources/seed/problems.json:  python3 scripts/build-snapshot.py
Problems are listed by their study-path `order`, which the backend also uses as the displayed number.
"""
import json, os, sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
seed = json.load(open(os.path.join(root, "backend/src/main/resources/seed/problems.json")))
out = []
for i, p in enumerate(sorted(seed, key=lambda q: q["order"]), 1):
    out.append({
        "id": p["order"], "number": p["order"], "slug": p["slug"], "title": p["title"], "difficulty": p["difficulty"], "tags": p["tags"],
        "description": p["description"], "starterCode": p["starterCode"],
        "samples": [{"input": t["input"], "expectedOutput": t["expectedOutput"]} for t in p["testCases"] if t.get("sample")],
    })
dest = os.path.join(root, "frontend/public/problems-snapshot.json")
json.dump(out, open(dest, "w"), separators=(",", ":"), ensure_ascii=False)
print(f"{len(out)} problems, {os.path.getsize(dest) // 1024} KB -> {dest}", file=sys.stderr)
