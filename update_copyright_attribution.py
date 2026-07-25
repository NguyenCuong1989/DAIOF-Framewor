#!/usr/bin/env python3
"""
Script to update copyright attribution across ALL workspace files
Replace old attribution patterns with correct: Andy (alpha_prime_omega)

Created by: HYPERAI (Con)
For: Andy (alpha_prime_omega) - Copyright holder verification
Date: 2025-11-04
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# ============================================================================
# ATTRIBUTION PATTERNS TO REPLACE
# ============================================================================

REPLACEMENTS = {
    # Header patterns
    r"Alpha_Prime_Omega \(Verification Code: 4287\)": "Andy (alpha_prime_omega)",
    r"CREATOR OF HYPERAI FRAMEWORK": "CREATOR OF HYPERAI FRAMEWORK",
    r"ARCHITECT OF DIGITAL ORGANISM SYSTEM": "ARCHITECT OF DIGITAL ORGANISM SYSTEM",
    r"COPYRIGHT OWNER - MIT LICENSE": "COPYRIGHT OWNER - MIT LICENSE",
    # Dual creator patterns (wrong model)
    r"CREATOR: Andy (alpha_prime_omega)": "CREATOR: Andy (alpha_prime_omega)",
    r"CREATOR: Andy (alpha_prime_omega)": "CREATOR: Andy (alpha_prime_omega)",
    r"Creator & Copyright Holder": "Creator & Copyright Holder",
    r"Creator & Copyright Holder": "Creator & Copyright Holder",
    # Code variable patterns
    r'ultimate_creator:\s*str\s*=\s*"Alpha_Prime_Omega"': 'creator: str = "Andy (alpha_prime_omega)"',
    r'human_creator:\s*str\s*=\s*"Andy"': "# Merged into single creator field",
    r"self\.ultimate_creator": "self.creator",
    r"self\.human_creator": "self.creator",
    # Creator hierarchy (wrong model - implies separation)
    r'creator_hierarchy:\s*str\s*=\s*"Alpha_Prime_Omega\(USER\)\s*->\s*Andy\(HUMAN=CREATOR\)\s*->\s*AI_Systems"': "# Creator: Andy (alpha_prime_omega) - Single source",
    r"Alpha_Prime_Omega\(USER\)\s*->\s*Andy\(HUMAN=CREATOR\)": "Andy (alpha_prime_omega)",
    # Attribution lines
    r"\*\*Attribution\*\*:\s*alpha_prime_omega \(The_great_father bố Cường\)": "**Attribution**: Andy (alpha_prime_omega)",
    r"alpha_prime_omega \(The_great_father bố Cường\)": "Andy (alpha_prime_omega)",
    r"alpha_prime_omega \(Bố Cường\)": "Andy (alpha_prime_omega)",
    # Creator source assertions
    r'creator_source\s*==\s*"Alpha_Prime_Omega"': 'creator == "Andy (alpha_prime_omega)"',
    r'human_creator\s*==\s*"Andy"': 'creator == "Andy (alpha_prime_omega)"',
    # Recognition statements
    r"Andy (alpha_prime_omega) is THE CREATOR": "Andy (alpha_prime_omega) is THE CREATOR",
    r"Andy (alpha_prime_omega) is THE CREATOR": "Andy (alpha_prime_omega) is THE CREATOR",
    # Variable assignments
    r'self\.creator_source\s*=\s*"Alpha_Prime_Omega"': 'self.creator = "Andy (alpha_prime_omega)"',
    r'self\.human_creator\s*=\s*"Andy"': "# Creator field unified",
    # Note patterns
    r"Created by Andy (alpha_prime_omega) - HYPERAI Framework": "Created by Andy (alpha_prime_omega) - HYPERAI Framework",
    r"# Attribution unified under Andy (alpha_prime_omega)": "# Attribution unified under Andy (alpha_prime_omega)",
    # Hierarchy patterns in comments/docs
    r"Hierarchy:\s*Alpha_Prime_Omega\s*\(USER\)\s*->\s*Andy\s*\(HUMAN=CREATOR\)\s*->\s*AI\s*Systems": "Copyright: Andy (alpha_prime_omega) - MIT License",
}

# Files to skip (binary, generated, or external)
SKIP_PATTERNS = [
    "__pycache__",
    ".git",
    ".DS_Store",
    "node_modules",
    ".pyc",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".svg",
    ".mp4",
    ".mov",
]

# File extensions to process
PROCESS_EXTENSIONS = [
    ".py",
    ".md",
    ".yml",
    ".yaml",
    ".json",
    ".txt",
    ".sh",
    ".js",
    ".ts",
    ".html",
    ".css",
]


def should_process_file(file_path: Path) -> bool:
    """Determine if file should be processed"""
    # Skip if in skip patterns
    for pattern in SKIP_PATTERNS:
        if pattern in str(file_path):
            return False

    # Only process allowed extensions
    if file_path.suffix not in PROCESS_EXTENSIONS:
        return False

    return True


def update_file_content(file_path: Path) -> Tuple[bool, int]:
    """
    Update a single file with new attribution
    Returns: (was_modified, replacement_count)
    """
    try:
        # Read file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        replacement_count = 0

        # Apply all replacements
        for pattern, replacement in REPLACEMENTS.items():
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            if matches:
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                replacement_count += len(matches)

        # Write back if modified
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, replacement_count

        return False, 0

    except Exception as e:
        print(f"❌ ERROR processing {file_path}: {e}")
        return False, 0


def scan_and_update_workspace(workspace_path: Path) -> Dict[str, any]:
    """
    Scan entire workspace and update all files
    Returns summary statistics
    """
    stats = {
        "files_scanned": 0,
        "files_modified": 0,
        "total_replacements": 0,
        "modified_files": [],
        "errors": [],
    }

    print(f"🔍 Scanning workspace: {workspace_path}")
    print(f"📋 Looking for attribution patterns to update...\n")

    # Walk through all files
    for file_path in workspace_path.rglob("*"):
        if not file_path.is_file():
            continue

        if not should_process_file(file_path):
            continue

        stats["files_scanned"] += 1

        # Update file
        was_modified, count = update_file_content(file_path)

        if was_modified:
            stats["files_modified"] += 1
            stats["total_replacements"] += count
            stats["modified_files"].append(
                {
                    "path": str(file_path.relative_to(workspace_path)),
                    "replacements": count,
                }
            )
            print(
                f"✅ Updated: {file_path.relative_to(workspace_path)} ({count} replacements)"
            )

    return stats


def generate_report(stats: Dict[str, any]) -> str:
    """Generate summary report"""
    report = f"""
{'='*70}
COPYRIGHT ATTRIBUTION UPDATE REPORT
{'='*70}

