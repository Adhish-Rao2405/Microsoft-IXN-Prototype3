# Evaluation Plan (Baseline)

## Research-grade Framing
Prototype 3 is evaluated as a local-first, schema-constrained benchmarking framework where model outputs are treated as untrusted proposals until deterministic checks pass.

Master framing:
This dissertation develops and evaluates a local-first, schema-constrained robotic planning benchmark in which model outputs must pass deterministic validation, semantic scoring, and rejection-before-execution checks before being considered suitable for robotic execution.

## Local-first Definition
Local-first means inference is executed on local hardware under explicit resource constraints, without cloud inference dependency in the benchmark path.

## Baseline Evaluation Stages
1. Read benchmark command and metadata.
2. Generate plan via planner adapter.
3. Parse JSON output.
4. Validate action schema contract.
5. Apply safety validation.
6. Apply uncertainty and semantic scoring.
7. Mark rejection/eligibility outcomes.

## Core Evaluation Criteria
Outputs are judged on whether they are:
1. parseable
2. schema-valid
3. semantically correct
4. safe before execution
5. robust under ambiguity
6. reproducible across model and hardware constraints

## Revised RQ4
At what rates does deterministic rejection-before-execution correctly catch invalid/unsafe/semantically wrong plans (false accept rate), and at what rates does it over-reject otherwise valid plans (false reject rate)?

## Achieved vs Planned Contributions
Achieved:
- schema-constrained action contract
- planner output contract and deterministic planner settings
- rejection-before-execution gate behavior
- benchmark/schema alignment checks in loader tests

Planned:
- expanded semantic scoring evidence tables
- multi-model comparative runs
- final evidence pack for dissertation figures/tables

## Semantic Scoring Categories
See semantic scoring definitions in:
- specs/prototype3_baseline/semantic_scoring_rules.md

## Reproducibility Metadata Requirements
Each benchmark run should capture at minimum:
- run timestamp
- model alias and resolved model ID
- Foundry endpoint/base URL
- operating system/version
- Python version
- CPU model
- RAM size
- GPU/VRAM (if used)
- planner parameters (temperature, max_tokens, timeout)
- benchmark dataset version/path

## Phase Exit Criteria (Current Planning Baseline)
- Phase 3.4: schema vocabulary audit completed, including moveee finding and contract documentation.
- Phase 3.5: semantic scoring rules and acceptance/rejection categories documented and test-mapped.
- Phase 3.6: rejection metric definitions (false accept/false reject) operationalized in outputs.
- Phase 3.7: reproducibility metadata exported with benchmark runs.
- Phase 3.8: single-model benchmark run artifacts completed.
- Phase 3.9: multi-model comparison completed.
- Phase 3.10: dissertation evidence pack generated.

## Determinism Controls
Planner request settings are fixed for stable comparison:
- temperature 0.0
- max_tokens 256

Evidence:
- src/brain/foundry_planner.py
- src/schema/action_schema.py
- datasets/benchmark_v1.json
- tests/test_run_benchmark.py
