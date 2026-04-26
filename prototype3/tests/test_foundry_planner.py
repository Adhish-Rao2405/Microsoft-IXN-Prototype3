import json

from src.brain.foundry_planner import FoundryPlanner


class _GoodClient:
    def generate(self, **kwargs):
        del kwargs
        return json.dumps({"actions": [{"action": "pick", "object": "medicine_cup"}]})


class _NonJsonClient:
    def generate(self, **kwargs):
        del kwargs
        return "not-json-output"


class _ConnectionClient:
    def generate(self, **kwargs):
        del kwargs
        raise ConnectionError("cannot connect")


class _TimeoutClient:
    def generate(self, **kwargs):
        del kwargs
        raise TimeoutError("timed out")


class _SchemaInvalidButJsonClient:
    def generate(self, **kwargs):
        del kwargs
        return json.dumps({"actions": [{"action": "pick"}]})


def test_valid_json_response_is_parsed_correctly() -> None:
    planner = FoundryPlanner("qwen2.5-coder-0.5b", client=_GoodClient())
    result = planner.plan("Pick up the medicine cup", {})

    assert result.success is True
    assert result.error is None
    assert isinstance(result.parsed_output, dict)
    assert result.raw_output is not None


def test_non_json_response_returns_parse_error() -> None:
    planner = FoundryPlanner("qwen2.5-coder-0.5b", client=_NonJsonClient())
    result = planner.plan("Pick up the medicine cup", {})

    assert result.success is False
    assert result.error == "parse_error"


def test_connection_error_returns_foundry_connection_error() -> None:
    planner = FoundryPlanner("qwen2.5-coder-0.5b", client=_ConnectionClient())
    result = planner.plan("Pick up the medicine cup", {})

    assert result.success is False
    assert result.error == "foundry_connection_error"
    assert result.raw_output is None


def test_timeout_returns_foundry_timeout() -> None:
    planner = FoundryPlanner("qwen2.5-coder-0.5b", client=_TimeoutClient())
    result = planner.plan("Pick up the medicine cup", {})

    assert result.success is False
    assert result.error == "foundry_timeout"
    assert result.raw_output is None


def test_raw_output_is_preserved_on_parse_failure() -> None:
    planner = FoundryPlanner("qwen2.5-coder-0.5b", client=_NonJsonClient())
    result = planner.plan("Pick up the medicine cup", {})

    assert result.success is False
    assert result.error == "parse_error"
    assert result.raw_output == "not-json-output"


def test_foundry_planner_does_not_run_schema_validation_internally() -> None:
    planner = FoundryPlanner("qwen2.5-coder-0.5b", client=_SchemaInvalidButJsonClient())
    result = planner.plan("Pick up the medicine cup", {})

    assert result.success is True
    assert result.error is None
    assert result.parsed_output == {"actions": [{"action": "pick"}]}


def test_planner_returns_plan_result_compatible_object() -> None:
    planner = FoundryPlanner("qwen2.5-coder-0.5b", client=_GoodClient())
    result = planner.plan("Pick up the medicine cup", {})

    assert hasattr(result, "success")
    assert hasattr(result, "error")
    assert hasattr(result, "raw_output")
    assert hasattr(result, "parsed_output")
    assert hasattr(result, "planning_latency_ms")
    assert isinstance(result.planning_latency_ms, int)


def test_unknown_alias_returns_unknown_model_error() -> None:
    planner = FoundryPlanner("nonexistent-model", client=_GoodClient())
    result = planner.plan("Pick up the medicine cup", {})

    assert result.success is False
    assert result.error == "unknown_model_error"
