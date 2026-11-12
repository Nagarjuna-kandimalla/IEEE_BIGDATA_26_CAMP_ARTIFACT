#!/usr/bin/env python3
"""Submit a configured reproduction once; no historical job IDs are reused."""
import argparse, json, os, shlex, subprocess, time
from pathlib import Path


def submit(root):
    root = Path(root).resolve()
    base = root / "experiments"
    plan = json.loads((base / "plan.json").read_text())
    s = plan["settings"]
    auto = base / "code/automation"
    if (base / "jobs.json").exists():
        raise RuntimeError("Already submitted; refusing duplicate jobs")
    env = os.environ.copy()
    env["CAMP_RQ5_LIVE_ROOT"] = str(root)
    for executable in ["sbatch", "squeue", "scontrol", "sacct"]:
        import shutil

        if not shutil.which(executable):
            raise RuntimeError("Missing " + executable)
    node = subprocess.check_output(
        ["scontrol", "show", "node", s["controller_node"], "-o"], text=True
    )
    cpus = int(node.split("CPUTot=")[1].split()[0])
    assert (
        cpus >= s["controller_cpus"] + s["learner_cpus"] + 1
    ), "Controller/learner/monitor reservations exceed node CPU count"

    def mib(value):
        value = str(value).upper()
        return int(float(value[:-1]) * (1024 if value.endswith("G") else 1))

    assert (
        int(node.split("RealMemory=")[1].split()[0])
        >= mib(s["controller_memory"]) + mib(s["learner_memory"]) + 256
    ), "Controller/learner/monitor memory reservations exceed Slurm capacity"
    for tool in ["python", "nextflow"]:
        if not Path(s[tool]).is_file():
            raise RuntimeError("Configured tool does not exist: " + s[tool])
    jobs = []
    gates = {}
    last = None

    def add(key, kind, script, dependency=None, worker=None, cpus=2, mem="4G"):
        args = [
            "sbatch",
            "--parsable",
            "--export=ALL",
            "--job-name=camp-" + key + "-" + kind,
            "--partition="
            + (s["task_partition"] if worker else s["controller_partition"]),
            "--nodelist=" + (worker or s["controller_node"]),
            "--cpus-per-task=" + str(cpus),
            "--mem=" + mem,
            "--time=24:00:00",
            "--chdir=" + str(root),
            "--output=" + str(base / "logs" / f"{key}-{kind}-%j.log"),
        ]
        if dependency:
            args += ["--dependency=" + dependency]
        args += [
            "--wrap="
            + shlex.join(
                ["/usr/bin/python3", str(auto / script)]
                + ([] if script in ["report.py", "supervisor.py"] else [key])
            )
        ]
        jid = int(
            subprocess.check_output(args, env=env, text=True).strip().split(";")[0]
        )
        jobs.append(
            {
                "phase": key,
                "kind": kind,
                "job_id": jid,
                "dependency": dependency,
                "command": args,
            }
        )
        temp = base / "jobs.json.tmp"
        temp.write_text(
            json.dumps({"submitted_at": time.time(), "jobs": jobs}, indent=2) + "\n"
        )
        temp.replace(base / "jobs.json")
        return jid

    for p in plan["phases"]:
        dependencies = []
        if last:
            dependencies.append(str(last))
        # Direct-Transfer parent explicitly remains Warm-Transfer cold even though its scheduling follows Warm-Transfer new input.
        if p.get("parent") and gates[p["parent"]] not in [last]:
            dependencies.append(str(gates[p["parent"]]))
        controller = add(
            p["key"],
            "controller",
            "run_stage.py",
            "afterok:" + ":".join(dependencies) if dependencies else None,
            cpus=s["controller_cpus"],
            mem=s["controller_memory"],
        )
        validator = add(
            p["key"], "validation", "validate_stage.py", "afterany:" + str(controller)
        )
        gates[p["key"]] = validator
        last = (
            add(
                p["key"],
                "archive",
                "archive_stage.py",
                "afterok:" + str(validator),
                worker=p["archive_worker"],
                mem="1G",
            )
            if s["archive_between_stages"]
            else validator
        )
    report = add("all", "report", "report.py", "afterok:" + str(last))
    monitor = add("all", "supervisor", "supervisor.py", cpus=1, mem="256M")
    print(
        json.dumps(
            {"jobs": jobs, "report_job": report, "supervisor_job": monitor}, indent=2
        )
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True, type=Path)
    a = p.parse_args()
    submit(a.root)
