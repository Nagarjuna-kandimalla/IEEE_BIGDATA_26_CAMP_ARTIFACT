#!/usr/bin/env python3
"""Exercise portable restoration/configuration and fake Slurm; no real jobs."""
import os, sys, json, subprocess, tempfile, shutil, hashlib, sqlite3
from pathlib import Path

repo = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo / "SCRIPTS/RQ5/live"))
from configure import configure

base = Path(tempfile.mkdtemp(prefix="camp rq5 portable check "))
subprocess.run(
    [sys.executable, str(repo / "SCRIPTS/RQ5/live/models.py"), "verify", "--deep"],
    check=True,
)
from reproduce_results import reproduce

reproduce(base / "recomputed")
cfg = json.loads((repo / "SCRIPTS/RQ5/live/config/cluster.example.json").read_text())
cfg["python"] = sys.executable
tool = base / "nextflow"
tool.write_text("#!/bin/sh\nexit 0\n")
tool.chmod(0o755)
cfg["nextflow"] = str(tool)
config = base / "cluster.json"
config.write_text(json.dumps(cfg))
root = base / "clean relocated workspace"
configure(root, config)
plan = json.loads((root / "experiments/plan.json").read_text())
assert [p["key"] for p in plan["phases"]] == [
    "warm_transfer_cold",
    "warm_transfer_warm",
    "warm_transfer_new_input",
    "direct_transfer_new_input",
]
assert plan["phases"][-1]["parent"] == "warm_transfer_cold"
assert plan["phases"][2]["parent"] == "warm_transfer_warm"
assert all(
    Path(p["run_root"]).is_relative_to(root)
    and Path(p["handoff"]).is_relative_to(root)
    and Path(p["manifest"]).is_relative_to(repo)
    for p in plan["phases"]
)
subprocess.run(
    ["sha256sum", "--check", "--quiet", "SHA256SUMS"],
    cwd=root / "experiments/code",
    check=True,
)
seed = root / "experiments/code/experiment/artifacts"
script = (
    repo
    / "SCRIPTS/RQ5/experiment_template/camp/live_online_learning/scripts/preflight_run_inputs.py"
)
subprocess.run(
    [
        cfg["python"],
        str(script),
        "--workflow",
        "bowtie2",
        "--model-root",
        str(seed / "initial_model"),
        "--history-features",
        str(seed / "initial_history_features.tsv"),
        "--history-db",
        str(seed / "initial_history.sqlite3"),
        "--base-training-frame",
        str(seed / "initial_model/base_training_frame.tsv"),
        "--expected-workflow-rows",
        "0",
    ],
    check=True,
    stdout=(base / "initial-preflight.json").open("w"),
)
# Simulate only the scheduler API; do not execute a workflow or provision workers.
bin = base / "stubbin"
bin.mkdir()
counter = base / "job-counter"
counter.write_text("1000")
capture = base / "submitted.jsonl"
stub = """#!/usr/bin/env python3
import sys,json,os
from pathlib import Path
counter=Path(os.environ['CAMP_TEST_COUNTER']);capture=Path(os.environ['CAMP_TEST_CAPTURE'])
if Path(sys.argv[0]).name=='sbatch':
 n=int(counter.read_text())+1;counter.write_text(str(n));capture.open('a').write(json.dumps(sys.argv[1:])+'\\n');print(n)
elif Path(sys.argv[0]).name=='scontrol':print('NodeName=controller CPUTot=16 RealMemory=58000')
"""
for name in ["sbatch", "squeue", "scontrol", "sacct"]:
    (bin / name).write_text(stub)
    (bin / name).chmod(0o755)
env = os.environ.copy()
env.update(
    PATH=str(bin) + ":" + env["PATH"],
    CAMP_TEST_COUNTER=str(counter),
    CAMP_TEST_CAPTURE=str(capture),
)
cmd = [sys.executable, str(repo / "SCRIPTS/RQ5/live/submit.py"), "--root", str(root)]
subprocess.run(cmd, env=env, check=True, stdout=(base / "submission.json").open("w"))
jobs = json.loads((root / "experiments/jobs.json").read_text())["jobs"]
assert len(jobs) == 14
assert [j["phase"] for j in jobs if j["kind"] == "controller"] == [
    p["key"] for p in plan["phases"]
]
assert any(
    "afterok:" in (j["dependency"] or "") and ":" in j["dependency"][8:]
    for j in jobs
    if j["phase"] == "direct_transfer_new_input" and j["kind"] == "controller"
)
res = subprocess.run(cmd, env=env, capture_output=True)
assert res.returncode != 0 and b"Already submitted" in res.stderr
# The recorded cold branch must rebase metadata and preserve original scientific bytes.
saved = base / "saved cold relocated"
configure(saved, config, saved_cold=True)
sp = json.loads((saved / "experiments/plan.json").read_text())
assert len(sp["phases"]) == 1 and sp["phases"][0]["key"] == "direct_transfer_new_input"
assert sp["settings"]["controller_cpus"] == 2
hand = json.loads(
    (saved / "experiments/saved-cold-checkpoint/handoff.json").read_text()
)
assert hand["expected_bowtie2_history_rows"] == 6000
assert str(saved) in hand["model_root"]
assert Path(hand["history_db"]).is_file()
subprocess.run(
    [
        cfg["python"],
        str(script),
        "--workflow",
        "bowtie2",
        "--model-root",
        hand["model_root"],
        "--history-features",
        hand["history_features"],
        "--history-db",
        hand["history_db"],
        "--base-training-frame",
        hand["base_training_frame"],
        "--expected-workflow-rows",
        "6000",
    ],
    check=True,
    stdout=(base / "saved-cold-preflight.json").open("w"),
)
with sqlite3.connect(hand["history_db"]) as c:
    assert c.execute("pragma integrity_check").fetchone()[0] == "ok"
results = {
    "status": "PASS",
    "tests": [
        "All four stage metrics recomputed independently",
        "All model/container blobs decoded and verified separately",
        "Fresh path with spaces configured; full frozen source hashes pass",
        "Offline seed preflight: zero Bowtie2 history",
        "Slurm API simulated: sequential gates and shared-cold parent; no real jobs submitted",
        "Duplicate submission refused",
        "Recorded cold restored at another path with matching history/calibration and SQLite integrity",
        "Saved-cold branch omits cold/warm executions",
    ],
    "scope": "Packaging, preflight, configuration and simulated orchestration checks. A new full Slurm biological rerun was NOT performed.",
}
(base / "validation.json").write_text(json.dumps(results, indent=2) + "\n")
output = repo / "build/rq5-live-selfcheck"
output.mkdir(parents=True, exist_ok=True)
shutil.copy2(base / "validation.json", output / "validation.json")
print(json.dumps(results, indent=2))
shutil.rmtree(base)
