#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Standalone build/event-stream launcher, added 2026-11-10.
"""Compile the unchanged Ponder core and run causal TSV events; no scheduler."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / '.build'


def verify(path, expected):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f'Checksum mismatch: {path}')


def build():
    manifest = json.loads((ROOT / 'upstream_manifest.json').read_text())
    for item in manifest['files']:
        verify(ROOT / item['local_path'], item['sha256'])
    jars = []
    for item in manifest['dependencies']:
        path = BUILD / 'lib' / item['name']
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            data = urllib.request.urlopen(item['url'], timeout=60).read()
            if hashlib.sha256(data).hexdigest() != item['sha256']:
                raise ValueError(f'Download checksum mismatch: {item["name"]}')
            path.write_bytes(data)
        verify(path, item['sha256'])
        jars.append(path)
    classes = BUILD / 'classes'
    classes.mkdir(parents=True, exist_ok=True)
    sources = sorted((ROOT / 'upstream' / 'src').rglob('*.java'))
    sources += sorted((ROOT / 'src').rglob('*.java'))
    sources += sorted((ROOT / 'tests').rglob('*.java'))
    classpath = os.pathsep.join(map(str, jars))
    subprocess.run(['javac', '--release', '11', '-encoding', 'UTF-8', '-cp', classpath,
                    '-d', str(classes), *map(str, sources)], check=True)
    return os.pathsep.join([str(classes), classpath])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('test', help='Compile and run correctness checks on synthetic histories')
    run = sub.add_parser('run', help='Process ordered TSV events; writes a new output file')
    run.add_argument('--events', required=True, type=Path)
    run.add_argument('--output', required=True, type=Path)
    run.add_argument('--min-bytes', type=int)
    run.add_argument('--max-bytes', type=int)
    args = parser.parse_args()
    # Refuse overwrites before compilation/downloads.
    if args.command == 'run' and args.output.exists():
        parser.error('Output exists; select a new file')
    classpath = build()
    if args.command == 'test':
        subprocess.run(['java', '-ea', '-cp', classpath, 'camp.baselines.PonderAdapterTest'], check=True)
    else:
        command = ['java', '-cp', classpath, 'camp.baselines.PonderAdapter']
        for name in ('min_bytes', 'max_bytes'):
            value = getattr(args, name)
            if value is not None:
                command += ['--' + name.replace('_', '-'), str(value)]
        # Binary file handles avoid shell/pipeline encoding differences on Windows.
        # A failed run may leave partial output: exit status must be checked.
        with args.events.open('rb') as source, args.output.open('xb') as target:
            subprocess.run(command, stdin=source, stdout=target, check=True)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
