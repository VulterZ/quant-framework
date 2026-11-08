import json

from apps.api.services import model_provider_service as models
from apps.api.services import search_provider_service as search
from apps.api.services import settings_export_service as export

MODEL_KEY = "sk-test-MODEL-12345"
BRAVE_KEY = "brave-test-KEY-67890"


def _isolate(monkeypatch, tmp_path):
    """Point settings at a temp folder and clear env fallbacks."""
    monkeypatch.setenv("ALPHALAB_RUNTIME_DIR", str(tmp_path))
    for name in ("CONEXUS_MODEL_BASE_URL", "CONEXUS_MODEL_ID",
                 "CONEXUS_MODEL_API_KEY", "BRAVE_SEARCH_API_KEY"):
        monkeypatch.delenv(name, raising=False)


def _save_sample_settings():
    models.save_profile(
        {"id": "p1", "name": "My model", "base_url": "https://openrouter.ai/api/v1",
         "model": "some/model", "api_key": MODEL_KEY},
        activate=True,
    ) 
    search.save_settings({"provider": "brave", "brave_api_key": BRAVE_KEY})


def test_export_contains_no_api_keys(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    _save_sample_settings()

    text = json.dumps(export.export_settings())

    assert MODEL_KEY not in text
    assert BRAVE_KEY not in text
    assert "api_key\":" not in text.replace("has_api_key", "").replace("has_brave_api_key", "")


def test_export_records_which_keys_existed(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    _save_sample_settings()

    result = export.export_settings()

    assert result["models"]["active_id"] == "p1"
    assert result["models"]["profiles"][0]["has_api_key"] is True
    assert result["models"]["profiles"][0]["base_url"] == "https://openrouter.ai/api/v1"
    assert result["search"]["provider"] == "brave"
    assert result["search"]["has_brave_api_key"] is True


def test_export_does_not_change_saved_settings(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)
    _save_sample_settings()

    export.export_settings()

    assert models.read_settings()["profiles"][0]["api_key"] == MODEL_KEY
    assert search.read_settings()["brave_api_key"] == BRAVE_KEY


def test_export_with_no_saved_settings(monkeypatch, tmp_path):
    _isolate(monkeypatch, tmp_path)

    result = export.export_settings()

    assert result["models"]["profiles"] == []
    assert result["search"]["has_brave_api_key"] is False