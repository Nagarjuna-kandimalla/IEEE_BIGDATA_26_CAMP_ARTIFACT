#!/usr/bin/env python3
"""Losslessly restore verified models/history without Git LFS or machine paths."""
import argparse, gzip, hashlib, json, os, shutil, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
STORE = REPO / "DATA/RQ5/live/models"


def index():
    return json.loads((STORE / "index.json").read_text())


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def parts(digest, meta):
    return meta.get(
        "parts",
        [{"file": digest + ".gz", "sha256": meta["sha256"], "bytes": meta["bytes"]}],
    )


def decode(digest, meta, destination=None):
    with tempfile.TemporaryFile() as compressed:
        for p in parts(digest, meta):
            f = STORE / "blobs" / p["file"]
            assert f.stat().st_size == p["bytes"] and sha(f) == p["sha256"], f
            with f.open("rb") as src:
                shutil.copyfileobj(src, compressed)
        compressed.seek(0)
        h = hashlib.sha256()
        with gzip.GzipFile(fileobj=compressed) as f:
            for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
                h.update(block)
                if destination is not None:
                    destination.write(block)
        assert h.hexdigest() == digest, (
            "Uncompressed model checksum mismatch: " + digest
        )


def extract(bundle, destination):
    data = index()
    bundle = data.get("aliases", {}).get(bundle, bundle)
    d = data["bundles"][bundle]
    destination = Path(destination).resolve()
    if destination.exists():
        raise RuntimeError("Refusing existing destination " + str(destination))
    temporary = destination.with_name(destination.name + ".tmp-" + str(os.getpid()))
    temporary.mkdir(parents=True)
    try:
        for f in d["files"]:
            rel = Path(f["path"])
            assert not rel.is_absolute() and ".." not in rel.parts
            target = temporary / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("wb") as out:
                decode(f["sha256"], data["blobs"][f["sha256"]], out)
            assert target.stat().st_size == f["bytes"]
            target.chmod(f["mode"])
        handoff = temporary / "handoff.json"
        if handoff.exists():
            shutil.copy2(handoff, temporary / "handoff.original.json")
            h = json.loads(handoff.read_text())
            for key, value in {
                "model_root": "model",
                "history_features": "history_features.tsv",
                "history_db": "history.sqlite3",
                "base_training_frame": "model/base_training_frame.tsv",
            }.items():
                h[key] = str(destination / value)
            h["restored_from_bundle"] = bundle
            h["phase"] = bundle
            h["raw_history_retained_at"] = (
                "See packaged task_outcomes.jsonl.gz; original absolute path in handoff.original.json"
            )
            handoff.write_text(json.dumps(h, indent=2) + "\n")
        temporary.replace(destination)
    except BaseException:
        shutil.rmtree(temporary)
        raise
    return destination


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    v = sub.add_parser("verify")
    v.add_argument("--deep", action="store_true")
    e = sub.add_parser("extract")
    e.add_argument("bundle")
    e.add_argument("destination", type=Path)
    a = p.parse_args()
    data = index()
    if a.command == "list":
        print(
            json.dumps(
                {
                    k: {
                        "files": len(v["files"]),
                        "uncompressed_bytes": v["uncompressed_bytes"],
                    }
                    for k, v in data["bundles"].items()
                },
                indent=2,
            )
        )
    elif a.command == "extract":
        print(extract(a.bundle, a.destination))
    else:
        for digest, meta in data["blobs"].items():
            for part in parts(digest, meta):
                f = STORE / "blobs" / part["file"]
                assert f.stat().st_size == part["bytes"] and sha(f) == part["sha256"], f
            if a.deep:
                decode(digest, meta)
        print("PASS:", len(data["blobs"]), "verified model blobs; deep=" + str(a.deep))


if __name__ == "__main__":
    main()
