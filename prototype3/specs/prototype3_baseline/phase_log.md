# Phase Log (Baseline Spec Layer)

## Context
This folder records a manual Spec Kit-style baseline for Prototype 3 without introducing tooling changes or repository restructuring.

## Completed Phases (Checkpointed)
- Phase 3.4a: planner/schema contract alignment (commit 4eded0c)
- Phase 3.4b: deterministic rejection-before-execution gate (commit 8f7d0c5)
- Phase 3.4c: benchmark/schema alignment (commit adc922c)
- Phase 3.4d: baseline specification documents (commit c6e6218)
- Phase 3.4e: schema vocabulary audit and evaluation plan update (commit ad22a20)
- Phase 3.5: semantic scoring implementation and spec alignment (commit 94d0a59)
- Phase 3.6: semantic_failure_mode field in benchmark runner (commit e709ef9)

## Phase 3.5 Summary
- Implemented deterministic semantic comparator in src/eval/scoring.py.
- Extended failure_mode taxonomy to full spec-aligned vocabulary.
- Added 15 net new tests in tests/test_scoring.py (20 total, all passing).
- Full controlled-temp suite: 130/130 passed, zero regressions.

### Files changed
- src/eval/scoring.py: added _first_failure_mode helper; extended score_semantics with
  granular failure_mode detection; aligned all tokens to semantic_scoring_rules.md vocabulary.
- tests/test_scoring.py: added 15 new tests covering EXECUTE_EXACT and EXECUTE_FLEXIBLE
  edge cases; removed phase annotation comment; fixed schema-invalid test fixture.

### Failure mode tokens now implemented
- exact_match, acceptable_equivalent, correct_reject
- wrong_object, wrong_target, wrong_action
- unnecessary_extra_action, missing_action
- false_accept, false_reject
- malformed_or_unparseable_output, unsupported_action
- semantic_mismatch (catch-all), parse_error (fallback)

### Deferred items (tracked, not blocking)
- missing_action and wrong_action are live code tokens not yet documented in
  semantic_scoring_rules.md. Must be added before Phase 3.9 evidence pack.
- EXECUTE_FLEXIBLE partial credit logic limitation: place actions without an object key
  will not trigger acceptable_equivalent (object is None). Known gap; deferred to Phase 3.6.
- pick+place equivalence not implemented: not documented in semantic_scoring_rules.md.

## Phase 3.6 Summary
- Added semantic_failure_mode field to the run_benchmark output record in src/eval/run_benchmark.py.
- Field carries the Phase 3.5 scoring taxonomy token (exact_match, wrong_object, false_accept, etc.)
  alongside the existing gate-level failure_mode field. The two fields serve distinct purposes and
  must remain separate.
- Updated two stale SemanticScore fixtures in tests/test_run_benchmark.py from failure_mode="none"
  to failure_mode="exact_match" to match Phase 3.5 vocabulary.
- Added three new tests: field presence, correct exact_match value (C01), wrong_object value (C04).

## Phase 3.7 Summary
- Added src/eval/run_metadata.py: collect_run_metadata() collects 14 reproducibility fields
  (git commit hash, Python/OS/CPU info, psutil RAM, planner config, timestamps). Never raises.
- Modified src/eval/run_benchmark.py: sidecar JSON (run_metadata_*.json) written per model loop;
  "category" and "run_metadata_path" fields added to every run record;
  model names sanitised with re.sub for Windows-safe filenames.
- Modified src/eval/metrics_logger.py: added write_summary_csv(jsonl_path, csv_path) -> int
  with fixed 14-column order; raises ValueError if JSONL does not exist.
- Added tests/test_run_metadata.py: 4 new unit tests for metadata collection.
- Added 2 tests to tests/test_run_benchmark.py: sidecar JSON creation, category/run_metadata_path fields.
- Added 2 tests to tests/test_metrics_logger.py: CSV column order, missing-file error.
- Full controlled-temp suite: 141/141 passed, zero regressions.

### Files changed
- src/eval/run_metadata.py (new)
- src/eval/run_benchmark.py (add imports, sidecar write, record fields)
- src/eval/metrics_logger.py (add write_summary_csv)
- tests/test_run_metadata.py (new, 4 tests)
- tests/test_run_benchmark.py (+2 tests)
- tests/test_metrics_logger.py (+2 tests, updated import)

## Phase 3.8 Summary
- Updated src/eval/__main__.py to delegate module execution to run_benchmark.main().
- Extended src/eval/run_benchmark.py main() to auto-export CSV summaries and print
  a compact post-run metrics summary (records written, schema valid, execution eligible,
  and connection errors when present).
- Added two CLI-behavior tests in tests/test_run_benchmark.py:
  test_main_produces_csv_alongside_jsonl and test_main_prints_summary_to_stdout.
- Full controlled-temp suite after Phase 3.8 changes: 144/144 passed, zero regressions.

### Files changed
- src/eval/__main__.py (delegate to run_benchmark.main)
- src/eval/run_benchmark.py (CLI CSV auto-export + printed summary)
- tests/test_run_benchmark.py (+2 CLI tests)

## Phase 3.9 Summary
- Added src/eval/comparison.py: aggregate_model_metrics() groups per-record JSONL by model
  and computes 10 summary fields (counts, rates, false accept/reject, mean latency).
- Added write_comparison_csv() to src/eval/metrics_logger.py.
- Extended src/eval/run_benchmark.py main() to auto-export a per-model comparison CSV
  (alongside the per-record CSV) when more than one model is in the run.
- Added tests/test_comparison.py: 4 unit tests for aggregation logic.
- Added 2 tests to tests/test_metrics_logger.py: comparison CSV column order, missing-file error.
- Added 2 tests to tests/test_run_benchmark.py: comparison CSV produced for multi-model runs,
  skipped for single-model runs.
- Full controlled-temp suite after Phase 3.9 changes: 152/152 passed, zero regressions.

### Files changed
- src/eval/comparison.py (new)
- src/eval/metrics_logger.py (add write_comparison_csv, module-level import)
- src/eval/run_benchmark.py (add write_comparison_csv to imports, comparison export in main)
- tests/test_comparison.py (new, 4 tests)
- tests/test_metrics_logger.py (+2 tests)
- tests/test_run_benchmark.py (+2 tests)

## Current Phase
- Phase 3.9: complete — pending commit

## Phase 3.4 Audit Finding: moveee
- moveee is present in schema validation, planner contract prompt, safety validation tests, and schema tests.
- moveee is not present in benchmark_v1 gold_intents after benchmark alignment.
- Classification: intentional supported primitive with low benchmark usage, not removed in this phase.

## What Was Added In Baseline Specs
- specs/prototype3_baseline/overview.md
- specs/prototype3_baseline/requirements.md
- specs/prototype3_baseline/architecture.md
- specs/prototype3_baseline/action_schema_contract.md
- specs/prototype3_baseline/planner_contract.md
- specs/prototype3_baseline/safety_gate.md
- specs/prototype3_baseline/benchmark_plan.md
- specs/prototype3_baseline/evaluation_plan.md
- specs/prototype3_baseline/phase_log.md
- specs/prototype3_baseline/semantic_scoring_rules.md

## Guardrails Applied
- Documentation only for this audit update.
- No changes to src/, tests/, datasets/, or runtime pipeline behavior.

## Exit Criteria Snapshot
- Vocabulary audit completed with explicit moveee decision.
- Semantic scoring categories documented.
- Reproducibility metadata requirements documented.
- Phase progression and commit evidence recorded.
