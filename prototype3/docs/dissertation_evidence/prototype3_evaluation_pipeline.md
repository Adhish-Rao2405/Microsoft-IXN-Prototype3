# Prototype 3 Evaluation Pipeline

## Purpose

Prototype 3 evaluates model outputs through a staged pipeline so that model response success is not confused with valid or safe task planning.

## Pipeline Stages

1. Load benchmark command.
2. Build prompt/system message.
3. Call local Foundry model.
4. Capture raw model response.
5. Attempt parse/recovery.
6. Check JSON validity.
7. Apply schema/action validation.
8. Apply semantic validity check where available.
9. Apply deterministic safety gate.
10. Record execution eligibility where available.
11. Write per-command results.
12. Generate summary metrics.

## Key Principle

A model response can pass an earlier stage and fail a later stage.

## Example Metric Progression

request_success
→ parse_success
→ json_valid
→ schema_valid
→ semantic_validity
→ safety_result
→ execution_validity

## Why This Matters

This directly addresses the supervisor concern that metrics and evaluation criteria needed to be explicit. The staged pipeline makes it clear whether a failure occurred at the model request layer, response parsing layer, JSON layer, schema layer, semantic layer, safety layer or execution-eligibility layer.

## Failure Handling

Failures are recorded as evidence, not hidden. Invalid JSON, schema failure or safety rejection are useful evaluation outcomes because they identify where local model output stops being usable under the prototype constraints.
