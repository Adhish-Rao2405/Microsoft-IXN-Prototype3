# Prototype 3 Benchmark Design

## Purpose

Prototype 3 uses a controlled benchmark to evaluate local model behaviour under repeatable conditions.

## Benchmark Scope

The benchmark contains 30 commands.

The benchmark is treated as a fixed 30-command evaluation set. Any category labels should be interpreted according to the dataset file. Where category labels are available, they may distinguish:

- clear commands;
- moderately ambiguous commands;
- highly ambiguous commands.

## Why 30 Commands

Thirty commands are sufficient for controlled prototype comparison and dissertation evidence generation, but not enough for broad statistical generalisation. The benchmark supports engineering evaluation within a defined scope rather than population-level claims about all natural-language robot commands.

## What the Benchmark Measures

- Response completion.
- Parseability.
- JSON validity.
- Schema/action validity.
- Safety-gate behaviour.
- Model differences where applicable.

## What the Benchmark Does Not Measure

- Physical execution success.
- Real robot safety.
- Broad natural-language generalisation.
- Production reliability.
- Cloud performance.
- Quantisation performance.
- Resource utilisation.

## Benchmark Reproducibility

The fixed dataset, model alias, prompt, run configuration and output files must be recorded for each run. Reproducibility depends on preserving the command set, model identifier, local serving configuration, parser behaviour and output paths used to generate the summary evidence.

## Dissertation-Safe Wording

Prototype 3 provides controlled benchmark evidence rather than population-level statistical proof.
