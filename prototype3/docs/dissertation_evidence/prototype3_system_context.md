# Prototype 3 — Benchmark and Local Model Evaluation Layer

## Purpose

Prototype 3 is the structured benchmark and local model-evaluation layer of the dissertation. It builds on Prototype 2's validation architecture and evaluates how local Foundry-served models behave across a controlled 30-command benchmark.

Prototype 3 is not the final execution system and not a production robot controller. Its role is to make model behaviour measurable, comparable and traceable.

## Research Role

Prototype 3 converts the project from an architecture demonstration into a controlled evaluation pipeline. It records how model outputs move through request handling, parsing, JSON validation, action-schema validation, semantic checking where available, safety validation and execution-eligibility assessment.

## Relationship to Prototype 2

Prototype 2 introduced deterministic validation and fail-closed safety behaviour. Prototype 3 uses that logic to evaluate model behaviour across a fixed benchmark, preserving the distinction between a model returning text and a model producing a valid, safety-checkable task-planning action.

## Relationship to Prototype 4 and 5

Prototype 3 outputs are consumed by later evidence layers:

- Prototype 4 uses Prototype 3 evidence for execution-grounded safety and safety-latency analysis.
- Prototype 5 consumes Prototype 3 evidence in the final evidence orchestrator and brief-closure layer.

## Core Question

How reliably do local Foundry-served models produce parseable, JSON-valid, schema-compatible and safety-checkable task-planning outputs under a controlled benchmark?

## Dissertation Contribution

Prototype 3's contribution is the benchmark and metric separation, not production deployment. It provides evidence that local model behaviour can be made measurable through a fixed command set and a staged validation pipeline.

## Limitations

- 30-command benchmark only.
- Local model benchmark scope.
- No physical robot execution claim.
- No local-vs-cloud comparison.
- No quantisation study.
- No live resource profiling.
- No statistical population-level inference.
