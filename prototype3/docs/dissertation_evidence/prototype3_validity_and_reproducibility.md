# Prototype 3 Validity and Reproducibility

## Purpose

This document addresses reproducibility and validity boundaries for Prototype 3.

## Reproducibility Controls

- Fixed benchmark dataset.
- Explicit model alias.
- Fixed prompt/system prompt.
- Deterministic temperature where applicable.
- Recorded output files.
- Per-command logs.
- Summary CSV/JSON outputs.
- Git commit/phase logs.

## Internal Validity

The staged validation pipeline reduces ambiguity by recording exactly where a response fails. A response that reaches the model client is not automatically treated as parseable, JSON-valid, schema-valid, semantically valid, safe or executable.

## Construct Validity

The project avoids vague accuracy and instead measures separate constructs: response success, parseability, JSON validity, schema validity, safety result and execution eligibility. This makes the reported metrics closer to the engineering behaviours being evaluated.

## External Validity

The 30-command benchmark does not prove generalisation to all robot language commands. Results should be interpreted within the benchmark scope, local model configuration and validation pipeline used.

## Statistical Conclusion Validity

Prototype 3 should not claim broad statistical significance. It provides controlled engineering evidence. The benchmark size is useful for prototype comparison and traceability but is not a basis for population-level inference.

## Reproducibility Limitations

- Local model availability may vary.
- Foundry Local version may vary.
- Hardware affects latency.
- Model aliases can change.
- Prompts/configuration must be recorded.

## Dissertation-Safe Wording

Prototype 3 results should be interpreted as controlled benchmark evidence, not population-level statistical inference.
