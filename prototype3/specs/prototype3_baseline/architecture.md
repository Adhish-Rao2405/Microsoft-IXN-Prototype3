# Baseline Architecture

## Components
- Benchmark corpus: datasets/benchmark_v1.json
- Action schema validator: src/schema/action_schema.py
- Foundry planner adapter: src/brain/foundry_planner.py
- Benchmark integrity tests: tests/test_benchmark_loader.py

## Flow (Current Baseline)
1. Load benchmark items from the fixed dataset.
2. Obtain planner output for each command.
3. Parse planner output as JSON.
4. Validate output against the action schema contract.
5. Continue evaluation only when schema contract is satisfied.

## Contract Boundaries
- action_schema.py is the source of truth for allowed actions and keys.
- foundry_planner.py defines planner-facing output expectations.
- benchmark_v1.json defines evaluation tasks and gold intents; these gold intents are validated by validate_action_plan in tests.

## Design Principle
The baseline is fail-closed: contract violations are treated as rejection conditions, preserving rejection-before-execution behavior.
