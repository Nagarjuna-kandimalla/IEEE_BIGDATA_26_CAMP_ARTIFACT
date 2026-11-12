#!/usr/bin/env python3
"""Track queued reproduction jobs and resume only verified audited stopped children."""
import json, subprocess, time
from pathlib import Path
from common import ROOT, BASE, atomic, plan

while True:
    try:
        jobs = json.loads((BASE / "jobs.json").read_text())["jobs"]
        raw = subprocess.check_output(
            [
                "sacct",
                "-X",
                "-n",
                "-P",
                "-S",
                "1970-01-01",
                "-j",
                ",".join(str(x["job_id"]) for x in jobs),
                "--format=JobIDRaw,State,ExitCode",
            ],
            text=True,
        )
        states = {
            x.split("|")[0]: x.split("|")[1:3] for x in raw.splitlines() if "|" in x
        }
        atomic(BASE / "status.json", {"updated_at": time.time(), "jobs": states})
        if (BASE / "comparison/reproduction-results.json").exists():
            break
        failed = {
            k: v
            for k, v in states.items()
            if v[0].split()[0]
            in ["FAILED", "OUT_OF_MEMORY", "TIMEOUT", "NODE_FAIL", "CANCELLED"]
        }
        if failed:
            atomic(
                BASE / "failure.json",
                {
                    "time": time.time(),
                    "jobs": failed,
                    "note": "Dependent phases do not bypass validation.",
                },
            )
        settings = plan()["settings"]
        rows = subprocess.check_output(
            ["squeue", "-h", "-t", "R,PD", "-o", "%j|%N|%Z"], text=True
        ).splitlines()
        for worker in settings["workers"]:
            name = "camp-health-" + worker
            if any(x.startswith(name + "|") for x in rows):
                continue
            if not any(
                ("|" + worker + "|") in x
                and any(str(p["run_root"]) + "/work/" in x for p in plan()["phases"])
                for x in rows
            ):
                continue
            import shlex

            subprocess.run(
                [
                    "sbatch",
                    "--parsable",
                    "--export=ALL",
                    "--job-name=" + name,
                    "--partition=" + settings["task_partition"],
                    "--nodelist=" + worker,
                    "--cpus-per-task=1",
                    "--mem=128M",
                    "--time=00:02:00",
                    "--output=" + str(BASE / "logs/health-%j.log"),
                    "--wrap="
                    + shlex.join(
                        [
                            "/usr/bin/python3",
                            str(BASE / "code/automation/resume-stopped-audited.py"),
                        ]
                    ),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
            )
    except Exception as e:
        atomic(BASE / "supervisor-error.json", {"time": time.time(), "error": repr(e)})
    time.sleep(45)
