# Standalone Ponder memory-sizing baseline

Status: extracted and checked on synthetic histories, 2026-11-10. No CAMP
comparison or workflow experiment has been run with this adapter.

This module runs the original Java Ponder predictor without Kubernetes or the
Common Workflow Scheduler. It accepts prelaunch input sizes and previously
completed peak-memory observations, then emits initial memory requests.
The original numerical calculation code is compiled unchanged, using the same
Apache Commons Math version as the pinned upstream project.

See [attribution and extraction record](NOTICE.md) and
[source/dependency hashes](upstream_manifest.json).

## Preserved behavior

- Fewer than five observations: use maximum observed peak plus 128 MiB only
  when a previously observed input is strictly larger than the query input.
  Otherwise return no prediction and retain the original task request.
- Five or more observations: Pearson correlation strictly greater than 0.3
  selects the unequal-loss linear model; otherwise use maximum peak + 128 MiB.
- The regression uses the upstream overprediction loss weight 0.02, optimizer,
  initial guess, tolerances, GiB scaling, prediction bounds, and weighted
  residual-variance offset with a minimum 128 MiB buffer.
- Prediction history is separate for each caller-supplied group. Each observation
  increments the corresponding upstream predictor version.
- A null prediction preserves the original default request. Otherwise the
  extracted request transformation preserves upstream ordered minimum/maximum/
  original-request checks, integer truncation, then rounding up to a full MiB.

The ordered checks matter: an explicit maximum branch can return a request above
the original default, and rounding can exceed a non-MiB-aligned bound. This module
does not silently replace the original behavior with a different clipping formula.
Specify realistic, preferably MiB-aligned bounds in the comparison protocol.

## Deliberate boundary and differences

This is the **Ponder core with no additional outer residual-offset wrapper**,
equivalent to selecting `ponder-offset=none` in the pinned scheduler. Ponder's
own internal buffer/weighted offset is still active. Bare `ponder` in that
scheduler receives an additional default `MaxOffset` wrapper. That extra wrapper
is not included here; report this choice and do not claim that every original
experiment used it. Native scheduler behavior and this explicit baseline
configuration must not be conflated.

The adapter handles one initial allocation per task. Native scheduler rechecks of
queued tasks and native retry behavior are outside its boundary. The replay or
live harness controls outcome release, retries, and task execution. Failed/OOM
observations must not be supplied as successful unconstrained memory targets.

Additional guards reject duplicate outcomes, duplicate initial decisions,
predictions for already-observed targets, inconsistent input sizes, invalid bytes,
and non-finite upstream predictions. The original scaler can silently cast a NaN
to an integer; this adapter fails instead. Do not silently omit a failing case:
retain the error and investigate before using that run for a paper.

## Event interface

Input is UTF-8 TSV, without BOM, with this exact header and six fields per row:

```text
event<TAB>group<TAB>task_id<TAB>input_bytes<TAB>peak_bytes<TAB>default_bytes
```

- `group`: a stable workflow/process/context key. Do not pool different task types
  merely because they have similar names. Use the same grouping rules throughout.
- `task_id`: stable logical identity, unique within the group.
- `input_bytes`: total prelaunch task input size, in integer bytes. Check which
  files count, including shared references; match upstream input-size semantics
  as closely as possible. Compressed read size, uncompressed read size, and
  consumed bytes are not interchangeable.
- `predict`: leave `peak_bytes` empty; supply the task's original/default memory
  request in `default_bytes`. Do not substitute observed peak or CAMP's optimized
  request as the default. Missing original defaults require an explicit,
  development-selected fallback policy disclosed with the results.
- `observe`: supply a positive successful peak in `peak_bytes`; leave
  `default_bytes` empty. Release the event only when the outcome is completed and
  available to the allocator. Source-history observations may precede predictions.

Rows are processed in the supplied order. The adapter prevents using the target's
own already-recorded outcome, but it cannot establish real-world availability of
other tasks without an independently validated event schedule. Keep decision,
completion, and ingestion timestamps in the parent experiment records.

For example: predict task A; predict task B while A is still running; observe A
only after completion; predict task C with A in history. Predicting B must not
automatically reveal A just because A appears earlier in a task table.

Output contains one row per prediction, with group, task identity, history count,
raw prediction bytes (empty for fallback), final request bytes, and status.
All request caps/floors belong in the experiment metadata. Raw prediction is
provided so that any different shared allocation policy can be analyzed separately.

## Running the isolated adapter

The helper uses Python's standard library and an existing JDK 11 or newer.
It verifies original-source hashes and downloads checksum-pinned Java dependencies
into ignored `.build/` on first use. It does not install a scheduler or change
the CAMP environment. Run from the artifact root:

```bash
python SCRIPTS/BASELINES/ponder/ponder.py test
python SCRIPTS/BASELINES/ponder/ponder.py run --events events.tsv --output ponder_predictions.tsv
```

Optional `--min-bytes` and `--max-bytes` must be selected before evaluation.
Neither is silently assumed. Existing output files are refused. A nonzero exit
code means the run failed; an output file may contain only partial results.
Do not use partial predictions as a successful evaluation.

Each invocation starts with empty history. Replay source `observe` events to seed
it. For frozen evaluation, supply all permitted source observations first and no
new evaluation observations. For online evaluation, interleave predictions with
causally available observations. Launch each comparison repetition from its own
source history; do not carry test history across repetitions.

## Validation performed

`ponder.py test` compiles the adapter and original source, then runs 123 checks:

- Empty/short history and strict equality at the observed maximum input size.
- Exact positive regression, lower-bound handling, extrapolation, negative and
  degenerate correlations.
- Forty-eight raw-prediction cases compared exactly against direct calls to the
  unchanged upstream predictor across increasing, noisy histories. These exercise
  unequal-loss fitting and weighted residual offsets as well as startup behavior.
- Separate process histories, causal-interface guards, request-policy branch
  ordering, rounding, non-finite rejection, and actual TSV parsing/output.

These are adapter correctness checks, not independent validation of Ponder's
algorithm or a reproduction of the paper's end-to-end scheduler experiments.
Numerical equality was checked locally with JDK 11; rerun the checks in the
experiment environment before collecting results.

## Remaining work for a CAMP comparison

1. Map our recorded task input sizes, original requests, valid successful peaks,
   process/context identities, and causal release times into this event format.
2. Lock grouping, history population, and request bounds/default policy before
   evaluation. If timestamps are insufficient, use explicit batched replay.
3. Run CAMP under the same task population and information-release schedule.
4. Compute paired coverage and reservation metrics. Only a live execution can
   measure actual Ponder-driven OOMs, retries, and makespan.

Suggested paper wording:

> We evaluate the Ponder memory-sizing predictor using an isolated adapter of
> the authors' implementation (commit 3046e19), with its internal offset and no
> additional outer offset. Both methods receive prior outcomes according to
> the same replay schedule. This comparison evaluates memory-sizing behavior;
> it does not reproduce Ponder's Kubernetes scheduling experiments.

Use that wording only after performing the described comparison. See the
[experiment protocol](../../../BIG_DATA_EXPERIMENT_PROTOCOL.md) for metrics and
interpretation.
