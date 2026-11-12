#!/usr/bin/env bash
# Invoke with sudo. Use only on systemd worker hosts with an auditor budget
# reserved separately from Slurm task capacity. Task cgroups are unchanged.
set -euo pipefail
case "$(uname -m)" in
  x86_64) openat_nr=257 ;;
  aarch64) openat_nr=56 ;;
  *) echo 'Unsupported architecture for raw openat compatibility mode.' >&2; exit 1 ;;
esac
exec /usr/bin/systemd-run --quiet --wait --pipe --collect \
  --service-type=exec \
  --property=MemoryMax=1G \
  --property=MemorySwapMax=0 \
  --property=KillMode=control-group \
  "--setenv=CAMP_BCC_CFLAGS=-fms-extensions -DCAMP_RAW_OPENAT -DCAMP_OPENAT_NR=$openat_nr" \
  /usr/bin/python3 "$@"
