#!/usr/bin/env python3
"""Verify the complete artifact manifest, optionally requiring tracked-file coverage."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def verify(require_tracked=False):
    entries = json.loads((REPO / "ARTIFACT_MANIFEST.json").read_text())["files"]
    listed = set()
    for entry in entries:
        relative = Path(entry["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError("Unsafe manifest path: " + str(relative))
        if entry["path"] in listed:
            raise RuntimeError("Duplicate manifest path: " + entry["path"])
        listed.add(entry["path"])
        path = REPO / relative
        if not path.is_file() or path.stat().st_size != entry["bytes"]:
            raise RuntimeError("Missing file or size mismatch: " + str(relative))
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
                digest.update(block)
        if digest.hexdigest() != entry["sha256"]:
            raise RuntimeError("Checksum mismatch: " + str(relative))
    if require_tracked:
        tracked = {
            p.decode()
            for p in subprocess.check_output(
                ["git", "-C", str(REPO), "ls-files", "-z"]
            ).split(b"\0")
            if p
        }
        tracked.discard("ARTIFACT_MANIFEST.json")
        if tracked - listed:
            raise RuntimeError(
                "Tracked files omitted from manifest: " + repr(sorted(tracked - listed))
            )
    return {
        "status": "PASS",
        "verified_files": len(entries),
        "tracked_coverage_checked": require_tracked,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-tracked",
        action="store_true",
        help="Also check Git tracked files; omit for an extracted source archive",
    )
    args = parser.parse_args()
    print(json.dumps(verify(args.require_tracked), indent=2))
