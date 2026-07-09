import json
from pathlib import Path

from experiments.run_experiment import build_precomputed_results, write_results


_V1_ALGORITHMS = {
    "epsilon_greedy",
    "ucb1",
    "sliding_window_ucb",
    "thompson_sampling",
    "oracle",
}


def test_build_precomputed_results_contains_both_environments_and_v1_algorithms():
    payload = build_precomputed_results(seed=5, horizon=25)

    assert "overview" in payload
    assert "lab_defaults" in payload

    summaries = payload["overview"]["summaries"]
    traces = payload["overview"]["traces"]

    assert {row["environment"] for row in summaries} == {"empirical", "elasticity"}
    assert {row["environment"] for row in traces} == {"empirical", "elasticity"}

    for environment in ("empirical", "elasticity"):
        summary_algorithms = {row["algorithm"] for row in summaries if row["environment"] == environment}
        trace_algorithms = {row["algorithm"] for row in traces if row["environment"] == environment}
        assert summary_algorithms == _V1_ALGORITHMS
        assert trace_algorithms == _V1_ALGORITHMS


def test_write_results_creates_json(tmp_path: Path):
    output = tmp_path / "nested" / "precomputed_results.json"
    payload = {"overview": {"summaries": [{"algorithm": "oracle"}], "traces": []}}

    write_results(output, payload)

    assert output.exists()
    assert json.loads(output.read_text(encoding="utf-8")) == payload
