def test_analyze(client, monkeypatch):
    def mock_inference_pipeline(*args, **kwargs):
        return {
            "structures": [
                {
                    "structure_id": 1,
                    "records": 10,
                    "avg_risk_score": 0.75,
                    "failure_probability": 0.6,
                    "risk_level": "high",
                }
            ],
            "total_structures": 1,
            "high_risk_count": 0,
            "medium_risk_count": 1,
            "low_risk_count": 0,
        }

    monkeypatch.setattr("app.api.routes.inference_pipeline", mock_inference_pipeline)

    response = client.post("/analyze", json={})

    assert response.status_code == 200
    body = response.json()
    assert "structures" in body
    assert body["total_structures"] == 1


def test_train(client, monkeypatch):
    def mock_train_pipeline(*args, **kwargs):
        return {
            "status": "models trained",
            "feature_count": 10,
        }

    monkeypatch.setattr("app.api.routes.train_pipeline", mock_train_pipeline)

    response = client.post("/train", json={})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert "data" in body


def test_analyze_should_return_500_when_pipeline_fails(client, monkeypatch):
    def mock_inference_pipeline(*args, **kwargs):
        raise RuntimeError("pipeline failed")

    monkeypatch.setattr("app.api.routes.inference_pipeline", mock_inference_pipeline)

    response = client.post("/analyze", json={})

    assert response.status_code == 500


def test_train_should_return_500_when_pipeline_fails(client, monkeypatch):
    def mock_train_pipeline(*args, **kwargs):
        raise RuntimeError("training failed")

    monkeypatch.setattr("app.api.routes.train_pipeline", mock_train_pipeline)

    response = client.post("/train", json={})

    assert response.status_code == 500


def test_analyze_should_return_400_on_value_error(client, monkeypatch):
    def mock_inference_pipeline(*args, **kwargs):
        raise ValueError("bad input")

    monkeypatch.setattr("app.api.routes.inference_pipeline", mock_inference_pipeline)

    response = client.post("/analyze", json={})

    assert response.status_code == 400


def test_analyze_should_return_404_on_file_not_found(client, monkeypatch):
    def mock_inference_pipeline(*args, **kwargs):
        raise FileNotFoundError("missing")

    monkeypatch.setattr("app.api.routes.inference_pipeline", mock_inference_pipeline)

    response = client.post("/analyze", json={})

    assert response.status_code == 404
