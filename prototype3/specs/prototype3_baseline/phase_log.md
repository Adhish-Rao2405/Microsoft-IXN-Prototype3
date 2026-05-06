# Phase Log (Baseline Spec Layer)

## Context
This folder records a manual Spec Kit-style baseline for Prototype 3 without introducing tooling changes or repository restructuring.

## Completed Phases (Checkpointed)
- Phase 3.4a: planner/schema contract alignment (commit 4eded0c)
- Phase 3.4b: deterministic rejection-before-execution gate (commit 8f7d0c5)
- Phase 3.4c: benchmark/schema alignment (commit adc922c)
- Phase 3.4d: baseline specification documents (commit c6e6218)
- Phase 3.4e: schema vocabulary audit and evaluation plan update (commit pending)
- Phase 3.5: semantic scoring implementation and spec alignment (commit pending)

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

## Current Phase
- Phase 3.5: complete — pending commit

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