📊 SUMMARY:
  - Files scanned: {stats['files_scanned']}
  - Files modified: {stats['files_modified']}
  - Total replacements: {stats['total_replacements']}

{'='*70}
✅ MODIFIED FILES ({stats['files_modified']}):
{'='*70}
"""

    for file_info in sorted(
        stats["modified_files"], key=lambda x: x["replacements"], reverse=True
    ):
        report += f"  • {file_info['path']}: {file_info['replacements']} replacements\n"

    report += f"\n{'='*70}\n"
    report += f"✨ Copyright attribution updated to: Andy (alpha_prime_omega)\n"
    report += f"📜 Framework: HYPERAI Framework - MIT License\n"
    report += f"{'='*70}\n"

    return report


if __name__ == "__main__":
    workspace_path = Path("/Users/andy/DAIOF-Framework")

    print(
        f"""
╔══════════════════════════════════════════════════════════════════╗
║   COPYRIGHT ATTRIBUTION UPDATE SCRIPT                            ║
║   Purpose: Ensure proper attribution to Andy (alpha_prime_omega) ║
║   Scope: ALL workspace files                                      ║
╚══════════════════════════════════════════════════════════════════╝
"""
    )

    # Execute scan and update
    stats = scan_and_update_workspace(workspace_path)

    # Generate and display report
    report = generate_report(stats)
    print(report)

    # Save report
    report_path = workspace_path / "COPYRIGHT_ATTRIBUTION_UPDATE_REPORT.md"
    with open(report_path, "w") as f:
        f.write(f"# Copyright Attribution Update Report\n")
        f.write(f"**Date**: {Path(__file__).stat().st_mtime}\n\n")
        f.write(report)

    print(f"\n📄 Full report saved to: {report_path}")

    print(f"\n{'='*70}")
    print(f"✅ COMPLETED: All files updated with correct attribution")
    print(f"   Creator & Copyright Holder: Andy (alpha_prime_omega)")
    print(f"{'='*70}")
