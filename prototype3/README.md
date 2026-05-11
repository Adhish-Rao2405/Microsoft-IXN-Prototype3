Prototype 3 extends the safety-validated Prototype 2 architecture into a comparative evaluation framework for local LLM/SLM planning. It introduces a fixed 30-command benchmark for a healthcare-inspired constrained manipulation scenario, an uncertainty detection layer, semantic scoring, model abstraction, and per-run metrics logging. The goal is to evaluate planning reliability, ambiguity handling, and latency/resource trade-offs without changing the deterministic safety guarantees established in Prototype 2.

## Dissertation Evidence Documentation

Prototype 3 is documented as the benchmark and local model-evaluation layer of the UCL Microsoft IXN Foundry Local dissertation.

Additional dissertation-facing documentation is available in:

* `docs/dissertation_evidence/prototype3_system_context.md`
* `docs/dissertation_evidence/prototype3_io_contract.md`
* `docs/dissertation_evidence/prototype3_benchmark_design.md`
* `docs/dissertation_evidence/prototype3_evaluation_pipeline.md`
* `docs/dissertation_evidence/prototype3_metric_taxonomy.md`
* `docs/dissertation_evidence/prototype3_research_questions_and_claims.md`
* `docs/dissertation_evidence/prototype3_claim_boundary.md`
* `docs/dissertation_evidence/prototype3_validity_and_reproducibility.md`
* `docs/dissertation_evidence/prototype3_transition_from_prototype2.md`
* `docs/dissertation_evidence/prototype3_transition_to_prototype4_and_5.md`
* `docs/dissertation_evidence/prototype3_runtime_verification_template.md`

Prototype 3 should be interpreted as a controlled benchmark and local model-evaluation prototype. It evaluates how local Foundry-served models behave under a fixed 30-command benchmark and separates request success, parse success, JSON validity, schema validity, semantic validity, safety validity and execution eligibility. It does not claim production robot safety, physical deployment, local-vs-cloud comparison, quantisation performance, live resource profiling or broad statistical generalisation.

## Prototype Sequence Context

This repository represents Prototype 3 in a five-prototype dissertation sequence:

1. Prototype 1 — baseline constrained LLM-to-robot task-planning proof-of-concept in PyBullet.
2. Prototype 2 / 2.1 — deterministic safety validation and reproducible evaluation framework.
3. Prototype 3 — benchmark and local model evaluation.
4. Prototype 4 — execution-grounded safety evidence and safety-latency frontier.
5. Prototype 5 — final evidence orchestration and brief closure.
