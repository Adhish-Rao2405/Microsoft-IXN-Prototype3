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

## Phase 3.10 Summary
- Updated specs/prototype3_baseline/semantic_scoring_rules.md to include missing_action and
  wrong_action categories (deferred Phase 3.5 taxonomy debt).
- Added src/eval/evidence.py with generate_evidence_pack(jsonl_path, output_dir), including:
  per-model aggregation reuse, by-difficulty and by-category breakdowns, RQ4 rejection-rate summary,
  and exports for evidence_pack.json, evidence_by_difficulty.csv, evidence_by_category.csv.
- Extended src/eval/run_benchmark.py main() to auto-write the Phase 3.10 evidence pack for
  multi-model runs and print per-model FA/FR/CR summary lines.
- Added tests/test_evidence.py: 4 tests (required keys, output files, rate bounds, missing file).
- Added 1 test to tests/test_run_benchmark.py: evidence_pack.json is produced for multi-model CLI runs.
- Full controlled-temp suite after Phase 3.10 changes: 157/157 passed, zero regressions.

### Files changed
- specs/prototype3_baseline/semantic_scoring_rules.md (+missing_action, +wrong_action)
- src/eval/evidence.py (new)
- src/eval/run_benchmark.py (multi-model evidence pack generation in main)
- tests/test_evidence.py (new, 4 tests)
- tests/test_run_benchmark.py (+1 evidence-pack CLI test)

### Foundry Local Evidence (qwen2.5-coder-0.5b, cpu)
- Source run: results/runs/phase_3_10_evidence_foundry_alias_cpu_clean.jsonl (30 records)
- Evidence pack generated at results/summaries/foundry_evidence/:
  evidence_pack.json, evidence_by_difficulty.csv, evidence_by_category.csv
- Model-level false accept rate: 12/30 (40.0%) — model produced plans for REJECT_* commands; pipeline false accept rate: 0/30 (0.0%) — rejection gate caught all 12.
- Dissertation interpretation: The local model was often capable of producing schema-valid outputs,
  but schema validity alone did not imply safe or correct task execution. Although 25/30 responses
  were schema-valid, only 4/30 were execution eligible after semantic and rejection-before-execution
  checks. Most importantly, the model produced 12 plans for commands that should have been rejected,
  but the deterministic pipeline prevented all of them from becoming execution-eligible. This supports
  the dissertation’s zero-trust planning argument: local LLM/SLM outputs should be treated as
  untrusted proposals, not executable robot commands.

## Phase 3.10 Operational Notes (post-commit additions)
- Added 25 model aliases to src/brain/foundry_planner.py SUPPORTED_ALIASES to enable GPU model
  backends for RQ5 multi-model runs (qwen2.5-0.5b, qwen2.5-coder-1.5b, qwen2.5-1.5b, phi-4-mini,
  qwen3-1.7b, and forward-looking Qwen3/Phi-4 variants).
- Added --compare CLI mode to src/eval/run_benchmark.py main(): accepts multiple JSONL paths,
  merges records, writes comparison CSV and evidence pack in one command. Merged JSONL written
  to results/runs/; comparison CSV and evidence pack written to results/summaries/.
- Added 3 tests to tests/test_run_benchmark.py: compare mode merges and writes CSV (with merged
  JSONL in runs/), missing file is skipped without error, evidence pack is produced.
- Full controlled-temp suite after operational additions: 160/160 passed, zero regressions.

### Files changed
- src/brain/foundry_planner.py (alias expansion)
- src/eval/run_benchmark.py (--compare mode, merged JSONL path fix)
- tests/test_run_benchmark.py (+3 compare-mode tests)

## Phase 3.11 Summary — RQ5 Multi-Model Comparison Evidence

A clean RQ5 comparison run was completed using Foundry Local with the same 30-command benchmark
and deterministic evaluation pipeline. Each model was evaluated using the same schema validation,
semantic scoring, uncertainty assessment, safety validation, and rejection-before-execution gate.

### Infrastructure changes in this phase
- Expanded SUPPORTED_ALIASES in src/brain/foundry_planner.py from 2 to 27 entries to cover all
  available Foundry Local models (qwen2.5-*, qwen3-*, phi-4-*, phi-3-*, deepseek-r1-*, mistral-*,
  gpt-oss-20b). Previous runs failed with unknown_model_error for any alias not in the set.
- Added --compare CLI mode to src/eval/run_benchmark.py: accepts multiple JSONL paths, merges
  records, writes merged JSONL to results/runs/, comparison CSV to --output path, and evidence
  pack to a sibling _evidence/ directory.
- Added 3 tests to tests/test_run_benchmark.py covering compare mode:
  merge+CSV, missing-file skip, and evidence pack generation.
- Fixed pytest.ini: added tmp_path_retention_count=1 and tmp_path_retention_policy=failed to
  prevent Windows basetemp permission errors on cleanup.
- Full controlled-temp suite: 160/160 passed, zero regressions.

### Canonical RQ5 artefacts
- results/runs/rq5_qwen25_coder_05b_cpu.jsonl
- results/runs/rq5_qwen25_05b_cpu.jsonl
- results/runs/rq5_qwen25_coder_15b_cpu.jsonl
- results/runs/rq5_qwen25_15b_cpu.jsonl
- results/summaries/rq5_comparison.csv
- results/summaries/rq5_comparison_evidence/evidence_pack.json

Note: phi-3-mini-4k and qwen3-1.7b were attempted but produced 30/30 Foundry connection errors
(model not downloaded). Both contaminated files were deleted. The RQ5 comparison uses only
the four Qwen 2.5 models with zero connection errors.

### RQ5 Comparison Results (4 models, 30 commands each, CPU, temp=0.0, max_tokens=256)

| model | sv | sv_rate | ee | ee_rate | fa | fr | cr | lat_ms |
|---|---|---|---|---|---|---|---|---|
| qwen2.5-coder-0.5b:cpu | 25/30 | 83.3% | 4/30 | 13.3% | 12 | 0 | 5 | 2921.7 |
| qwen2.5-0.5b:cpu       | 14/30 | 46.7% | 2/30 |  6.7% |  8 | 0 | 9 | 3616.5 |
| qwen2.5-coder-1.5b:cpu | 28/30 | 93.3% | 5/30 | 16.7% | 15 | 0 | 2 | 8329.5 |
| qwen2.5-1.5b:cpu       | 23/30 | 76.7% | 3/30 | 10.0% | 10 | 0 | 7 | 8299.1 |

RQ4 rates from comparison evidence pack:
- qwen2.5-coder-0.5b:cpu  FA=40.0%  FR=0.0%  CR=16.7%
- qwen2.5-0.5b:cpu        FA=26.7%  FR=0.0%  CR=30.0%
- qwen2.5-coder-1.5b:cpu  FA=50.0%  FR=0.0%  CR= 6.7%
- qwen2.5-1.5b:cpu        FA=33.3%  FR=0.0%  CR=23.3%

Pipeline false accept rate: 0% across all four models. All model-level false accepts were
caught by the deterministic rejection gate.

### Files changed
- src/brain/foundry_planner.py (SUPPORTED_ALIASES expanded to 27 entries)
- src/eval/run_benchmark.py (--compare mode, output file truncation on each run start)
- pytest.ini (tmp_path retention policy)
- tests/test_run_benchmark.py (+3 compare-mode tests)

## Current Phase
- Phase 3.11: complete — RQ5 4-model CPU comparison committed

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
