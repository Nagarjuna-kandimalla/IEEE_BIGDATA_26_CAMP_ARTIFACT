"""Verify packaged file hashes and optionally gzip integrity (standard library)."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-gzip', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'ARTIFACT_MANIFEST.json').read_text(encoding='utf-8'))
    errors = []
    compressed = 0
    for item in manifest['files']:
        path = (ROOT / item['path']).resolve()
        if ROOT not in path.parents:
            errors.append('Path outside artifact: ' + item['path'])
            continue
        if not path.is_file():
            errors.append('Missing: ' + item['path'])
            continue
        if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            errors.append('Changed: ' + item['path'])
        if args.check_gzip and path.suffix == '.gz':
            try:
                with gzip.open(path, 'rb') as stream:
                    while stream.read(1024 * 1024):
                        pass
                compressed += 1
            except (OSError, EOFError) as error:
                errors.append('Invalid gzip ' + item['path'] + ': ' + str(error))
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print('PASS: {} packaged file hashes; {} gzip streams checked.'.format(len(manifest['files']), compressed))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
