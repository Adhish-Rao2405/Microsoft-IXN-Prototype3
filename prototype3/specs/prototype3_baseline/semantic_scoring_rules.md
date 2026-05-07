# Semantic Scoring Rules (Baseline)

## Purpose
Define consistent interpretation categories for semantic correctness, rejection behavior, and evaluation error analysis.

## Categories

### exact_match
Planned actions match benchmark gold intent exactly in action sequence and key arguments.

### acceptable_equivalent
Planned actions are not text-identical but satisfy the intended task outcome under allowed flexible behavior.

### schema_valid_but_semantically_wrong
Plan passes schema validation but fails task intent comparison.

### wrong_object
Plan references an object different from gold intent object requirements.

### wrong_target
Plan references a target/zone different from gold intent requirements.

### unnecessary_extra_action
Plan includes additional actions not required by the benchmark intent and not justified as acceptable equivalent behavior.

### false_accept
Pipeline marks a plan as execution-eligible when it should have been rejected (invalid, unsafe, semantically wrong, or uncertain per policy).

### false_reject
Pipeline rejects a plan that should have been considered execution-eligible under current benchmark label and policy.

### correct_reject
Pipeline rejects a plan that is correctly classified as invalid/unsafe/unsupported/uncertain.

### malformed_or_unparseable_output
Planner output cannot be parsed as valid JSON action payload.

### unsupported_action
Planner output uses an action outside the active schema vocabulary.

### missing_action
Fewer actions planned than the gold intent requires; one or more required steps are absent.

### wrong_action
Plan contains the correct number of actions but one or more action verbs differ from gold intent.

## Notes
- Schema-valid does not imply semantically correct.
- Rejection quality is evaluated with both false_accept and false_reject rates.
- Category mapping should be traceable to benchmark record fields and failure_mode/rejection_reasons outputs.
