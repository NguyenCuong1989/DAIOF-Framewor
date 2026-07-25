#!/usr/bin/env python3
"""
Create demo screenshots showing DAIOF in action
Generates multiple frames that can be combined into GIF
"""

import subprocess
import sys
import time


def create_demo_output():
    """Capture demo.sh output in stages"""

    print("🎬 Capturing DAIOF Framework demo output...\n")

    # Run demo.sh and capture output
    result = subprocess.run(
        ["./demo.sh"], capture_output=True, text=True, cwd="/Users/andy/DAIOF-Framework"
    )

    output = result.stdout

    # Save full output
    output_file = "assets/demo-output.txt"
    with open(output_file, "w") as f:
        f.write(output)

    print(f"✅ Demo output saved: {output_file}")
    print(f"   Size: {len(output)} bytes")
    print(f"\n📋 Output preview (first 50 lines):")
    print("=" * 60)
    lines = output.split("\n")
    for line in lines[:50]:
        print(line)
    print("=" * 60)
    print(f"\n✅ Total lines captured: {len(lines)}")

    return output_file


if __name__ == "__main__":
    create_demo_output()
