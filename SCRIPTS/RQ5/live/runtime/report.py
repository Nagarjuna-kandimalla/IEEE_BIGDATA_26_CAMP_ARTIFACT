#!/usr/bin/env python3
import csv, json, time
from pathlib import Path
from common import BASE, phase, plan, atomic

results = {}
for p in plan()["phases"]:
    hand = json.loads(Path(p["handoff"]).read_text())
    assert hand["status"] == "PASS"
    folder = Path(p["run_root"]) / "results/metrics/camp"
    rows = [
        x
        for x in csv.DictReader((folder / "task_instances.tsv").open(), delimiter="\t")
        if x["final_success"].lower() in ("true", "1")
    ]
    assert (
        len(rows) == 6000
        and len({(x["process"], x["task_instance"]) for x in rows}) == 6000
    )
    request = [float(x["first_applied_allocation_mib"]) for x in rows]
    peak = [float(x["final_peak_mib"]) for x in rows]
    runtime = [float(x["final_runtime_seconds"]) for x in rows]
    g = json.loads((folder / "summary.json").read_text())["global"]
    results[p["key"]] = {
        "tasks": 6000,
        "request_gib": sum(request) / 1024,
        "peak_gib": sum(peak) / 1024,
        "wastage_gibh": sum(
            max(a - b, 0) * t / 3600 / 1024 for a, b, t in zip(request, peak, runtime)
        ),
        "coverage_percent": 100 * sum(a >= b for a, b in zip(request, peak)) / 6000,
        "mdape_percent": g["a_plus_p_plus_c_point_median_ape_percent"],
        "oom_attempts": g["total_oom_attempts"],
        "duplicate_success_observations": hand["duplicate_success_observations"],
    }
atomic(
    BASE / "comparison/reproduction-results.json",
    {
        "status": "COMPLETED",
        "time": time.time(),
        "results": results,
        "notes": [
            "Nominal CAMP requests exclude execution allowance and failed-attempt costs.",
            "Direct-Transfer uses the parent cold checkpoint/history recorded in the plan and skips warm.",
            "Live completion order and measurements can change the online trajectory and results. These are new runs, not exact numerical replication guarantees.",
        ],
    },
)
print(json.dumps(results, indent=2))
