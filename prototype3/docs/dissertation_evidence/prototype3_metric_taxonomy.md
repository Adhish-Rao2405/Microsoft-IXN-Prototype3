# Prototype 3 Metric Taxonomy

## Purpose

Prototype 3 avoids a single vague "accuracy" score.

## Metric Table

| Metric | Definition | What it does not prove |
|---|---|---|
| request_success | Model/API returned a response | Does not prove parseability or validity |
| parse_success | JSON/action content could be recovered | Does not prove syntactically valid JSON |
| json_valid | Response was syntactically valid JSON | Does not prove schema or task correctness |
| schema_valid | Action matched the formal schema | Does not prove semantic correctness or safety |
| semantic_validity | Action matched intended task meaning where evaluated | Does not prove physical safety |
| safety_result | Deterministic safety gate result | Does not prove semantic alignment |
| execution_validity | Action could proceed under prototype constraints | Does not prove production safety |

## Important Distinction

JSON validity is not task accuracy. Schema validity is not safety. Safety validity is not semantic correctness.

## Baseline Definition

Prototype 3 establishes local model baselines under the fixed benchmark. These baselines compare model behaviour within the same local evaluation setup and should not be interpreted as cloud comparisons. Later Prototype 5 introduces local-vs-cloud comparison.

## Dissertation-Safe Wording

Prototype 3 reports structured validity metrics rather than a single undifferentiated accuracy score.
