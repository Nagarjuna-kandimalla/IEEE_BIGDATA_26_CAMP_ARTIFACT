"""Portable I/O and routing regressions; no network, sudo, or real Slurm jobs."""

import contextlib, hashlib, importlib.util, json, os, runpy, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

LIVE = Path(__file__).resolve().parents[1]


class PortableTests(unittest.TestCase):
    def test_fetch_verifies_pair_and_rejects_bad_partial(self):
        spec = importlib.util.spec_from_file_location("fetch", LIVE / "fetch_inputs.py")
        fetch = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fetch)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = root / "DATA/RQ5/live/inputs"
            base.mkdir(parents=True)
            fetch.REPO = root
            names = ["RUN_1.fastq.gz", "RUN_2.fastq.gz"]
            contents = {n: ("fixture " + n).encode() for n in names}
            (base / "new_6000.tsv").write_text(
                "run_accession\tfastq1_url\tfastq2_url\nRUN\thttps://example/"
                + names[0]
                + "\thttps://example/"
                + names[1]
                + "\n"
            )
            (base / "new_ena_metadata.tsv").write_text(
                "run_accession\tfastq_ftp\tfastq_md5\nRUN\t"
                + ";".join("example/" + n for n in names)
                + "\t"
                + ";".join(hashlib.md5(contents[n]).hexdigest() for n in names)
                + "\n"
            )
            dest = root / "download"
            args = ["fetch", "--dataset", "new", "--output", str(dest)]

            def download(command, **kwargs):
                Path(command[command.index("-O") + 1]).write_bytes(
                    contents[Path(command[-1]).name]
                )

            with patch.object(sys, "argv", args), patch.object(
                fetch.subprocess, "run", side_effect=download
            ):
                fetch.main()
            self.assertTrue(all((dest / n).read_bytes() == contents[n] for n in names))
            (dest / names[0]).write_bytes(b"bad")
            with patch.object(sys, "argv", args + ["--verify-only"]):
                with self.assertRaises(RuntimeError):
                    fetch.main()

            def corrupt(command, **kwargs):
                Path(command[command.index("-O") + 1]).write_bytes(b"partial")

            with patch.object(sys, "argv", args), patch.object(
                fetch.subprocess, "run", side_effect=corrupt
            ):
                with self.assertRaises(RuntimeError):
                    fetch.main()
            self.assertEqual((dest / names[0]).read_bytes(), b"bad")

    def test_task_routing_matches_partition_and_adds_allowance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "deployment").mkdir()
            (root / "experiments").mkdir()
            run = root / "live/runs/phase"
            work = run / "work/aa/bb"
            work.mkdir(parents=True)
            (root / "experiments/plan.json").write_text(
                json.dumps(
                    {
                        "registered_run_ids": ["phase"],
                        "settings": {
                            "controller_node": "head",
                            "workers": ["worker-a", "worker-b"],
                            "per_worker_task_admission": 16,
                            "task_partition": "compute",
                        },
                    }
                )
            )
            (work / ".command.run").write_text(
                "#!/bin/bash\n#SBATCH --mem=123M\n#SBATCH --nodelist=head\necho task\n"
            )
            old = Path.cwd()
            captured = []

            def execute(path, args):
                captured.extend(args)
                raise SystemExit(0)

            try:
                os.chdir(work)
                with patch.dict(
                    os.environ,
                    {"CAMP_RQ5_LIVE_ROOT": str(root), "CAMP_RUN_ID": "phase"},
                ), patch.object(sys, "argv", ["sbatch", ".command.run"]), patch(
                    "subprocess.check_output", return_value=""
                ), patch(
                    "os.execv", side_effect=execute
                ):
                    with self.assertRaises(SystemExit):
                        runpy.run_path(
                            str(LIVE / "runtime/route_worker_submission.py"),
                            run_name="__main__",
                        )
            finally:
                os.chdir(old)
            self.assertIn("--partition=compute", captured)
            self.assertIn("--nodelist=worker-a", captured)
            self.assertIn("--mem=251M", captured)
            grant = json.loads((work / ".execution-memory-grant.json").read_text())
            self.assertEqual(grant["camp_prediction_mib"], 123)
            self.assertEqual(grant["execution_allowance_mib"], 128)
            self.assertNotIn(
                "--nodelist=head", (work / ".command.worker.run").read_text()
            )


if __name__ == "__main__":
    unittest.main()
