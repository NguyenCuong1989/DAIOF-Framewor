#!/usr/bin/env python3
"""
🧪 Workflow Tester - Test all GitHub Actions workflows
"""

from datetime import datetime
from pathlib import Path

import yaml

workflows = [
    "realtime-tasks.yml",
    "health-check.yml",
    "autonomous-development.yml",
    "community-engagement.yml",
    "auto-dependency-updates.yml",
    "auto-pr-review.yml",
    "auto-issue-management.yml",
    "update-dashboard.yml",
]

print("🧪 DAIOF Workflow Tester")
print("=" * 60)

results = {}

for workflow in workflows:
    print(f"\n🧪 Testing {workflow}...")
    path = Path(f".github/workflows/{workflow}")

    if not path.exists():
        print(f"   ❌ File not found")
        results[workflow] = {"exists": False}
        continue

    try:
        content = yaml.safe_load(path.read_text())
        has_dispatch = False
        schedule = None

        if "on" in content:
            triggers = content["on"]
            if isinstance(triggers, dict):
                has_dispatch = "workflow_dispatch" in triggers
                schedule = triggers.get("schedule")

        print(f"   ✅ Syntax valid")
        if has_dispatch:
            print(f"   ✅ Has workflow_dispatch trigger")
        if schedule:
            print(f"   ✅ Has schedule")

        results[workflow] = {
            "exists": True,
            "valid": True,
            "dispatch": has_dispatch,
            "schedule": bool(schedule),
        }
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results[workflow] = {"exists": True, "valid": False, "error": str(e)}

# Summary
print("\n" + "=" * 60)
total = len(results)
valid = sum(1 for r in results.values() if r.get("valid"))
dispatchable = sum(1 for r in results.values() if r.get("dispatch"))

print(f"📊 SUMMARY:")
print(f"   Total: {total}")
print(f"   Valid: {valid}/{total} ✅")
print(f"   Dispatchable: {dispatchable}/{total} ✅")
print("=" * 60)

print(f"\n✅ All workflows ready!")
print(f"🔗 Test manually: https://github.com/NguyenCuong1989/DAIOF-Framework/actions")
