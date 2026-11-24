#!/usr/bin/env python3
"""Regenerates seed/problems.json and keeps the extra hidden tests that scripts/add-tests.mjs appended to existing problems.

generate_seed.py writes the base data from scratch; add-tests.mjs adds more test cases afterwards. Running the generator
alone would drop those, so this wrapper restores the committed test cases of every problem that already exists.
Problems listed after --fresh keep the generator's new tests instead (use it when a problem's answers changed).
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = HERE.parent / "src/main/resources/seed/problems.json"
fresh = set(sys.argv[sys.argv.index("--fresh") + 1].split(",")) if "--fresh" in sys.argv else set()

before = {p["slug"]: p for p in json.loads(SEED.read_text(encoding="utf-8"))}
subprocess.run([sys.executable, str(HERE / "generate_seed.py")], check=True)
generated = json.loads(SEED.read_text(encoding="utf-8"))
kept = 0
for problem in generated:
    old = before.get(problem["slug"])
    if old and problem["slug"] not in fresh:
        problem["testCases"] = old["testCases"]
        kept += 1
SEED.write_text(json.dumps(generated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"kept the committed tests of {kept} existing problems; {len(generated) - kept} take the generator's tests")
