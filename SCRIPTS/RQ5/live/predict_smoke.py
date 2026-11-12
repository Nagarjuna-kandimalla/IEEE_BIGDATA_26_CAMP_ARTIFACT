#!/usr/bin/env python3
"""Load a restored immutable checkpoint and make three prelaunch predictions."""
import argparse, json, sys, tempfile, shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--checkpoint", type=Path, required=True)
p.add_argument("--initial", type=Path, required=True)
a = p.parse_args()
sys.path.insert(
    0, str(REPO / "SCRIPTS/RQ5/experiment_template/camp/live_online_learning")
)
from camp_online.engine import OnlineCampEngine

with tempfile.TemporaryDirectory(prefix="camp-policies-") as directory:
    policies = Path(directory)
    shutil.copytree(a.initial / "policies", policies, dirs_exist_ok=True)
    (policies / "a_plus_p_plus_c").mkdir(exist_ok=True)
    shutil.copy2(
        a.initial / "camp_policy.json",
        policies / "a_plus_p_plus_c/process_tail_selected_policy.json",
    )
    engine = OnlineCampEngine(
        model_root=a.checkpoint / "model",
        history_features=a.checkpoint / "history_features.tsv",
        cold_start_root=a.initial / "workflow_cold/models",
        cold_start_policy=a.initial / "workflow_cold/policy.json",
        policy_root=policies,
        config_path=REPO
        / "SCRIPTS/RQ5/experiment_template/camp/original_offline_replay/config/experiment.json",
        camp_policy_path=a.initial / "camp_policy.json",
    )
    results = []
    for process, field in [
        ("ALIGN_CHUNK", "staged_original_input_bytes"),
        ("INDEX_BAM", "staged_intermediate_input_bytes"),
        ("FLAGSTAT_BAM", "staged_intermediate_input_bytes"),
    ]:
        result = engine.predict(
            {
                "task_id": "portability-test:" + process,
                "workflow": "bowtie2",
                "process": process,
                "version": "bowtie2-2.4.2+custom-nextflow",
                "system_config_id": "sc13",
                "static_input_bytes": 8000000,
                field: 8000000,
                "requested_threads": 2 if process == "ALIGN_CHUNK" else 1,
                "task_instance": "SRR_PORTABLE_UNSEEN_chunk_1",
                "input_identity": "portable-test-8000000",
                "decision_time": "2026-11-12T00:00:00+00:00",
            }
        )
        assert result["recommended_allocation_mb"] > 0
        results.append(
            {
                "process": process,
                "allocation_mib": result["recommended_allocation_mb"],
                "model_version": result["model_version"],
                "c_hat_bytes": result["c_hat_bytes"],
            }
        )
    print(json.dumps({"status": "PASS", "predictions": results}, indent=2))
