#!/usr/bin/env python3
"""Verified, lossless payload relocation to existing worker EBS."""
import csv, json, os, shutil, socket, subprocess, sys, time
from pathlib import Path
from common import ROOT, BASE, atomic, control, digest, event, phase, plan


def main(key):
    p = phase(key)
    run = Path(p["run_root"])
    out = control(key)
    out.mkdir(parents=True, exist_ok=True)
    assert socket.gethostname() == p["archive_worker"]
    assert json.loads(Path(p["handoff"]).read_text())["status"] == "PASS"
    archive = Path(p["archive_path"])
    record = out / "archive.json"
    if record.exists():
        saved = json.loads(record.read_text())
        assert saved["status"] == "PASS"
        assert (
            archive.stat().st_size == saved["archive_bytes"]
            and digest(archive) == saved["sha256"]
        )
    else:
        listing = subprocess.check_output(
            ["squeue", "-h", "-t", "PD,R,CF,CG,S", "-o", "%Z"], text=True
        )
        assert not any(
            x.startswith(str(run / "work") + "/") for x in listing.splitlines()
        ), "Active stage tasks remain"
        # Check the full paired downloads against their independent ENA MD5 metadata.
        meta = {
            r["run_accession"]: r
            for r in csv.DictReader(open(p["ena_metadata"]), delimiter="\t")
        }
        checks = []
        for row in csv.DictReader(open(p["manifest"]), delimiter="\t"):
            m = meta[row["run_accession"]]
            expected = {
                Path(u).name: h
                for u, h in zip(m["fastq_ftp"].split(";"), m["fastq_md5"].split(";"))
            }
            for field in ["fastq1_url", "fastq2_url"]:
                name = Path(row[field]).name
                matches = list((run / "results/downloads").rglob(name))
                assert len(matches) == 1, (name, matches)
                file = matches[0]
                actual = digest(file, "md5")
                assert actual == expected[name], ("Input MD5 mismatch", file)
                checks.append(
                    {"file": str(file), "md5": actual, "bytes": file.stat().st_size}
                )
        atomic(out / "input-md5.json", {"status": "PASS", "files": checks})
        files = []
        for f in (run / "work").rglob("*"):
            if (
                not f.is_symlink()
                and f.is_file()
                and (f.name.endswith(".fastq.gz") or f.suffix in (".bam", ".bai"))
            ):
                s = f.stat()
                files.append(
                    {
                        "path": str(f.relative_to(run)),
                        "bytes": s.st_size,
                        "mtime_ns": s.st_mtime_ns,
                    }
                )
        assert files, "No payload files found"
        subprocess.run(
            [
                "sudo",
                "-n",
                "install",
                "-d",
                "-o",
                str(os.getuid()),
                "-g",
                str(os.getgid()),
                str(archive.parent),
            ],
            check=True,
        )
        total = sum(x["bytes"] for x in files)
        assert (
            shutil.disk_usage(archive.parent).free
            > total + plan()["settings"]["archive_worker_reserve_bytes"]
        ), "Worker archive disk full"
        atomic(out / "payload-files.json", files)
        filelist = out / "payload-files.nul"
        filelist.write_bytes(b"".join(x["path"].encode() + b"\0" for x in files))
        tmp = archive.with_suffix(".tar.partial")
        subprocess.run(
            [
                "tar",
                "--create",
                "--file",
                str(tmp),
                "--directory",
                str(run),
                "--null",
                "--verbatim-files-from",
                "--no-recursion",
                "--files-from",
                str(filelist),
            ],
            check=True,
        )
        subprocess.run(
            ["tar", "--compare", "--file", str(tmp), "--directory", str(run)],
            check=True,
        )
        with tmp.open("rb") as f:
            os.fsync(f.fileno())
        sha = digest(tmp)
        tmp.replace(archive)
        saved = {
            "status": "PASS",
            "verified_at": time.time(),
            "worker": p["archive_worker"],
            "archive": str(archive),
            "archive_bytes": archive.stat().st_size,
            "payload_bytes": total,
            "payload_files": len(files),
            "sha256": sha,
            "verification": "GNU tar byte comparison against every source, plus SHA256 archive checksum",
            "restore_command": f'tar -xf {archive} -C {run} (run on {p["archive_worker"]})',
        }
        atomic(record, saved)
        event(key, "archive_verified", **saved)
    # Remove only staging copies already verified above. Small files and links stay.
    for x in json.loads((out / "payload-files.json").read_text()):
        f = run / x["path"]
        if not f.exists():
            continue
        assert (
            not f.is_symlink()
            and f.stat().st_size == x["bytes"]
            and f.stat().st_mtime_ns == x["mtime_ns"]
        ), f
        f.unlink()
    atomic(
        out / "archive-cleanup.json",
        {
            "status": "PASS",
            "time": time.time(),
            "controller_free_bytes": shutil.disk_usage(ROOT).free,
        },
    )
    event(key, "payload_relocation_completed")
    print(json.dumps(saved), flush=True)


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except Exception as e:
        atomic(
            control(sys.argv[1]) / "archive-error.json",
            {"time": time.time(), "error": repr(e)},
        )
        raise
