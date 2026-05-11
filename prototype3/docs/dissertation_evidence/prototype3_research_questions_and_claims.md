# Prototype 3 Research Questions and Claims

## Main Research Question

How reliably do local Foundry-served models produce structured, schema-compatible and safety-checkable robot task-planning outputs under a controlled command benchmark?

## Sub-Questions

1. Does the model return a response for each command?
2. Can the response be parsed or recovered?
3. Is the response valid JSON?
4. Does the action conform to the schema?
5. Does the action pass deterministic safety checks?
6. How do different local models compare under the same benchmark?
7. How do ambiguity levels affect response validity where categories are available?

## Evaluation Criteria

- Request success rate.
- Parse success rate.
- JSON-valid rate.
- Schema/action-valid rate.
- Safety pass/reject behaviour.
- Latency where measured.
- Per-command failure modes.

## Claims Supported

- Local model behaviour can be evaluated under fixed benchmark conditions.
- Validity must be separated into multiple metrics.
- Model response success alone is insufficient.
- Prototype 3 evidence can feed later safety and orchestration layers.

## Claims Not Supported

- Production safety.
- Physical robot execution.
- Local-vs-cloud comparison.
- Quantisation conclusions.
- Live resource utilisation.
- Statistically general natural-language understanding.
