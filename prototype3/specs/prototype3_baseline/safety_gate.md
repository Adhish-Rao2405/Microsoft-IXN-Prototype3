# Safety Gate Baseline

## Current Safety/Evaluation Intent
Prototype 3 baseline preserves rejection-before-execution behavior: outputs that violate contract checks are rejected before execution success can be recorded.

## Schema Gate As First Hard Barrier
Action schema validation is the first explicit contract gate and must pass before a plan can be treated as executable behavior.

Evidence:
- src/schema/action_schema.py (strict validation rules)
- tests/test_benchmark_loader.py::test_benchmark_gold_intents_match_action_schema_contract
- datasets/benchmark_v1.json allowed_behavior values (execute_if_schema_and_safety_valid and reject_* patterns)

## Safety-aware Benchmark Framing
Benchmark metadata encodes safety-aware allowed behavior and uncertainty-aware rejection expectations.

Evidence:
- datasets/benchmark_v1.json fields: allowed_behavior, uncertainty_expected, gold_label

## Baseline Guardrail
This specification layer documents existing fail-closed behavior and prevents accidental drift to execute-on-invalid outputs.
