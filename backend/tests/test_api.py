from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_datasets_endpoint_returns_products():
    response = client.get("/datasets")

    assert response.status_code == 200
    assert response.json()["products"]


def test_precomputed_endpoint_returns_overview():
    response = client.get("/experiments/precomputed")

    assert response.status_code == 200
    assert "overview" in response.json()


def test_run_experiment_endpoint_returns_summary_and_traces():
    response = client.post(
        "/experiments/run",
        json={
            "environment": "elasticity",
            "horizon": 25,
            "seed": 9,
            "algorithms": ["epsilon_greedy", "ucb1"],
            "parameters": {"epsilon_greedy": {"epsilon": 0.1}},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]
    assert payload["traces"]


def test_run_experiment_response_has_consistent_chart_arrays():
    response = client.post(
        "/experiments/run",
        json={
            "environment": "empirical",
            "horizon": 10,
            "seed": 5,
            "algorithms": ["epsilon_greedy", "ucb1", "sliding_window_ucb"],
            "parameters": {},
        },
    )

    payload = response.json()
    assert response.status_code == 200
    assert len(payload["traces"]) == 30
    assert len(payload["summary"]) == 3
    assert {row["algorithm"] for row in payload["summary"]} == {
        "epsilon_greedy",
        "ucb1",
        "sliding_window_ucb",
    }


def test_cors_allows_local_frontend_origin():
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code in {200, 204}
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
