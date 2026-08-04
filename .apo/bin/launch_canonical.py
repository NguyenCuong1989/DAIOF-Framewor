#!/usr/bin/env python3
"""
APΩ Canonical Node Launcher

Luồng:
    Gate đã chạy xong (preLaunchTask) → launcher kiểm tra port 3011:
        - Không có process: exec node-clean index.js
        - Có process canonical (owner=workspace + node.*index.js):
            * POLICY=REUSE  → reuse, exit 0
            * POLICY=REPLACE → kill owner → exec node-clean index.js
        - Có process foreign → không kill, exit 1

Quy định semantics:
    PreflightPass != PortFree
"""
import os
import re
import signal
import subprocess
import sys
from pathlib import Path


def read_policy(workspace: Path) -> str:
    env_policy = os.environ.get("APO_LAUNCH_POLICY", "").strip().upper()
    if env_policy:
        return env_policy
    policy_path = workspace / ".apo" / "state" / "launch_policy"
    if policy_path.exists():
        return policy_path.read_text(encoding="utf-8").strip().upper()
    return "REUSE"


def find_listener(port: int) -> int | None:
    result = subprocess.run(
        ["lsof", "-tiTCP:" + str(port), "-sTCP:LISTEN"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        return int(result.stdout.strip().splitlines()[0])
    except ValueError:
        return None


def process_command(pid: int) -> str:
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def process_cwd(pid: int) -> str:
    result = subprocess.run(
        ["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"],
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if line.startswith("n"):
            return line[1:]
    return ""


def is_canonical_owner(pid: int, workspace: Path, program: str) -> bool:
    cwd = process_cwd(pid)
    cmd = process_command(pid)
    if not cwd or not cmd:
        return False
    normalized_cwd = Path(cwd).resolve()
    normalized_workspace = workspace.resolve()
    if normalized_cwd != normalized_workspace:
        return False
    # Match node invocation for the target program
    pattern = re.compile(r"node.*" + re.escape(program) + r"(?:\s|$)")
    return bool(pattern.search(cmd))


def main() -> int:
    workspace = Path(os.environ.get("APO_WORKSPACE", "/Users/andy/tr-gi-p-merge-ready"))
    port = int(os.environ.get("APO_PORT", "3011"))
    program = os.environ.get("APO_PROGRAM", "index.js")
    node_clean = workspace / ".apo" / "bin" / "node-clean"
    target = workspace / program

    policy = read_policy(workspace)

    if not target.exists():
        print(f"APO_FATAL: target not found: {target}", file=sys.stderr)
        return 1

    pid = find_listener(port)

    if pid is None:
        print(f"RUNTIME_STATE=ABSENT → starting {program} on port {port}")
        os.environ["PORT"] = str(port)
        os.execv(str(node_clean), [str(node_clean), str(target)])

    cmd = process_command(pid)
    cwd = process_cwd(pid)
    print(f"PORT_{port}_PID={pid}")
    print(f"PORT_{port}_CMD={cmd}")
    print(f"PORT_{port}_CWD={cwd}")

    if is_canonical_owner(pid, workspace, program):
        print("RUNTIME_STATE=CANONICAL_EXISTING")
        if policy == "REPLACE":
            print(f"POLICY=REPLACE → stopping PID {pid}")
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            # Wait briefly for port release
            for _ in range(20):
                if find_listener(port) is None:
                    break
                import time

                time.sleep(0.1)
            os.environ["PORT"] = str(port)
            os.execv(str(node_clean), [str(node_clean), str(target)])
        else:
            print(f"POLICY={policy} → reusing existing canonical runtime")
            return 0

    print("RUNTIME_STATE=FOREIGN_OR_UNKNOWN")
    print(
        f"APO_FATAL: port {port} is owned by a foreign process (PID {pid}). "
        "Stop it manually or set APO_LAUNCH_POLICY=REPLACE if it is stale.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
