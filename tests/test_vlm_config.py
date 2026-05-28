from view_aware_graph.vlm import graph_output_path, load_vlm_settings, raw_response_path


def test_load_vlm_settings_uses_config_defaults() -> None:
    settings = load_vlm_settings(
        environ={
            "VLM_PROVIDER": "",
            "VLM_MODEL": "",
            "VLM_ENDPOINT": "",
            "VLM_TIMEOUT_SECONDS": "",
            "VLM_API_KEY": "",
        }
    )

    assert settings.provider == ""
    assert settings.model == ""
    assert settings.endpoint == "http://127.0.0.1:11434/api/generate"
    assert settings.temperature == 0.0
    assert settings.max_retries == 2
    assert settings.timeout_seconds == 600.0
    assert settings.api_key is None
    assert settings.raw_response_dir.as_posix() == "data/interim/vlm_raw"
    assert settings.graph_output_dir.as_posix() == "data/processed/view_graphs"


def test_load_vlm_settings_allows_environment_overrides() -> None:
    settings = load_vlm_settings(
        environ={
            "VLM_PROVIDER": "ollama",
            "VLM_MODEL": "qwen2.5vl:7b",
            "VLM_ENDPOINT": "http://localhost:11434/api/generate",
            "VLM_TIMEOUT_SECONDS": "1800",
            "VLM_API_KEY": "local-secret",
        }
    )

    assert settings.provider == "ollama"
    assert settings.model == "qwen2.5vl:7b"
    assert settings.endpoint == "http://localhost:11434/api/generate"
    assert settings.timeout_seconds == 1800.0
    assert settings.api_key == "local-secret"


def test_vlm_output_paths_use_ignored_directories() -> None:
    settings = load_vlm_settings(environ={})

    assert raw_response_path(settings, "gt_v3").as_posix() == (
        "data/interim/vlm_raw/gt_v3_raw.json"
    )
    assert graph_output_path(settings, "gt_v3").as_posix() == (
        "data/processed/view_graphs/gt_v3.json"
    )
