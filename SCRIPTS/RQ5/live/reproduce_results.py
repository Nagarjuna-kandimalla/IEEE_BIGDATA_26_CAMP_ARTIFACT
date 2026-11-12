#!/usr/bin/env python3
"""Recompute all four stage metrics and output comparisons without Slurm/models."""
import argparse, csv, gzip, hashlib, json, statistics
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SOURCE = REPO / "RESULTS/RQ5/live_experiments"


def table(path):
    with gzip.open(path, "rt", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def reproduce(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    phases = json.loads((SOURCE / "studies.json").read_text())["phases"]
    results = {}
    inputs = {}
    for key in phases:
        path = SOURCE / key / "task_instances.tsv.gz"
        rows = [x for x in table(path) if x["final_success"].lower() in ("true", "1")]
        assert (
            len(rows) == 6000
            and len({(x["process"], x["task_instance"]) for x in rows}) == 6000
        )
        request = [float(x["first_applied_allocation_mib"]) for x in rows]
        peak = [float(x["final_peak_mib"]) for x in rows]
        runtime = [float(x["final_runtime_seconds"]) for x in rows]
        assert min(peak) > 0
        median_error = statistics.median(
            abs(float(x["a_plus_p_plus_c_point_q50_mib"]) - y) / y * 100
            for x, y in zip(rows, peak)
        )
        summary = json.loads((SOURCE / key / "summary.json").read_text())["global"]
        assert (
            abs(median_error - summary["a_plus_p_plus_c_point_median_ape_percent"])
            < 1e-8
        )
        handoff = json.loads((SOURCE / key / "handoff.original.json").read_text())
        assert handoff["status"] == "PASS"
        results[key] = {
            "tasks": len(rows),
            "request_gib": sum(request) / 1024,
            "peak_gib": sum(peak) / 1024,
            "unused_gib_hours": sum(
                max(a - b, 0) * t / 3600 / 1024
                for a, b, t in zip(request, peak, runtime)
            ),
            "coverage_percent": sum(a >= b for a, b in zip(request, peak)) / 60,
            "mdape_percent": median_error,
            "first_attempt_ooms": int(summary["first_attempt_ooms"]),
            "oom_attempts": int(summary["total_oom_attempts"]),
            "duplicate_success_observations": handoff["duplicate_success_observations"],
        }
        inputs[str(path.relative_to(REPO))] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    comparisons = {}
    for name, a, b in [
        ("warm_pass_ablation", "warm_transfer_new_input", "direct_transfer_new_input"),
    ]:
        af = SOURCE / a / "flagstat"
        bf = SOURCE / b / "flagstat"
        files = list(af.glob("*.flagstat.txt"))
        assert len(files) == 1974 and {x.name for x in files} == {
            x.name for x in bf.glob("*.flagstat.txt")
        }
        same = sum(x.read_bytes() == (bf / x.name).read_bytes() for x in files)
        comparisons[name] = {
            "flagstat_exact_matches": same,
            "flagstat_total": len(files),
            "percent_change_second_vs_first": {
                k: 100 * (results[b][k] / results[a][k] - 1)
                for k in ["request_gib", "peak_gib", "unused_gib_hours"]
            },
        }
    report = {
        "status": "PASS",
        "results": results,
        "comparisons": comparisons,
        "source_sha256": inputs,
        "definitions": "First nominal CAMP requests, final successful task peak/runtime; excludes +128 MiB execution allowance and failed-attempt/measurement/modeling costs. Direct-Transfer reuses the Warm-Transfer cold checkpoint, not a fresh cold run.",
        "interpretation": "Clean executions can differ numerically due to completion-order-dependent online fitting. Frozen-model evaluation was not performed.",
    }
    (output / "results.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n"
    )
    with (output / "metrics.tsv").open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            ["stage", *next(iter(results.values())).keys()],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows({"stage": k, **v} for k, v in results.items())
    print(
        json.dumps(
            {
                "status": "PASS",
                "stages": len(results),
                "tasks_per_stage": 6000,
                "output": str(output),
            },
            indent=2,
        )
    )
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=REPO / "build/rq5-live-results")
    a = p.parse_args()
    reproduce(a.output)
