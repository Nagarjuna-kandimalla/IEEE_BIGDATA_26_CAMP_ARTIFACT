#!/usr/bin/env python3
import fcntl, json, os, shutil, subprocess, sys, time
from pathlib import Path
from common import (
    ROOT,
    BASE,
    atomic,
    control,
    digest,
    event,
    phase,
    plan,
    state_from_parent,
)


def main(key):
    p = phase(key)
    settings = {**plan()["settings"], **p.get("resource_overrides", {})}
    code = BASE / "code"
    state = state_from_parent(p)
    with (BASE / "control/stage-execution.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if Path(p["run_root"]).exists():
            raise RuntimeError("Refusing a non-fresh stage directory: " + p["run_root"])
        subprocess.run(
            ["sha256sum", "--check", "--quiet", "SHA256SUMS"], cwd=code, check=True
        )
        free = shutil.disk_usage(ROOT).free
        if free < settings["controller_free_space_before_stage_bytes"]:
            raise RuntimeError(f"Insufficient controller scratch: {free} bytes free")
        for item in json.loads((code / "assets.json").read_text())["containers"]:
            if digest(item["path"]) != item["sha256"]:
                raise RuntimeError("Container changed: " + item["path"])
        env = os.environ.copy()
        env.update(
            {
                "RQ5_ARTIFACT_ROOT": str(code / "artifact"),
                "RQ5_RUN_ROOT": str(ROOT / "live"),
                "RQ5_PYTHON": settings["python"],
                "RQ5_NEXTFLOW": settings["nextflow"],
                "NXF_VER": settings["nextflow_version"],
                "NXF_OPTS": "-Xms256m -Xmx2g",
                "CAMP_EBPF_TRACER": str(code / "deployment/ebpf_audit_py39.py"),
                "CAMP_EBPF_PYTHON_LAUNCHER": str(
                    code / "deployment/isolated_audit_python_parallel.sh"
                ),
                "CAMP_BOWTIE2_IMAGE": str(ROOT / "containers/bowtie2-2.4.2.sif"),
                "CAMP_SAMTOOLS_IMAGE": str(ROOT / "containers/samtools-1.20.sif"),
                "CAMP_APPTAINER_BIND": f"{ROOT}:{ROOT}",
                "CAMP_SLURM_QUEUE": settings["controller_partition"],
                "CAMP_TASK_SLURM_QUEUE": settings["task_partition"],
                "CAMP_WORKER_NODELIST": settings["controller_node"],
                "CAMP_LEARNER_NODELIST": settings["controller_node"],
                "CAMP_WORKER_CONSTRAINT": "",
                "CAMP_QUEUE_SIZE": str(settings["queue_size"]),
                "CAMP_LEARNER_CPUS": str(settings["learner_cpus"]),
                "CAMP_LEARNER_MEMORY": settings["learner_memory"],
                "CAMP_NFS_AUDIT_ACL_UID": str(settings["nfs_audit_uid"]),
                "CAMP_INPUT_MANIFEST": p["manifest"],
                "CAMP_DATASET_ID": p["dataset_id"],
                "OMP_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1",
                "MKL_NUM_THREADS": "1",
            }
        )
        invocation = [
            "bash",
            str(
                code / "experiment/camp/live_online_learning/slurm/run_fresh_bowtie2.sh"
            ),
            str(code / "experiment"),
            p["label"],
            state["model_root"],
            state["history_features"],
            state["history_db"],
            state["base_training_frame"],
            str(state["expected_bowtie2_history_rows"]),
        ]
        record = {
            "status": "RUNNING",
            "started_at": time.time(),
            "job_id": os.environ.get("SLURM_JOB_ID"),
            "phase": p,
            "input_state": state,
            "settings": settings,
            "command": invocation,
            "manifest_sha256": digest(p["manifest"]),
            "code_manifest_sha256": digest(code / "SHA256SUMS"),
        }
        atomic(control(key) / "controller.json", record)
        event(key, "controller_started", job_id=record["job_id"])
        result = subprocess.run(invocation, env=env)
        record.update(
            status="COMPLETED" if result.returncode == 0 else "FAILED",
            finished_at=time.time(),
            returncode=result.returncode,
        )
        atomic(control(key) / "controller.json", record)
        event(key, "controller_exited", returncode=result.returncode)
        return result.returncode


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1]))
    except Exception as error:
        event(sys.argv[1], "controller_failed", error=repr(error))
        raise
