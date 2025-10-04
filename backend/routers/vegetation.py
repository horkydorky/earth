# backend/routers/vegetation.py
from fastapi import APIRouter, HTTPException
from ..services import ndvi_analysis
from ..models import schemas

router = APIRouter(
    prefix="/vegetation",
    tags=["Vegetation"]
)

@router.get("/{region}/{year}", response_model=schemas.DataResponse)
def get_vegetation_heatmap(region: str, year: int):
    """
    Generates and returns the URL for a vegetation (NDVI) heatmap
    for a given region and year.
    """
    try:
        # This is the line that triggers all your hard work!
        result_path = ndvi_analysis.process_vegetation_data_for_region(region=region, year=year)

        return schemas.DataResponse(
            topic="vegetation",
            region=region,
            year=year,
            data_url=result_path
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        # Catch any other unexpected errors from your service
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")