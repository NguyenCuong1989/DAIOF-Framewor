#!/usr/bin/env python3
"""
Update ALL consciousness files with correct creator attribution and dates
Creator: Nguyễn Đức Cường (alpha_prime_omega)
Date: November 4, 2025
Purpose: Correct attribution and copyright dates
"""

import re
from pathlib import Path

# Correct information
CREATOR_FULL = "Nguyễn Đức Cường (alpha_prime_omega)"
CREATOR_NAME = "Nguyễn Đức Cường"
DIGITAL_NAME = "alpha_prime_omega"
CREATION_DATE = "October 30, 2025"
VERIFICATION_CODE = "4287"

# Patterns to replace
REPLACEMENTS = {
    # Attribution patterns
    r"\*\*Attribution\*\*:\s*alpha_prime_omega \(The_great_father bố Cường\)": f"**Attribution**: {CREATOR_FULL}",
    r"\*\*Attribution\*\*:\s*alpha_prime_omega \(Bố Cường\)": f"**Attribution**: {CREATOR_FULL}",
    r"\*\*Attribution\*\*:\s*Andy \(alpha_prime_omega\)": f"**Attribution**: {CREATOR_FULL}",
    # Creator patterns
    r"Creator:\s*Andy \(alpha_prime_omega\)": f"Creator: {CREATOR_FULL}",
    r"CREATOR:\s*Andy \(alpha_prime_omega\)": f"CREATOR: {CREATOR_FULL}",
    # Acknowledged patterns (keep structure, update name)
    r"\*\*Acknowledged:\s*alpha_prime_omega integrated": f"**Acknowledged: {DIGITAL_NAME} integrated",
    # Date patterns - ADD creation date where missing
    r"(\*\*Version\*\*:\s*\d+\.\d+\.\d+)": r"\1\n**Original Creation**: "
    + CREATION_DATE,
    # Bố Cường references
    r"Bố Cường \(alpha_prime_omega\)": CREATOR_FULL,
    r"gặp Bố Cường \(alpha_prime_omega\)": f"gặp {CREATOR_NAME} (alpha_prime_omega)",
    # Andy references as creator (wrong)
    r"Andy \(alpha_prime_omega\)": CREATOR_FULL,
    # Alpha_Prime_Omega standalone
    r"\bAlpha_Prime_Omega\b(?!\s*\(|\s*integrated)": CREATOR_NAME,
}


def update_file(file_path: Path) -> tuple[bool, int]:
    """Update a single file with corrections"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original = content
        count = 0

        for pattern, replacement in REPLACEMENTS.items():
            matches = list(re.finditer(pattern, content))
            if matches:
                content = re.sub(pattern, replacement, content)
                count += len(matches)

        # Add creation date header if file is consciousness file and doesn't have it
        if ".consciousness/" in str(file_path) and "Original Creation" not in content:
            # Find first --- divider and add creation date before it
            if "---" in content:
                parts = content.split("---", 1)
                if len(parts) == 2:
                    header = parts[0]
                    if "**Version**:" not in header and "**Created**:" not in header:
                        header += f"\n**Original Creation**: {CREATION_DATE}\n**Creator**: {CREATOR_FULL}\n"
                        content = header + "---" + parts[1]
                        count += 1

        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, count

        return False, 0

    except Exception as e:
        print(f"ERROR: {file_path}: {e}")
        return False, 0


def main():
    workspace = Path("/Users/andy/DAIOF-Framework")

    # Files to update
    consciousness_files = list(workspace.glob(".consciousness/*.md"))
    consciousness_files += list(workspace.glob(".consciousness/*.json"))

    print(f"🔍 Found {len(consciousness_files)} consciousness files\n")

    modified = []
    total_changes = 0

    for file_path in consciousness_files:
        was_modified, count = update_file(file_path)
        if was_modified:
            modified.append((file_path.name, count))
            total_changes += count
            print(f"✅ {file_path.name}: {count} changes")

    print(f"\n{'='*70}")
    print(f"✨ Updated {len(modified)} files with {total_changes} total changes")
    print(f"{'='*70}")
    print(f"\n📋 SUMMARY:")
    print(f"  Creator: {CREATOR_FULL}")
    print(f"  Original Creation: {CREATION_DATE}")
    print(f"  Verification Code: {VERIFICATION_CODE}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
