#!/usr/bin/env python3
"""
APΩ Workspace State Extractor

Scans the Antigravity workspace and emits a workspace-state.json that the
C++ canon gate (apo-canon-gate) can validate.

Phương trình:
    W = Extract(Workspace)
    R = Validate_APΩ(W)
    Launch = Execute  if R == 1
             Freeze/Reject if R == 0

Usage:
    python3 .apo/canon/extractor.py <workspace-root> <output-json>
"""
import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def discover_directories(root: Path) -> list[dict]:
    """Find top-level directories that contain a README.md."""
    dirs = []
    for entry in sorted(root.iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            readme = entry / "README.md"
            if readme.exists():
                dirs.append(
                    {
                        "name": entry.name,
                        "readmePath": str(readme.relative_to(root)),
                    }
                )
    return dirs


def make_graph(directory: dict) -> dict:
    """Build a minimal valid graph for one directory."""
    dir_id = directory["name"]
    readme_id = f"readme:{directory['name']}"
    return {
        "vertices": [
            {
                "id": dir_id,
                "label": directory["name"].capitalize(),
                "synthetic": False,
            },
            {
                "id": readme_id,
                "label": "README",
                "synthetic": False,
            },
        ],
        "edges": [
            {
                "from": dir_id,
                "to": readme_id,
                "label": "contains",
            }
        ],
    }


def make_trace(directory: dict, seq: int) -> list[dict]:
    """Create a deterministic runtime trace for the directory."""
    return [
        {
            "id": f"evt-{directory['name']}-{seq:03d}",
            "description": f"Directory '{directory['name']}' discovered with README.",
            "sourceDirectory": directory["name"],
            "sequence": seq,
        }
    ]


def make_lineage(graph: dict) -> dict:
    """Create a single-snapshot lineage for the graph."""
    return {
        "snapshots": [
            {
                "revision": 1,
                "previousFingerprint": "GENESIS",
                "fingerprint": str(uuid.uuid4()),
                "graph": graph,
            }
        ]
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="APΩ workspace state extractor")
    parser.add_argument("workspace", help="Workspace root path")
    parser.add_argument("output", help="Output workspace-state.json path")
    args = parser.parse_args()

    root = Path(args.workspace).resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory", file=sys.stderr)
        return 1

    directories = discover_directories(root)
    if not directories:
        # Fallback: at least one directory so the gate has something to validate.
        directories = [
            {
                "name": "workspace",
                "readmePath": "README.md" if (root / "README.md").exists() else "",
            }
        ]

    graphs = {}
    traces = {}
    lineages = {}
    cross_relations = []

    for index, directory in enumerate(directories, start=1):
        graph = make_graph(directory)
        graphs[directory["name"]] = graph
        traces[directory["name"]] = make_trace(directory, index)
        lineages[directory["name"]] = make_lineage(graph)

    # Cross-relations intentionally empty in this version:
    # adding a shared "workspace" root with one label to many children would
    # make the MultiGraph non-deterministic (same (from, label) -> multiple to).
    # A single canonical tree can be represented by keeping directory graphs
    # disconnected and relying on the directory set as the canonical partition.

    state = {
        "input": "META_SPEC_APO",
        "type": "APO-Language",
        "segmentLoaded": {
            "start": "1",
            "end": "9.12",
        },
        "directories": directories,
        "graphs": graphs,
        "crossRelations": cross_relations,
        "runtimeTraces": traces,
        "lineage": lineages,
        "extractedAt": datetime.now(timezone.utc).isoformat(),
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"W: {output_path} ({len(directories)} directories)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
