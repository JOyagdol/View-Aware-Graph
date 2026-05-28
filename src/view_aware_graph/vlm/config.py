"""Configuration loading for VLM runs."""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from view_aware_graph.vlm.types import RetryPolicy


@dataclass(frozen=True)
class VLMSettings:
    """Resolved VLM and project path settings."""

    provider: str
    model: str
    endpoint: str
    temperature: float
    max_retries: int
    timeout_seconds: float
    api_key: str | None
    prompt_path: Path
    schema_path: Path
    raw_response_dir: Path
    graph_output_dir: Path

    @property
    def retry_policy(self) -> RetryPolicy:
        """Retry policy derived from settings."""

        return RetryPolicy(max_retries=self.max_retries)


def load_vlm_settings(
    config_path: str | Path = "configs/default.toml",
    environ: Mapping[str, str] | None = None,
) -> VLMSettings:
    """Load VLM settings from TOML config with environment overrides."""

    env = os.environ if environ is None else environ
    config = _load_toml(config_path)
    vlm_config = _mapping(config.get("vlm"), "vlm")
    paths_config = _mapping(config.get("paths"), "paths")

    provider = env.get("VLM_PROVIDER") or _string(vlm_config.get("provider"), "vlm.provider")
    model = env.get("VLM_MODEL") or _string(vlm_config.get("model"), "vlm.model")
    endpoint = env.get("VLM_ENDPOINT") or _string(vlm_config.get("endpoint"), "vlm.endpoint")
    api_key = env.get("VLM_API_KEY") or None
    env_timeout_seconds = _env_float(env, "VLM_TIMEOUT_SECONDS")
    timeout_seconds = (
        env_timeout_seconds
        if env_timeout_seconds is not None
        else _float(vlm_config.get("timeout_seconds", 120.0), "vlm.timeout_seconds")
    )

    return VLMSettings(
        provider=provider,
        model=model,
        endpoint=endpoint,
        temperature=_float(vlm_config.get("temperature"), "vlm.temperature"),
        max_retries=_int(vlm_config.get("max_retries"), "vlm.max_retries"),
        timeout_seconds=timeout_seconds,
        api_key=api_key,
        prompt_path=Path(_string(paths_config.get("prompt"), "paths.prompt")),
        schema_path=Path(_string(paths_config.get("schema"), "paths.schema")),
        raw_response_dir=Path(_string(paths_config.get("interim_data"), "paths.interim_data"))
        / "vlm_raw",
        graph_output_dir=Path(_string(paths_config.get("processed_data"), "paths.processed_data"))
        / "view_graphs",
    )


def raw_response_path(settings: VLMSettings, run_id: str) -> Path:
    """Return the ignored raw-response path for a run id."""

    return settings.raw_response_dir / f"{run_id}_raw.json"


def graph_output_path(settings: VLMSettings, run_id: str) -> Path:
    """Return the ignored graph-output path for a run id."""

    return settings.graph_output_dir / f"{run_id}.json"


def _load_toml(config_path: str | Path) -> Mapping[str, Any]:
    path = Path(config_path)
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    return cast(Mapping[str, Any], data)


def _mapping(value: Any, key: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return cast(Mapping[str, Any], value)
    raise ValueError(f"Config section [{key}] is required.")


def _string(value: Any, key: str) -> str:
    if isinstance(value, str):
        return value
    raise ValueError(f"Config value {key} must be a string.")


def _float(value: Any, key: str) -> float:
    if isinstance(value, int | float):
        return float(value)
    raise ValueError(f"Config value {key} must be a number.")


def _env_float(env: Mapping[str, str], key: str) -> float | None:
    value = env.get(key)
    if not value:
        return None
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"Environment value {key} must be a number.") from exc


def _int(value: Any, key: str) -> int:
    if isinstance(value, int):
        return value
    raise ValueError(f"Config value {key} must be an integer.")
