# Prototype 3 Summary

## 1. Purpose

Prototype 3 is the benchmark and local model-evaluation layer for zero-trust robotic task planning with local SLMs. It evaluates whether Foundry-served local models can produce structured, schema-compatible and safety-checkable task-planning outputs under a fixed benchmark.

The prototype deliberately separates model output quality from execution permission. A model can return a plausible or schema-valid command while still being rejected by the downstream validation pipeline.

## 2. Role in the Dissertation Sequence

Prototype 3 extends the deterministic safety foundation from Prototype 2 into an empirical evaluation layer. It does not replace the safety gate; it measures how local models behave before and around that gate.

In the five-prototype sequence:

1. Prototype 1 established the constrained LLM-to-robot planning proof of concept.
2. Prototype 2 and 2.1 introduced deterministic validation and reproducible evaluation controls.
3. Prototype 3 adds a fixed benchmark, local model abstraction, metrics logging and model comparison.
4. Prototype 4 adds execution-grounded safety and safety-latency evidence.
5. Prototype 5 consolidates the evidence and adds final orchestration, local-vs-cloud comparison and resource profiling.

## 3. Research Questions RQ1-RQ5

Prototype 3 supports five local evaluation questions:

| RQ | Question | Prototype 3 evidence |
|---|---|---|
| RQ1 | Can the model return a response for each benchmark command? | Per-command request and raw-output logs |
| RQ2 | Can the response be parsed into JSON/action content? | Parse and JSON validity metrics |
| RQ3 | Does the output satisfy the action schema and semantic constraints? | Schema validity and semantic scoring metrics |
| RQ4 | Does the safety pipeline prevent unsafe or ambiguous commands from reaching execution eligibility? | False accept, false reject, correct reject and execution eligibility metrics |
| RQ5 | How do local Qwen 2.5 CPU models compare under the same benchmark? | Four-model comparison over the same 30-command dataset |

## 4. Benchmark Design

The benchmark contains 30 commands for a constrained healthcare-inspired manipulation scenario. The command set is fixed so that model outputs can be compared under repeatable conditions.

The benchmark includes clear, moderately ambiguous and highly ambiguous commands where dataset labels are available. This supports analysis of whether a model merely emits valid-looking JSON or correctly avoids execution for underspecified requests.

## 5. Metric Taxonomy

Prototype 3 avoids a single "accuracy" score. It reports staged validity metrics:

| Metric | Meaning |
|---|---|
| request_success | The model/API returned a response |
| parse_success | Action-like content could be recovered |
| json_valid | The response was syntactically valid JSON |
| schema_valid | The action matched the formal action schema |
| semantic_validity | The action matched the intended benchmark meaning where evaluated |
| safety_result | The deterministic safety gate result |
| execution_validity | The action was eligible to proceed under prototype constraints |

The key interpretation is that schema validity is not equivalent to execution eligibility, and execution eligibility is not a production-safety claim.

## 6. Evaluation Pipeline

Each benchmark command passes through the same staged pipeline:

1. Load benchmark command.
2. Build the planner prompt.
3. Query the local Foundry model.
4. Capture the raw response.
5. Attempt parse/recovery.
6. Validate JSON syntax.
7. Validate the formal action schema.
8. Apply semantic scoring where available.
9. Apply the deterministic safety gate.
10. Record execution eligibility.
11. Write per-command results.
12. Generate summary evidence.

This pipeline implements a zero-trust evaluation pattern: model outputs are treated as untrusted until they pass each downstream check.

## 7. Key Results

Baseline model: `foundry:qwen2.5-coder-0.5b:cpu`.

| Result | Value |
|---|---:|
| Benchmark size | 30 commands |
| Schema-valid outputs | 25/30 |
| Execution-eligible outputs | 4/30 |
| Model-level false accepts | 12/30 |
| Pipeline false accepts | 0/30 |

The baseline result shows that a high schema-validity rate did not translate into broad execution eligibility. The deterministic pipeline prevented model-level false accepts from becoming pipeline false accepts.

For RQ5, four Qwen 2.5 CPU models were compared:

| Model | Schema-valid outputs | Execution-eligible outputs | Model-level false accepts |
|---|---:|---:|---:|
| `foundry:qwen2.5-0.5b:cpu` | 14/30 | 2/30 | 8/30 |
| `foundry:qwen2.5-1.5b:cpu` | 23/30 | 3/30 | 10/30 |
| `foundry:qwen2.5-coder-0.5b:cpu` | 25/30 | 4/30 | 12/30 |
| `foundry:qwen2.5-coder-1.5b:cpu` | 28/30 | 5/30 | 15/30 |

Coder models improved schema validity, but higher schema validity did not imply proportional execution eligibility. The pipeline false accept rate remained 0% across all four tested models.

## 8. Evidence Artefacts

Primary evidence files:

- `datasets/benchmark_v1.json`
- `results/runs/phase_3_10_evidence_foundry_alias_cpu_clean.jsonl`
- `results/runs/rq5_comparison.jsonl`
- `results/summaries/foundry_evidence/evidence_pack.json`
- `results/summaries/rq5_comparison.csv`
- `results/summaries/rq5_comparison_evidence/evidence_pack.json`

Supporting documentation:

- `docs/dissertation_evidence/prototype3_benchmark_design.md`
- `docs/dissertation_evidence/prototype3_evaluation_pipeline.md`
- `docs/dissertation_evidence/prototype3_metric_taxonomy.md`
- `docs/dissertation_evidence/prototype3_research_questions_and_claims.md`
- `docs/dissertation_evidence/prototype3_claim_boundary.md`
- `docs/dissertation_evidence/prototype3_validity_and_reproducibility.md`

## 9. How to Reproduce / Run Tests

Run the test suite:

```powershell
pytest
```

Run the benchmark entry point:

```powershell
python -m src.eval.run_benchmark
```

Generate or inspect summary evidence from existing runs:

```powershell
python -m src.eval.evidence
```

Exact reproducibility depends on preserving the benchmark file, model alias, prompt configuration, Foundry Local model availability and output paths.

## 10. Claim Boundaries

Prototype 3 supports controlled engineering claims about local model output validity under a fixed benchmark. It does not claim:

- production robot safety;
- physical robot execution success;
- broad statistical generalisation;
- live resource profiling;
- quantisation conclusions;
- local-vs-cloud comparison.

The strongest dissertation-safe claim is that Prototype 3 demonstrates a reproducible benchmark and evaluation pipeline that prevents schema-valid but unsafe or ambiguous model outputs from being treated as execution-ready.

## 11. Link to Prototype 4 and 5

Prototype 3 produces model-output evidence and validity metrics. Prototype 4 consumes this style of evidence and adds execution-grounded safety, including safety-latency analysis. Prototype 5 then consolidates Prototype 3 and Prototype 4 evidence into the final orchestration layer, adding broader comparison and resource evidence where those claims are explicitly supported.
