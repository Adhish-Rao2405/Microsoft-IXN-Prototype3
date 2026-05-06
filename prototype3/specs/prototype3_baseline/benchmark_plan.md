# Benchmark Plan (Baseline)

## Dataset
Use the fixed benchmark dataset at datasets/benchmark_v1.json.

## Structure Constraints
- Exactly 30 benchmark items.
- Unique item IDs.
- Required fields per item (id, command, difficulty, category, gold_label, gold_intent, uncertainty_expected, allowed_behavior, semantic_pass_rule, notes).

Evidence:
- tests/test_benchmark_loader.py::test_load_benchmark_success
- tests/test_benchmark_loader.py::test_load_benchmark_invalid_count
- tests/test_benchmark_loader.py::test_load_benchmark_duplicate_id

## Gold Intent Verification
All gold_intent payloads are required to pass the active action schema validator.

Evidence:
- tests/test_benchmark_loader.py::test_benchmark_gold_intents_match_action_schema_contract
- src/schema/action_schema.py::validate_action_plan

## Execution Philosophy
Benchmarking is contract-first and rejection-aware: schema/safety/uncertainty expectations are represented in benchmark metadata and validated in the evaluation pipeline.
