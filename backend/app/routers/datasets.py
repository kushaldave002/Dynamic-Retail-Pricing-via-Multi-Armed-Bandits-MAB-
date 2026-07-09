from fastapi import APIRouter

from app.services.data_service import load_dataset_catalog


router = APIRouter(tags=["datasets"])


@router.get("/datasets")
def list_datasets() -> dict[str, object]:
    return load_dataset_catalog()
