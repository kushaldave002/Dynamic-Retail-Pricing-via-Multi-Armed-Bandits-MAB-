from fastapi import APIRouter, HTTPException

from app.schemas.experiments import SimulationRequest, SimulationResponse
from app.services.data_service import load_precomputed_results
from app.services.experiment_service import run_requested_experiment


router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("/precomputed")
def get_precomputed_results() -> dict[str, object]:
    return load_precomputed_results()


@router.post("/run", response_model=SimulationResponse)
def run_experiment(request: SimulationRequest) -> SimulationResponse:
    try:
        payload = run_requested_experiment(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return SimulationResponse.model_validate(payload)
