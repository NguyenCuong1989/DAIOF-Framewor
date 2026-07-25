#!/usr/bin/env python3
"""
COMPLETE WORKSPACE SCAN - Including ALL files (git, cache, ignored)
Creator: Nguyễn Đức Cường (alpha_prime_omega)
Date: November 4, 2025
Purpose: Comprehensive IP audit for copyright protection
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/andy/DAIOF-Framework")
CREATOR = "Nguyễn Đức Cường (alpha_prime_omega)"
CREATION_DATE = "2025-10-30"

# Files from .gitignore that need STRICT copyright
PRIORITY_IGNORED_PATTERNS = [
    "__pycache__/",
    "*.pyc",
    "*.py[cod]",
    "*.pkl",
    "*.pickle",
    "ecosystem_data/",
    "simulation_results/",
    ".env",
    "venv/",
    ".venv/",
    "*.log",
    ".DS_Store",
]


def scan_all_files():
    """Scan TẤT CẢ files kể cả ignored"""
    all_files = []
    ignored_files = []
    git_files = []

    for root, dirs, files in os.walk(WORKSPACE):
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(WORKSPACE)

            file_info = {
                "path": str(rel_path),
                "full_path": str(file_path),
                "size": file_path.stat().st_size if file_path.exists() else 0,
                "extension": file_path.suffix,
                "in_git": ".git" in str(rel_path),
                "is_ignored": is_ignored(str(rel_path)),
                "priority_copyright": needs_priority_copyright(str(rel_path)),
            }

            all_files.append(file_info)

            if file_info["in_git"]:
                git_files.append(file_info)
            elif file_info["is_ignored"]:
                ignored_files.append(file_info)

    return all_files, ignored_files, git_files


def is_ignored(path):
    """Check if file matches .gitignore patterns"""
    for pattern in PRIORITY_IGNORED_PATTERNS:
        if pattern in path or path.endswith(pattern.replace("*", "")):
            return True
    return False


def needs_priority_copyright(path):
    """Files that need STRICT copyright protection FIRST"""
    priority_patterns = [
        "ecosystem_data/",
        "simulation_results/",
        ".pyc",
        ".pkl",
        ".pickle",
        "__pycache__",
        "venv/",
        ".env",
    ]
    return any(p in path for p in priority_patterns)


def categorize_files(all_files):
    """Phân loại files theo IP category"""
    categories = {
        "priority_copyright": [],  # Ignored files - STRICT protection
        "open_source": [],  # Public MIT License files
        "conditional": [],  # Need permission
        "proprietary": [],  # Private only
        "git_internal": [],  # .git files
    }

    for f in all_files:
        if f["in_git"]:
            categories["git_internal"].append(f)
        elif f["priority_copyright"]:
            categories["priority_copyright"].append(f)
        elif any(x in f["path"] for x in ["haios", "secret", "private"]):
            categories["proprietary"].append(f)
        elif any(x in f["path"] for x in ["examples/", "docs/", "README"]):
            categories["open_source"].append(f)
        else:
            categories["conditional"].append(f)

    return categories


def generate_comprehensive_report():
    """Generate complete IP audit including ALL files"""
    print("🔍 Scanning TOÀN BỘ workspace (including .git, cache, ignored)...")

    all_files, ignored_files, git_files = scan_all_files()
    categories = categorize_files(all_files)

    report = {
        "scan_metadata": {
            "creator": CREATOR,
            "scan_date": datetime.now().isoformat(),
            "workspace": str(WORKSPACE),
            "copyright_effective_from": CREATION_DATE,
        },
        "summary": {
            "total_files": len(all_files),
            "ignored_files": len(ignored_files),
            "git_files": len(git_files),
            "priority_copyright_needed": len(categories["priority_copyright"]),
            "open_source": len(categories["open_source"]),
            "conditional_use": len(categories["conditional"]),
            "proprietary": len(categories["proprietary"]),
        },
        "priority_copyright_files": [
            {
                "path": f["path"],
                "size": f["size"],
                "extension": f["extension"],
                "reason": "Ignored file - needs STRICT protection",
            }
            for f in categories["priority_copyright"]
        ],
        "categories": {k: [f["path"] for f in v] for k, v in categories.items()},
        "gitignore_patterns_found": PRIORITY_IGNORED_PATTERNS,
        "copyright_notice": {
            "creator": CREATOR,
            "date": CREATION_DATE,
            "applies_to": "ALL files including ignored and cached files",
            "violation": "Any use without attribution is copyright infringement from Oct 30, 2025",
        },
    }

    # Save report
    output_file = WORKSPACE / "COMPLETE_IP_AUDIT_ALL_FILES.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n✅ COMPLETE SCAN FINISHED!")
    print(f"📊 Total files scanned: {len(all_files)}")
    print(f"🔒 Priority copyright (ignored): {len(categories['priority_copyright'])}")
    print(f"📁 Git internal: {len(git_files)}")
    print(f"🟢 Open source: {len(categories['open_source'])}")
    print(f"🟡 Conditional: {len(categories['conditional'])}")
    print(f"🔴 Proprietary: {len(categories['proprietary'])}")
    print(f"\n📄 Report saved: {output_file}")

    return report


if __name__ == "__main__":
    report = generate_comprehensive_report()

    # Print priority files that need copyright FIRST
    print("\n" + "=" * 70)
    print("🔥 PRIORITY: Files cần COPYRIGHT NGHIÊM NGẶT TRƯỚC (from .gitignore)")
    print("=" * 70)

    for f in report["priority_copyright_files"][:20]:
        print(f"  • {f['path']} ({f['size']} bytes)")

    if len(report["priority_copyright_files"]) > 20:
        print(f"  ... and {len(report['priority_copyright_files']) - 20} more files")

    print("\n" + "=" * 70)
    print(f"✅ Creator: {CREATOR}")
    print(f"📅 Copyright from: {CREATION_DATE}")
    print("=" * 70)
