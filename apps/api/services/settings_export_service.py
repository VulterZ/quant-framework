from __future__ import annotations

from apps.api.services import model_provider_service as models
from apps.api.services import search_provider_service as search


def export_settings() -> dict:
    model_settings = models.read_settings()
    search_settings = search.read_settings()
    return {
        "version": 1,
        "models": {
            "active_id": model_settings["active_id"],
            "profiles": [
                {k: v for k, v in profile.items() if k != "api_key"}
                | {"has_api_key": bool(profile.get("api_key"))}
                for profile in model_settings["profiles"]
            ],
        },
        "search": {
            **{k: v for k, v in search_settings.items() if k != "brave_api_key"},
            "has_brave_api_key": bool(search_settings.get("brave_api_key")),
        },
    }