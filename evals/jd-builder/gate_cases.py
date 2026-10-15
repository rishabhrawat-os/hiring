#!/usr/bin/env python3
"""Synthetic step outputs that check_gate.py must pass or fail."""
import copy
import json
import subprocess
import sys

skill, out = sys.argv[1:]
GATE = [sys.executable, f"{skill}/scripts/check_gate.py"]

src = [{"id": f"s{i}", "url": f"https://example.org/{i}", "publisher": "x", "date": "2026-06", "type": "posting"} for i in range(16)]
research = {
    "round": 1, "role_summary": "x",
    "level": {"name": "Manager", "experience_range": "4–7 years", "track": "Individual contributor", "rationale": "x", "sources": ["s0"]},
    "level_dimensions": [{"key": f"K{i}", "expectation": "x", "sources": ["s1"]} for i in range(6)],
    "responsibilities": [{"area": "a", "items": [{"text": "x", "sources": ["s2"]}]}],
    "must_haves": [{"text": "x", "why": "x", "sources": ["s3"]}],
    "nice_to_haves": [{"text": "x", "sources": ["s4"]}],
    "tools": {"ads": ["x"]},
    "behaviours": [{"title": "x", "evidence": "x", "sources": ["s5"]} for _ in range(5)],
    "ai_use": [{"text": "x", "sources": ["s6"]}],
    "assessment": [{"title": "x", "how": "x", "sources": ["s7"]} for _ in range(6)],
    "mismatch": [{"text": "x", "sources": ["s8"]}],
    "must_include_status": [{"item": "x", "status": "current", "note": ""}],
    "objection_responses": [],
    "sources": src,
}
dims = {"role_accuracy": 20, "seniority": 15, "currency": 14, "coverage": 15, "realism": 10, "context": 9, "evidence": 10, "fairness": 5}
challenge = {"round": 1, "persona": "VP", "score": 98, "by_dimension": dims, "pass": True,
             "objections": [{"id": "c1-1", "severity": "minor", "area": "", "issue": "", "evidence": "", "required_change": ""}],
             "own_searches": [f"query {i}" for i in range(6)],
             "spot_checks": [{"source": f"s{i}", "supports_claim": True, "note": ""} for i in range(5)]}
fmt = {"round": 1, "score": 96, "by_dimension": {"blueprint": 29, "faithful": 25, "human": 28, "proofreading": 14}, "pass": True, "issues": []}


def run(kind, data, *extra):
    p = f"{out}/gate.json"
    json.dump(data, open(p, "w"))
    return subprocess.run(GATE + [kind, p, *extra], capture_output=True, text=True).returncode == 0


json.dump(research, open(f"{out}/research.json", "w"))
cases = [
    ("research ok", True, "research", research, "--run-date", "2026-10-15"),
    ("research old sources", False, "research", {**research, "sources": [{**s, "date": "2023-01"} for s in src]}, "--run-date", "2026-10-15"),
    ("research claim without source", False, "research", {**research, "must_haves": [{"text": "x", "why": "x", "sources": []}]}, "--run-date", "2026-10-15"),
    ("research bad date", False, "research", research, "--run-date", "15/10/2026"),
    ("challenge ok", True, "challenge", challenge, "--research", f"{out}/research.json"),
    ("challenge bonus key", False, "challenge", {**challenge, "score": 95, "by_dimension": {**dims, "currency": 9, "bonus": 5}}),
    ("challenge low score", False, "challenge", {**challenge, "score": 90, "by_dimension": {**dims, "currency": 6}}),
    ("challenge Major caps", False, "challenge", {**challenge, "objections": [{"id": "c1-2", "severity": "Major"}]}),
    ("challenge duplicate spot checks", False, "challenge", {**challenge, "spot_checks": [{"source": "s1", "supports_claim": True}] * 5}),
    ("challenge empty searches", False, "challenge", {**challenge, "own_searches": [""] * 6}),
    ("challenge failed spot check, minor objection", False, "challenge",
     {**challenge, "spot_checks": challenge["spot_checks"][:4] + [{"source": "s4", "supports_claim": False}],
      "objections": [{"id": "c1-3", "severity": "minor", "issue": "s4 weak"}]}),
    ("format ok", True, "format", fmt),
    ("format open major", False, "format", {**fmt, "issues": [{"id": "f1", "severity": "major"}]}),
]
bad = 0
for name, want, kind, data, *extra in cases:
    if run(kind, copy.deepcopy(data), *extra) != want:
        print(f"FAIL gate case: {name} (expected {'pass' if want else 'fail'})")
        bad = 1
if not bad:
    print(f"ok   gate checks ({len(cases)} cases)")
sys.exit(bad)
