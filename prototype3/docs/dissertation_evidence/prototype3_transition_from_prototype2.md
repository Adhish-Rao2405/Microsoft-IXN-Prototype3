# Transition from Prototype 2 to Prototype 3

## What Prototype 2 Established

- Deterministic schema validation.
- Safety gate.
- Adversarial fail-closed testing.
- Evidence pack generation.
- Deterministic planner and model planner separation.

## Remaining Gap After Prototype 2

Prototype 2 showed the validation architecture but did not fully characterise local model behaviour across a fixed command benchmark. It established how outputs could be constrained, but the dissertation still needed a controlled way to measure how local models behave under repeated benchmark conditions.

## Prototype 3 Response

Prototype 3 introduces a 30-command benchmark and records structured model-behaviour metrics. It evaluates request success, parse success, JSON validity, schema/action validity, safety outcomes, semantic validity where available and execution eligibility where available.

## Dissertation Interpretation

Prototype 2 made model output constrainable. Prototype 3 made model behaviour measurable.
