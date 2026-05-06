# Evaluation Plan (Baseline)

## Objective
Evaluate local planner outputs against fixed benchmark intents while preserving deterministic validation and rejection-before-execution behavior.

## Baseline Evaluation Stages
1. Read benchmark command and metadata.
2. Generate plan via planner adapter.
3. Parse JSON output.
4. Validate action schema contract.
5. Apply downstream safety/semantic/uncertainty checks according to benchmark intent labels and allowed behavior.

## Acceptance Framing
A plan is only execution-eligible after contract checks pass. Invalid outputs are treated as rejection outcomes.

## Determinism
Planner request settings are fixed for stable comparison:
- temperature 0.0
- max_tokens 256

Evidence:
- src/brain/foundry_planner.py
- datasets/benchmark_v1.json
- src/schema/action_schema.py
