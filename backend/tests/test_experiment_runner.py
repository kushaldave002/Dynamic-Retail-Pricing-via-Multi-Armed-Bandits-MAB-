from pathlib import Path

from experiments.run_experiment import build_precomputed_results, write_results


def test_build_precomputed_results_contains_overview_and_lab_defaults():
    payload = build_precomputed_results(seed=5, horizon=25)

    assert "overview" in payload
    assert "lab_defaults" in payload
    assert payload["overview"]["summaries"]
    assert payload["overview"]["traces"]


def test_write_results_creates_json():
    output = Path(".tmp") / "precomputed_results.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    try:
        write_results(output, {"overview": {"summaries": [], "traces": []}})
        assert output.exists()
    finally:
        if output.exists():
            output.unlink()
