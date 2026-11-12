import json, os, signal, socket, subprocess, time
from pathlib import Path

root = Path(os.environ["CAMP_RQ5_LIVE_ROOT"]).resolve()
runs = [
    Path(x["run_root"])
    for x in json.loads((root / "experiments/plan.json").read_text())["phases"]
]
host = socket.gethostname()
listing = subprocess.check_output(
    ["/usr/bin/squeue", "-h", "-t", "R", "-o", "%i|%N|%Z"], text=True
)
actions = []
for line in listing.splitlines():
    fields = line.split("|", 2)
    if len(fields) != 3:
        continue
    job, node, work = fields
    if node != host or not any(
        work.startswith(str(run / "work") + "/") for run in runs
    ):
        continue
    path = Path(work)
    key = path.parent.name + path.name
    script = path / ".command.run"
    if not script.exists():
        continue
    import re

    matches = re.findall(r"local ready_file='([^']+)'", script.read_text())
    if len(matches) != 1:
        continue
    ready = Path(matches[0])
    trace = ready.parent
    try:
        pid = int((trace / "task_pid.txt").read_text())
        launcher = int((trace / "audit_launcher_pid.txt").read_text())
        if not ready.exists() or int(ready.read_text()) != pid:
            continue
        proc = Path("/proc") / str(pid)
        if "job_" + job + "/" not in (proc / "cgroup").read_text():
            continue
        state = (proc / "status").read_text().split("State:", 1)[1].strip()[0]
        if state not in ("T", "t"):
            continue
        if not Path("/proc", str(launcher)).exists():
            continue
        launcher_state = (
            Path("/proc", str(launcher), "status")
            .read_text()
            .split("State:", 1)[1]
            .strip()[0]
        )
        if launcher_state == "Z":
            continue
        if time.time() - ready.stat().st_mtime < 5:
            continue
        os.kill(pid, signal.SIGCONT)
        actions.append(
            {
                "time": time.time(),
                "host": host,
                "job_id": int(job),
                "task_pid": pid,
                "audit_launcher_pid": launcher,
                "ready_file": str(ready),
                "action": "SIGCONT after verified audit readiness",
            }
        )
    except (FileNotFoundError, ProcessLookupError, ValueError, PermissionError):
        continue
out = (
    root
    / "deployment"
    / ("stopped-task-recovery-" + os.environ["SLURM_JOB_ID"] + ".json")
)
out.write_text(json.dumps(actions, indent=2) + "\n")
print(json.dumps(actions), flush=True)
