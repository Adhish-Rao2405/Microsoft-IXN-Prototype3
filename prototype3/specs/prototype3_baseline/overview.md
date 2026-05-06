# Prototype 3 Baseline Overview

## Purpose
Prototype 3 provides a comparative evaluation framework for local LLM/SLM planning in a constrained healthcare-inspired manipulation scenario.

## Current Baseline Scope
- Fixed benchmark dataset with 30 commands and gold intents.
- Planner interface for Foundry-hosted local models.
- Strict action-schema validation as a hard contract.
- Safety-first rejection-before-execution evaluation flow.
- Benchmark loader tests that enforce dataset integrity and schema-valid gold intents.

## Evidence
- Architecture summary: README.md
- Action schema contract: src/schema/action_schema.py
- Planner contract and prompt constraints: src/brain/foundry_planner.py
- Benchmark definitions: datasets/benchmark_v1.json
- Baseline loader and contract checks: tests/test_benchmark_loader.py

## Non-goals In This Baseline Layer
- No runtime behavior changes.
- No schema expansion.
- No benchmark mutation.
- No refactor of planner/safety/evaluation code.
