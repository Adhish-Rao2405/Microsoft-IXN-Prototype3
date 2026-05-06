# Phase Log (Baseline Spec Layer)

## Context
This folder records a manual Spec Kit-style baseline for Prototype 3 without introducing tooling changes or repository restructuring.

## Completed Phases (Checkpointed)
- Phase 3.4a: planner/schema contract alignment (commit 4eded0c)
- Phase 3.4b: deterministic rejection-before-execution gate (commit 8f7d0c5)
- Phase 3.4c: benchmark/schema alignment (commit adc922c)
- Phase 3.4d: baseline specification documents (commit c6e6218)

## Current Phase
- Phase 3.4: schema vocabulary audit and semantic scoring foundation

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
