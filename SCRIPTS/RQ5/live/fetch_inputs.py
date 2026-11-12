#!/usr/bin/env python3
"""Fetch exact public FASTQs with ENA MD5 validation; never accept partial files."""
import argparse, csv, hashlib, json, os, subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def md5(path):
    h = hashlib.md5()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", choices=["original", "new"], required=True)
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--verify-only", action="store_true")
    p.add_argument("--limit", type=int)
    a = p.parse_args()
    base = REPO / "DATA/RQ5/live/inputs"
    with (base / (a.dataset + "_6000.tsv")).open() as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    with (base / (a.dataset + "_ena_metadata.tsv")).open() as f:
        meta = {r["run_accession"]: r for r in csv.DictReader(f, delimiter="\t")}
    a.output.mkdir(parents=True, exist_ok=True)
    results = []
    for row in rows[: a.limit]:
        expected = {
            Path(u).name: h
            for u, h in zip(
                meta[row["run_accession"]]["fastq_ftp"].split(";"),
                meta[row["run_accession"]]["fastq_md5"].split(";"),
            )
        }
        for field in ["fastq1_url", "fastq2_url"]:
            url = row[field]
            name = Path(url).name
            target = a.output / name
            checksum = expected[name]
            if not target.exists() or md5(target) != checksum:
                if a.verify_only:
                    raise RuntimeError("Missing or invalid FASTQ " + str(target))
                temp = target.with_suffix(target.suffix + ".partial")
                subprocess.run(
                    [
                        "wget",
                        "--tries=10",
                        "--retry-connrefused",
                        "--retry-on-http-error=403,408,429,500,502,503,504",
                        "--timeout=120",
                        "-O",
                        str(temp),
                        url,
                    ],
                    check=True,
                )
                if md5(temp) != checksum:
                    raise RuntimeError(
                        "ENA MD5 mismatch; partial retained for diagnosis: " + str(temp)
                    )
                temp.replace(target)
            results.append(
                {"file": name, "md5": checksum, "bytes": target.stat().st_size}
            )
    (a.output / "input-verification.json").write_text(
        json.dumps({"status": "PASS", "dataset": a.dataset, "files": results}, indent=2)
        + "\n"
    )
    print("PASS:", len(results), "FASTQs verified")


if __name__ == "__main__":
    main()
