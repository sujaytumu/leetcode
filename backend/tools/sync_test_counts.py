#!/usr/bin/env python3
"""Rewrites the problem counts that backend tests assert (total, pages, hard, DP, "SUM" search, easy) from problems.json."""
import json, math, re
from pathlib import Path

root = Path(__file__).resolve().parents[2]
data = json.loads((root / "backend/src/main/resources/seed/problems.json").read_text(encoding="utf-8"))
total = len(data)
hard = sum(p["difficulty"] == "HARD" for p in data)
easy = sum(p["difficulty"] == "EASY" for p in data)
dp = sum("dynamic-programming" in p["tags"] for p in data)
summ = sum(("sum" in p["title"].lower() or "sum" in p["slug"].lower()) for p in data)
tests = root / "backend/src/test/java/com/sujaytumu/leetcode"

def edit(path, pairs):
    text = path.read_text(encoding="utf-8")
    for pattern, repl in pairs:
        text, n = re.subn(pattern, repl, text)
        assert n, f"{path.name}: no match for {pattern}"
    path.write_text(text, encoding="utf-8")

edit(tests / "ProblemApiTest.java", [
    (r'(\$\.totalElements"\)\.value\()\d+(\)\)\s*\n\s*\.andExpect\(jsonPath\("\$\.totalPages"\))', rf'\g<1>{total}\2'),
    (r'(\$\.totalPages"\)\.value\()\d+', rf'\g<1>{math.ceil(total / 5)}'),
    (r'(param\("difficulty", "hard"\)\)\s*\n\s*\.andExpect\(status\(\)\.isOk\(\)\)\s*\n\s*\.andExpect\(jsonPath\("\$\.totalElements"\)\.value\()\d+', rf'\g<1>{hard}'),
    (r'(param\("tag", "dynamic-programming"\)\)\s*\n\s*\.andExpect\(status\(\)\.isOk\(\)\)\s*\n\s*\.andExpect\(jsonPath\("\$\.totalElements"\)\.value\()\d+', rf'\g<1>{dp}'),
    (r'(param\("q", "SUM"\)\)\s*\n\s*\.andExpect\(status\(\)\.isOk\(\)\)\s*\n\s*\.andExpect\(jsonPath\("\$\.totalElements"\)\.value\()\d+', rf'\g<1>{summ}'),
])
text = (tests / "ProblemApiTest.java").read_text(encoding="utf-8")
text = re.sub(r'(sort", "difficulty"\)\.param\("dir", "desc"\)\.param\("size", "100"\)\)\s*\n\s*\.andExpect\(status\(\)\.isOk\(\)\)\s*\n\s*\.andExpect\(jsonPath\("\$\.totalElements"\)\.value\()\d+', rf'\g<1>{total}', text)
text = re.sub(r'(param\("sort", "number"\)\.param\("dir", "desc"\)\.param\("size", "1"\)\)\s*\n\s*\.andExpect\(jsonPath\("\$\.items\[0\]\.number"\)\.value\()\d+', rf'\g<1>{total}', text)
text = re.sub(r'(param\("sort", "acceptance"\)\.param\("size", "100"\)\)\s*\n\s*\.andExpect\(status\(\)\.isOk\(\)\)\s*\n\s*\.andExpect\(jsonPath\("\$\.totalElements"\)\.value\()\d+', rf'\g<1>{total}', text)
(tests / "ProblemApiTest.java").write_text(text, encoding="utf-8")
edit(tests / "SubmissionApiTest.java", [(r'(jsonPath\("\$\.total"\)\.value\()\d{3}', rf'\g<1>{total}'), (r'(EASY\.total"\)\.value\()\d+', rf'\g<1>{easy}')])
edit(tests / "ProfileApiTest.java", [(r'(progress\.total"\)\.value\()\d+', rf'\g<1>{total}')])
edit(tests / "study/StudyApiTest.java", [(r'dailyIndex\(\d+, day\)', f'dailyIndex({total}, day)'), (r'first < \d+', f'first < {total}')])
print(f"synced: {total} problems, {hard} hard, {easy} easy, {dp} DP, {summ} match 'sum'")
