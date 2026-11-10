"""Build the working manuscript in a separate directory; preserve source layout."""
import argparse
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / 'Big_Data_paper' / 'Big_Data_Camera_Ready'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', choices=['latexmk', 'tectonic'], default='latexmk')
    parser.add_argument('--executable', help='Explicit path to the selected TeX engine')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'build' / 'paper')
    args = parser.parse_args()
    out = args.output_dir.resolve()
    # Never stage a build into the versioned paper source or over its parent.
    if out == PROJECT or PROJECT in out.parents or out in PROJECT.parents:
        parser.error('Choose a build directory separate from the manuscript source')
    compiler = args.executable or shutil.which(args.engine)
    if not compiler:
        parser.error('Compiler not found; use --executable or put it on PATH')
    out.mkdir(parents=True, exist_ok=True)
    shutil.copytree(PROJECT / 'source', out / 'source', dirs_exist_ok=True)
    wrapper = out / 'camp_bigdata.tex'
    text = (r'\RequirePackage[T1]{fontenc}' + '\n') if args.engine == 'tectonic' else ''
    wrapper.write_text(text + r'\input{source/Camera_Ready/main.tex}' + '\n', encoding='utf-8')
    if args.engine == 'tectonic':
        command = [compiler, '-k', '--keep-logs', wrapper.name]
    else:
        command = [compiler, '-pdf', '-interaction=nonstopmode', '-halt-on-error', wrapper.name]
    subprocess.run(command, cwd=out, check=True)
    pdf = out / 'camp_bigdata.pdf'
    if not pdf.is_file():
        raise RuntimeError('Build finished without the expected PDF')
    print('Built:', pdf)


if __name__ == '__main__':
    main()
