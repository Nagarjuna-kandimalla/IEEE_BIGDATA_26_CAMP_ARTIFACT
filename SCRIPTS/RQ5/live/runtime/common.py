"""Shared bookkeeping for the sequential CAMP experiments."""

import hashlib, json, os, time
from pathlib import Path

ROOT = Path(os.environ["CAMP_RQ5_LIVE_ROOT"]).resolve()
BASE = ROOT / "experiments"


def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp-" + str(os.getpid()))
    temp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    temp.replace(path)


def plan():
    return json.loads((BASE / "plan.json").read_text())


def phase(key):
    return next(x for x in plan()["phases"] if x["key"] == key)


def control(key):
    return BASE / "control" / key


def event(key, action, **fields):
    path = control(key) / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(
            json.dumps(
                {"time": time.time(), "action": action, **fields}, sort_keys=True
            )
            + "\n"
        )


def digest(path, algorithm="sha256"):
    h = hashlib.new(algorithm)
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def state_from_parent(p):
    if p.get("seed_handoff"):
        s = json.loads(Path(p["seed_handoff"]).read_text())
        assert s["status"] == "PASS"
        return {
            k: s[k]
            for k in [
                "model_root",
                "history_features",
                "history_db",
                "base_training_frame",
                "expected_bowtie2_history_rows",
            ]
        }
    if p.get("parent"):
        parent = phase(p["parent"])
        s = json.loads(Path(parent["handoff"]).read_text())
        if s.get("status") != "PASS":
            raise RuntimeError("Parent state is not validated")
        return {
            k: s[k]
            for k in [
                "model_root",
                "history_features",
                "history_db",
                "base_training_frame",
                "expected_bowtie2_history_rows",
            ]
        }
    seed = BASE / "code/experiment/artifacts"
    return {
        "model_root": str(seed / "initial_model"),
        "history_features": str(seed / "initial_history_features.tsv"),
        "history_db": str(seed / "initial_history.sqlite3"),
        "base_training_frame": str(seed / "initial_model/base_training_frame.tsv"),
        "expected_bowtie2_history_rows": 0,
    }
