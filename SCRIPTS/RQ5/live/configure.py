#!/usr/bin/env python3
"""Prepare a fresh, portable Slurm reproduction; does not submit jobs."""
import argparse, hashlib, json, os, shutil, sys
from pathlib import Path
from models import REPO, extract, sha


def configure(root, config, saved_cold=False, initial_state=None):
    root = Path(root).resolve()
    settings = json.loads(Path(config).read_text())
    required = [
        "controller_node",
        "controller_partition",
        "task_partition",
        "workers",
        "python",
        "nextflow",
    ]
    for k in required:
        if not settings.get(k):
            raise ValueError("Missing cluster setting " + k)
    if root.exists():
        raise RuntimeError("Refusing existing run workspace " + str(root))
    settings = {
        **json.loads(
            (Path(__file__).parent / "config/cluster.example.json").read_text()
        ),
        **settings,
    }
    settings.update(
        nextflow_version="25.10.7",
        execution_allowance_mib=128,
        audit_service_memory="384M",
        retries_after_initial_attempt=3,
        first_model_update=128,
        update_every=128,
        calibration_window=64,
        seed=1996,
        full_auditing=True,
        archive_worker_reserve_bytes=8 * 2**30,
        controller_free_space_before_stage_bytes=58 * 2**30,
    )
    assert len(settings["workers"]) > 0 and settings["per_worker_task_admission"] > 0
    base = root / "experiments"
    code = base / "code"
    (base / "control").mkdir(parents=True)
    (base / "logs").mkdir()
    (root / "deployment").mkdir()
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree(
        REPO / "SCRIPTS/RQ5/experiment_template", code / "experiment", ignore=ignore
    )
    (
        shutil.copytree(Path(initial_state).resolve(), code / "experiment/artifacts")
        if initial_state
        else extract("initial", code / "experiment/artifacts")
    )
    extract("containers", root / "containers")
    for name in ["bowtie2", "common"]:
        shutil.copytree(
            REPO / "WORKFLOWS" / name, code / "artifact/WORKFLOWS" / name, ignore=ignore
        )
    shutil.copytree(
        Path(__file__).parent / "runtime", code / "automation", ignore=ignore
    )
    (code / "deployment").mkdir()
    for name in [
        "route_worker_submission.py",
        "ebpf_audit_py39.py",
        "isolated_audit_python_parallel.sh",
    ]:
        shutil.copy2(
            Path(__file__).parent / "runtime" / name, code / "deployment" / name
        )
    phases = []
    for study in ["warm_transfer"]:
        for stage in ["cold", "warm", "new_input"]:
            key = f"{study}_{stage}"
            label = key
            manifest = "new_6000.tsv" if stage == "new_input" else "original_6000.tsv"
            parent = (
                None
                if stage == "cold"
                else f"{study}_" + ("cold" if stage == "warm" else "warm")
            )
            phases.append(
                {
                    "key": key,
                    "study": study,
                    "stage": stage,
                    "label": label,
                    "run_root": str(root / "live/runs" / label),
                    "handoff": str(
                        base / f"{study}/checkpoints" / stage / "handoff.json"
                    ),
                    "parent": parent,
                    "manifest": str(REPO / "DATA/RQ5/live/inputs" / manifest),
                    "ena_metadata": str(
                        REPO
                        / "DATA/RQ5/live/inputs"
                        / (
                            "new_ena_metadata.tsv"
                            if stage == "new_input"
                            else "original_ena_metadata.tsv"
                        )
                    ),
                    "dataset_id": (
                        "bowtie2_prjna486148_unseen_6000"
                        if stage == "new_input"
                        else "bowtie2_prjeb11501_online_unseen_6000"
                    ),
                    "expected_tasks": 6000,
                    "expected_chunks": 1974,
                    "archive_worker": settings["workers"][
                        ["cold", "warm", "new_input"].index(stage)
                        % len(settings["workers"])
                    ],
                    "archive_path": str(
                        Path(settings["archive_directory"]) / study / (stage + ".tar")
                    ),
                }
            )
    p = dict(next(p for p in phases if p["key"] == "warm_transfer_new_input"))
    p.update(
        key="direct_transfer_new_input",
        study="direct_transfer",
        label="direct_transfer_new_input",
        run_root=str(root / "live/runs/direct_transfer_new_input"),
        handoff=str(base / "direct_transfer/checkpoints/new_input/handoff.json"),
        parent="warm_transfer_cold",
        archive_path=str(
            Path(settings["archive_directory"]) / "direct_transfer/new_input.tar"
        ),
    )
    phases.append(p)
    if saved_cold:
        extract("warm_transfer_cold", base / "saved-cold-checkpoint")
        p["parent"] = None
        p["seed_handoff"] = str(base / "saved-cold-checkpoint/handoff.json")
        phases = [p]
        settings.update(controller_cpus=2, controller_memory="4G")
    for p in phases:
        (base / "control" / p["key"]).mkdir()
    plan = {
        "schema": 1,
        "phases": phases,
        "registered_run_ids": [p["label"] for p in phases],
        "settings": settings,
        "scope": "Warm-Transfer cold/warm/new-input sequence and Direct-Transfer new-input branch from the same cold checkpoint.",
    }
    (base / "plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    shim = code / "artifact/WORKFLOWS/bowtie2/tool_shims/sbatch"
    shim.write_text(
        '#!/usr/bin/env bash\nset -euo pipefail\nexec /usr/bin/python3 "${CAMP_RQ5_LIVE_ROOT:?}/experiments/code/deployment/route_worker_submission.py" "$@"\n'
    )
    shim.chmod(0o755)
    assets = {
        "containers": [
            {"path": str(p), "sha256": sha(p)}
            for p in sorted((root / "containers").glob("*.sif"))
        ]
    }
    (code / "assets.json").write_text(json.dumps(assets, indent=2) + "\n")
    files = sorted(p for p in code.rglob("*") if p.is_file())
    (code / "SHA256SUMS").write_text(
        "".join(sha(p) + "  " + str(p.relative_to(code)) + "\n" for p in files)
    )
    (root / "cluster.json").write_text(json.dumps(settings, indent=2) + "\n")
    print(root)
    return root


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", required=True, type=Path)
    p.add_argument("--config", required=True, type=Path)
    p.add_argument(
        "--saved-cold",
        action="store_true",
        help="Run only Direct-Transfer from the packaged Warm-Transfer cold checkpoint",
    )
    p.add_argument(
        "--initial-state",
        type=Path,
        help="Use a separately rebuilt artifacts directory instead of the packaged offline seed",
    )
    a = p.parse_args()
    configure(a.root, a.config, a.saved_cold, a.initial_state)
