# Action Schema Contract

## Source Of Truth
src/schema/action_schema.py

## Top-level Forms
Accepted top-level forms:
- Dict with actions key: {"actions": [...]}
- Direct list of action objects

Rejected top-level forms include:
- Non-list/non-dict values
- Dict missing actions key
- Dict where actions is not a list

## Allowed Actions
- pick
- place
- moveee
- opengripper
- closegripper
- reset
- describescene

## Allowed Keys By Action
- pick: action, object
- place: action, target
- moveee: action, target, target_xyz
- opengripper: action, width
- closegripper: action, force
- reset: action
- describescene: action

## Per-action Constraints
- pick requires object as string.
- place requires target as string.
- moveee requires exactly one of target or target_xyz.
- moveee target_xyz must be a 3-number list.
- opengripper width is optional but must be numeric when present.
- closegripper force is optional but must be numeric when present.
- Unexpected keys are rejected.

## moveee Audit Conclusion (Phase 3.4)
- moveee is intentional in the current baseline.
- It is implemented in schema validation and safety validation.
- It is included in planner prompt vocabulary.
- It is exercised by schema/safety tests.
- It is not currently used by benchmark_v1.json gold_intents, which mostly use pick/place composition.

Interpretation:
- moveee is a supported low-level motion primitive.
- pick/place remains the dominant benchmark expression layer.
- No schema removal is performed in this phase.

## Validation Interface
validate_action_plan(parsed) returns SchemaValidationResult:
- valid: bool
- errors: list[str]
- normalized_actions: list[dict] | None
