# Baseline Requirements

## R1. Fixed Benchmark Corpus
The system must evaluate against the fixed 30-command benchmark corpus with unique IDs and required fields.

Evidence:
- datasets/benchmark_v1.json
- tests/test_benchmark_loader.py::test_load_benchmark_success
- tests/test_benchmark_loader.py::test_load_benchmark_invalid_count
- tests/test_benchmark_loader.py::test_load_benchmark_duplicate_id

## R2. Gold Intent Contract Validity
Every benchmark gold_intent must satisfy the active action schema.

Evidence:
- tests/test_benchmark_loader.py::test_benchmark_gold_intents_match_action_schema_contract
- src/schema/action_schema.py::validate_action_plan

## R3. Planner Output Must Be Structured JSON
Planner output is expected as raw JSON and should conform to the active action schema contract used by validation.

Evidence:
- src/brain/foundry_planner.py::SYSTEM_PROMPT
- src/schema/action_schema.py

## R4. Rejection Before Execution
Invalid plans are rejected by contract checks before any execution success can be recorded in evaluation.

Evidence:
- README.md baseline statement about deterministic safety guarantees
- src/schema/action_schema.py (hard validity result)
- datasets/benchmark_v1.json field: allowed_behavior (execute_if_schema_and_safety_valid or reject_*)

## R5. Controlled Dissertation Evolution
Specification docs describe implemented behavior only and are used to constrain future agent changes.
