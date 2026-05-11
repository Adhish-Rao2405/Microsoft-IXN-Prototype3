# Prototype 3 Input/Output Contract

## Prototype Name

Prototype 3 — Benchmark and Local Model Evaluation Layer

## Prototype Type

Benchmark/evaluation prototype.

## Primary Purpose

To evaluate local model behaviour using a fixed benchmark and produce structured evidence for later dissertation analysis.

## Input Contract

| Input | Description | Used by |
|---|---|---|
| Benchmark dataset | Fixed 30-command task set | Benchmark runner |
| Command category | Clear, moderately ambiguous or highly ambiguous command group where available | Evaluation analysis |
| Local model alias | Foundry Local model identifier | Planner/model client |
| Prompt template/system prompt | Instruction format given to the model | Planner |
| Foundry Local endpoint/base URL | Local inference endpoint | Model client |
| Parser/recovery logic | Extracts JSON/action content from model response | Evaluation pipeline |
| Action schema | Defines permitted action format | Schema validator |
| Safety validator | Applies deterministic safety checks | Safety evaluation |
| Run configuration | Temperature, token limit, model alias and output paths | Reproducibility |

## Output Contract

| Output | Description | Downstream relevance |
|---|---|---|
| Raw model response | Text returned by local model | Used for parse/JSON analysis |
| Parsed action candidate | Extracted JSON/action object where possible | Used for validation |
| Request success metric | Whether model returned a response | Separates API success from validity |
| Parse success metric | Whether action content was recoverable | Separates recovery from JSON validity |
| JSON-valid metric | Whether output was syntactically valid JSON | Measures structured-output reliability |
| Schema/action validity | Whether action fits the formal schema | Measures interface compliance |
| Safety result | Deterministic safety-gate outcome | Measures safe/unsafe pass behaviour |
| Summary CSV/JSON | Aggregated run metrics | Used in dissertation evidence |
| Per-command logs | Command-level outputs and failures | Supports traceability |
| Phase logs / RQ summaries | Research-question specific summaries | Feeds Prototype 4/5 |

## Non-Outputs

Prototype 3 does not produce:

- cloud baseline comparison;
- quantisation evidence;
- live Foundry process CPU/memory profile;
- final Prototype 5 evidence manifest;
- production hardware validation.
