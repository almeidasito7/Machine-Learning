from app.services.explainability import generate_insights

def test_generate_insights():
    result = generate_insights({
        "risk_score": 0.9,
        "failure_probability": 0.9
    })

    assert isinstance(result, list)
    assert len(result) > 0
