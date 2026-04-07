import sys
import types

from app.services.openai_service import generate_narrative


def test_should_return_template_when_api_key_is_not_configured(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.openai_api_key", None)

    result = generate_narrative(
        {
            "total_structures": 3,
            "high_risk": 1,
            "medium_risk": 1,
            "low_risk": 1,
            "avg_risk_score": 0.42,
        }
    )

    assert isinstance(result, str)
    assert "Analysis completed" in result


def test_should_return_llm_response_when_openai_call_succeeds(monkeypatch):
    class FakeResponse:
        def __init__(self):
            self.choices = [
                types.SimpleNamespace(
                    message=types.SimpleNamespace(content="Generated engineering narrative.")
                )
            ]

    class FakeCompletions:
        def create(self, **kwargs):
            return FakeResponse()

    class FakeChat:
        def __init__(self):
            self.completions = FakeCompletions()

    class FakeOpenAI:
        def __init__(self, api_key):
            self.chat = FakeChat()

    fake_module = types.SimpleNamespace(OpenAI=FakeOpenAI)

    monkeypatch.setitem(sys.modules, "openai", fake_module)
    monkeypatch.setattr("app.core.config.settings.openai_api_key", "sk-test-valid")
    monkeypatch.setattr("app.core.config.settings.openai_model", "gpt-4o-mini")

    result = generate_narrative(
        {
            "total_structures": 2,
            "high_risk": 1,
            "medium_risk": 1,
            "low_risk": 0,
            "avg_risk_score": 0.66,
            "avg_failure_probability": 0.44,
            "top_structures": [
                {
                    "structure_id": 1,
                    "avg_risk_score": 0.9,
                    "failure_probability": 0.8,
                    "risk_level": "high",
                }
            ],
        }
    )

    assert result == "Generated engineering narrative."


def test_should_fallback_to_template_when_openai_call_fails(monkeypatch):
    class FakeCompletions:
        def create(self, **kwargs):
            raise RuntimeError("OpenAI failure")

    class FakeChat:
        def __init__(self):
            self.completions = FakeCompletions()

    class FakeOpenAI:
        def __init__(self, api_key):
            self.chat = FakeChat()

    fake_module = types.SimpleNamespace(OpenAI=FakeOpenAI)

    monkeypatch.setitem(sys.modules, "openai", fake_module)
    monkeypatch.setattr("app.core.config.settings.openai_api_key", "sk-test-valid")
    monkeypatch.setattr("app.core.config.settings.openai_model", "gpt-4o-mini")

    result = generate_narrative(
        {
            "total_structures": 1,
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 1,
            "avg_risk_score": 0.12,
        }
    )

    assert isinstance(result, str)
    assert "Analysis completed" in result
