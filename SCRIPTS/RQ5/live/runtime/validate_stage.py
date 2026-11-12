#!/usr/bin/env python3
import collections, csv, json, os, shutil, sqlite3, subprocess, sys, time
from pathlib import Path
from common import (
    ROOT,
    BASE,
    atomic,
    control,
    digest,
    event,
    phase,
    state_from_parent,
    plan,
)


def main(key):
    p = phase(key)
    run = Path(p["run_root"])
    camp = run / "camp"
    destination = Path(p["handoff"]).parent
    if Path(p["handoff"]).exists():
        old = json.loads(Path(p["handoff"]).read_text())
        if old.get("status") == "PASS":
            return
        raise RuntimeError("Existing non-passing handoff requires inspection")
    code = BASE / "code"
    expected_path = control(key) / "expected-tasks.tsv"
    expected_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            plan()["settings"]["python"],
            str(code / "artifact/WORKFLOWS/common/build_static_manifest.py"),
            "bowtie2",
            "--runs",
            p["manifest"],
            "--dataset-id",
            p["dataset_id"],
            "--out",
            str(expected_path),
        ],
        check=True,
    )
    expected = {
        (r["process"], r["task_instance"])
        for r in csv.DictReader(expected_path.open(), delimiter="\t")
    }
    assert len(expected) == p["expected_tasks"]
    successes = {}
    attempts = []
    counts = collections.Counter()
    for file in (camp / "task_outcomes").glob("*.outcome.json"):
        x = json.loads(file.read_text())
        o = x["task_outcome"]
        attempts.append(x)
        counts[x["exit_status"]] += 1
        if x["exit_status"] == 0:
            assert (
                o["peak_memory_bytes"] is not None and o["consumed_bytes"] is not None
            ), file
            k = (o["process"], o["task_instance"])
            if (
                k not in successes
                or o["completion_time"] > successes[k]["completion_time"]
            ):
                successes[k] = o
    if set(successes) != expected:
        raise RuntimeError(
            f"Coverage mismatch: {len(expected-set(successes))} missing, {len(set(successes)-expected)} unexpected"
        )
    trace = list(
        csv.DictReader(
            (run / "results/pipeline_info/execution_trace.txt").open(), delimiter="\t"
        )
    )
    completed = {
        (r["process"], r["tag"])
        for r in trace
        if r["status"] in ("COMPLETED", "CACHED") and r["exit"].strip() == "0"
    }
    assert completed == expected, (
        "Nextflow trace coverage mismatch",
        len(expected - completed),
    )
    bam = sorted((run / "results/bam").glob("*.bam"))
    bai = list((run / "results/bam").glob("*.bai"))
    flags = list((run / "results/flagstat").glob("*.flagstat.txt"))
    assert len(bam) == len(bai) == len(flags) == p["expected_chunks"]
    for file in bam + bai + flags:
        assert file.exists() and file.stat().st_size > 0, file
    subprocess.run(
        [
            "apptainer",
            "exec",
            "--bind",
            f"{ROOT}:{ROOT}",
            str(ROOT / "containers/samtools-1.20.sif"),
            "samtools",
            "quickcheck",
            *[str(x) for x in bam],
        ],
        check=True,
    )
    pointer = json.loads((camp / "current_model.json").read_text())
    model = Path(pointer["model_root"])
    history = Path(pointer["history_features"])
    assert not (camp / "learner.ready").exists(), "Learner has not closed its state"
    with sqlite3.connect(camp / "online_learner_state.sqlite3") as c:
        assert c.execute("pragma integrity_check").fetchone()[0] == "ok"
        eligible = c.execute("select count(*) from online_rows").fetchone()[0]
        processed = c.execute("select count(*) from processed_outcomes").fetchone()[0]
        assert processed == len(attempts), (processed, len(attempts))
        assert eligible == pointer["eligible_count"]
        assert (
            c.execute(
                "select model_version from model_updates order by sequence desc limit 1"
            ).fetchone()[0]
            == pointer["model_version"]
        )
    rows = list(csv.DictReader(history.open(), delimiter="\t"))
    ids = {r["logical_task_id"] for r in rows}
    assert len(ids) == len(rows)
    target = sum(r["workflow"].lower() == "bowtie2" for r in rows)
    inherited = state_from_parent(p)["expected_bowtie2_history_rows"]
    assert target == inherited + eligible
    temp = destination.with_name(
        destination.name + ".tmp-" + os.environ.get("SLURM_JOB_ID", "local")
    )
    if temp.exists():
        shutil.rmtree(temp)
    temp.mkdir(parents=True)
    shutil.copytree(model, temp / "model")
    shutil.copy2(history, temp / "history_features.tsv")
    shutil.copy2(
        camp / "online_learner_state.sqlite3", temp / "online_learner_state.sqlite3"
    )
    with sqlite3.connect(camp / "inference_history.sqlite3") as src, sqlite3.connect(
        temp / "history.sqlite3"
    ) as dst:
        src.backup(dst)
    with sqlite3.connect(temp / "history.sqlite3") as c:
        raw = c.execute("select count(*) from task_outcomes").fetchone()[0]
        c.execute("create temp table keep_ids (task_id text primary key)")
        c.executemany("insert into keep_ids values (?)", ((x,) for x in ids))
        c.execute(
            "delete from task_feature_classes where task_id not in (select task_id from keep_ids)"
        )
        c.execute(
            "delete from task_outcomes where task_id not in (select task_id from keep_ids)"
        )
        c.commit()
        assert {r[0] for r in c.execute("select task_id from task_outcomes")} == ids
        assert c.execute("pragma integrity_check").fetchone()[0] == "ok"
        c.execute("vacuum")
    check = subprocess.run(
        [
            plan()["settings"]["python"],
            str(
                code
                / "experiment/camp/live_online_learning/scripts/preflight_run_inputs.py"
            ),
            "--workflow",
            "bowtie2",
            "--model-root",
            str(temp / "model"),
            "--history-features",
            str(temp / "history_features.tsv"),
            "--history-db",
            str(temp / "history.sqlite3"),
            "--base-training-frame",
            str(temp / "model/base_training_frame.tsv"),
            "--expected-workflow-rows",
            str(target),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    (temp / "warm-input-preflight.json").write_text(check.stdout)
    report = {
        "status": "PASS",
        "verified_at": time.time(),
        "phase": key,
        "successful_unique_tasks": len(successes),
        "expected_tasks": len(expected),
        "successful_attempt_observations": eligible,
        "duplicate_success_observations": eligible - len(expected),
        "inherited_bowtie2_observations": inherited,
        "attempt_exit_counts": dict(counts),
        "verified_bam_files": len(bam),
        "verified_bai_files": len(bai),
        "verified_flagstat_files": len(flags),
        "samtools_quickcheck": "PASS",
        "model_version": pointer["model_version"],
        "model_root": str(destination / "model"),
        "history_features": str(destination / "history_features.tsv"),
        "history_db": str(destination / "history.sqlite3"),
        "base_training_frame": str(destination / "model/base_training_frame.tsv"),
        "expected_bowtie2_history_rows": target,
        "history_rows_matching_model": len(ids),
        "raw_history_rows": raw,
        "excluded_raw_diagnostic_rows": raw - len(ids),
        "raw_history_retained_at": str(camp / "inference_history.sqlite3"),
        "calibration_and_history_preflight": json.loads(check.stdout),
        "resource_protocol": "Frozen final settings, explicit 128 MiB execution allowance; predictions and actual grants reported separately.",
        "history_protocol": "All fitted observations retained, including repeated successful attempts. Failed diagnostics retained separately; warm seed projects exactly the model-used observation IDs.",
    }
    atomic(temp / "handoff.json", report)
    files = sorted(x for x in temp.rglob("*") if x.is_file())
    (temp / "SHA256SUMS").write_text(
        "".join(digest(x) + "  " + str(x.relative_to(temp)) + "\n" for x in files)
    )
    if destination.exists():
        raise RuntimeError("Unexpected existing checkpoint directory")
    temp.replace(destination)
    event(
        key,
        "validation_passed",
        model_version=report["model_version"],
        eligible=eligible,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except Exception as error:
        atomic(
            control(sys.argv[1]) / "validation-error.json",
            {"time": time.time(), "error": repr(error)},
        )
        event(sys.argv[1], "validation_failed", error=repr(error))
        raise
