# Planner Contract

## Planner Module
src/brain/foundry_planner.py

## External Role
FoundryPlanner adapts local Foundry chat completions into structured PlanResult objects for downstream evaluation.

## Output Contract Expectations
SYSTEM_PROMPT currently enforces:
- Raw JSON only
- No markdown fences
- No explanatory text
- Action names aligned with active schema actions
- No extra keys outside schema allowance

Prompt vocabulary includes:
- pick, place, moveee, opengripper, closegripper, describescene, reset

## Runtime Inputs
- model_alias: supported aliases currently include qwen2.5-coder-0.5b and qwen2.5-coder-7b
- device: default cpu
- scene_state included in user prompt context

## Runtime Outputs
PlanResult fields:
- success
- parsed_output
- raw_output
- error
- planning_latency_ms

## Error Mapping
Planner maps transport/response/parse failures to explicit error codes, including:
- unknown_model_error
- parse_error
- foundry_timeout
- foundry_connection_error
- foundry_response_error

## Determinism Controls
- temperature is fixed at 0.0
- max_tokens is fixed at 256

## moveee Note
The planner prompt exposes moveee because it is part of the active schema/safety contract. In the current benchmark corpus, most gold intents are represented with pick/place actions rather than moveee.
