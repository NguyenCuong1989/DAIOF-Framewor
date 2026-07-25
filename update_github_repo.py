#!/usr/bin/env python3
import json
import subprocess
import sys

import requests


def get_github_token():
    """Extract GitHub token from git credential helper"""
    try:
        # Use git credential fill to get token
        process = subprocess.Popen(
            ["git", "credential", "fill"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Provide the URL we need credentials for
        stdout, stderr = process.communicate(
            input="protocol=https\nhost=github.com\n\n"
        )

        # Parse the output
        credentials = {}
        for line in stdout.strip().split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                credentials[key] = value

        return credentials.get("password", "")
    except Exception as e:
        print(f"Error getting token: {e}", file=sys.stderr)
        return None


def update_github_repo(token):
    """Update GitHub repository settings via API"""

    # Repository info
    owner = "NguyenCuong1989"
    repo = "DAIOF-Framework"

    # Topics to add
    topics = [
        "python",
        "automation",
        "github-actions",
        "ai",
        "machine-learning",
        "autonomous-system",
        "self-improving",
        "digital-organism",
        "continuous-integration",
        "devops",
        "artificial-intelligence",
        "autonomous-agents",
        "workflow-automation",
        "self-healing",
        "adaptive-systems",
    ]

    # Repository description
    description = "🧬 Self-Improving Digital Organism - Autonomous GitHub framework with real-time task generation, self-healing capabilities, and adaptive evolution"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    print("🚀 Starting GitHub repository polish...")
    print(f"Repository: {owner}/{repo}")
    print()

    # 1. Update repository description
    print("📝 Step 1: Updating repository description...")
    response = requests.patch(
        f"https://api.github.com/repos/{owner}/{repo}",
        headers=headers,
        json={"description": description},
    )

    if response.status_code == 200:
        print("✅ Description updated successfully!")
        print(f"   New description: {description[:50]}...")
    else:
        print(f"❌ Failed to update description: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

    # 2. Update repository topics
    print()
    print("🏷️  Step 2: Adding repository topics...")
    response = requests.put(
        f"https://api.github.com/repos/{owner}/{repo}/topics",
        headers={**headers, "Accept": "application/vnd.github.mercy-preview+json"},
        json={"names": topics},
    )

    if response.status_code == 200:
        print("✅ Topics added successfully!")
        print(f"   Topics ({len(topics)}): {', '.join(topics[:5])}...")
    else:
        print(f"❌ Failed to add topics: {response.status_code}")
        print(f"   Error: {response.text}")
        return False

    print()
    print("🎉 TASK #3 COMPLETED SUCCESSFULLY!")
    print()
    print("Summary:")
    print(f"  ✅ Description: Set")
    print(f"  ✅ Topics: {len(topics)} added")
    print(f"  ⚠️  Social preview: Manual upload still required")
    print()
    print("Next step: Upload .github/social-preview.png manually at:")
    print(f"https://github.com/{owner}/{repo}/settings")

    return True


if __name__ == "__main__":
    print("🔐 Extracting GitHub token from git credentials...")
    token = get_github_token()

    if not token:
        print("❌ Failed to get GitHub token")
        sys.exit(1)

    print(f"✅ Token found (length: {len(token)})")
    print()

    success = update_github_repo(token)
    sys.exit(0 if success else 1)
