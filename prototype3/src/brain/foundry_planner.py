from __future__ import annotations

from dataclasses import dataclass
import json
import socket
import time
from typing import Any, Protocol
from urllib import error as urlerror
from urllib import request as urlrequest


SYSTEM_PROMPT = (
    "You are a robot task planner. Convert commands to JSON actions only.\n"
    "Schema: {\"actions\":[{\"action\":\"pick\"|\"place\"|\"moveee\"|"
    "\"opengripper\"|\"closegripper\"|\"describe_scene\"|\"reset\","
    "\"parameters\":{}}]}\n"
    "Output valid JSON only. No explanation."
)


@dataclass
class PlanResult:
    success: bool
    parsed_output: object | None
    raw_output: str | None
    error: str | None
    planning_latency_ms: int


class FoundryClientProtocol(Protocol):
    def generate(
        self,
        *,
        model_alias: str,
        device: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        timeout_s: float,
    ) -> str:
        ...


class _HttpFoundryClient:
    def __init__(self, endpoint: str = "http://127.0.0.1:8080/v1/chat/completions") -> None:
        self._endpoint = endpoint

    def generate(
        self,
        *,
        model_alias: str,
        device: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        max_tokens: int,
        timeout_s: float,
    ) -> str:
        body = {
            "model": f"{model_alias}:{device}",
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        payload = json.dumps(body).encode("utf-8")
        req = urlrequest.Request(
            self._endpoint,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlrequest.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")

        parsed = json.loads(raw)
        choices = parsed.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ValueError("foundry_response_missing_choices")

        first = choices[0]
        if not isinstance(first, dict):
            raise ValueError("foundry_response_bad_choice")

        message = first.get("message")
        if not isinstance(message, dict):
            raise ValueError("foundry_response_bad_message")

        content = message.get("content")
        if not isinstance(content, str):
            raise ValueError("foundry_response_bad_content")

        return content


class FoundryPlanner:
    SUPPORTED_ALIASES = {
        "qwen2.5-coder-0.5b",
        "qwen2.5-coder-7b",
    }

    def __init__(
        self,
        model_alias: str,
        device: str = "cpu",
        client: FoundryClientProtocol | None = None,
        timeout_s: float = 30.0,
    ) -> None:
        self.model_alias = model_alias
        self.device = device
        self.timeout_s = timeout_s
        self._client: FoundryClientProtocol = client or _HttpFoundryClient()

    def plan(self, command: str, scene_state: dict[str, Any] | None) -> PlanResult:
        start = time.perf_counter()
        if self.model_alias not in self.SUPPORTED_ALIASES:
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="unknown_model_error",
                planning_latency_ms=0,
            )

        user_prompt = f"Command: {command}\nScene: {scene_state or {}}"

        try:
            raw_text = self._client.generate(
                model_alias=self.model_alias,
                device=self.device,
                system_prompt=SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.0,
                max_tokens=256,
                timeout_s=self.timeout_s,
            )
            try:
                parsed = json.loads(raw_text)
                latency_ms = int((time.perf_counter() - start) * 1000)
                return PlanResult(
                    success=True,
                    parsed_output=parsed,
                    raw_output=raw_text,
                    error=None,
                    planning_latency_ms=latency_ms,
                )
            except json.JSONDecodeError:
                latency_ms = int((time.perf_counter() - start) * 1000)
                return PlanResult(
                    success=False,
                    parsed_output=None,
                    raw_output=raw_text,
                    error="parse_error",
                    planning_latency_ms=latency_ms,
                )
        except TimeoutError:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="foundry_timeout",
                planning_latency_ms=latency_ms,
            )
        except socket.timeout:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="foundry_timeout",
                planning_latency_ms=latency_ms,
            )
        except urlerror.URLError:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="foundry_connection_error",
                planning_latency_ms=latency_ms,
            )
        except ConnectionError:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="foundry_connection_error",
                planning_latency_ms=latency_ms,
            )
        except ValueError:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="foundry_response_error",
                planning_latency_ms=latency_ms,
            )
        except Exception:
            latency_ms = int((time.perf_counter() - start) * 1000)
            return PlanResult(
                success=False,
                parsed_output=None,
                raw_output=None,
                error="foundry_response_error",
                planning_latency_ms=latency_ms,
            )