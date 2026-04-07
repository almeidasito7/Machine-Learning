from fastapi import APIRouter, HTTPException

from app.core.logging import get_logger
from app.schemas.requests import AnalyzeRequest, TrainRequest
from app.schemas.responses import AnalyzeResponse
from app.services.pipeline.inference_pipeline import inference_pipeline
from app.services.pipeline.train_pipeline import train_pipeline

logger = get_logger(__name__)

router = APIRouter()


@router.post("/train")
def train(request: TrainRequest):
    try:
        result = train_pipeline(
            retrain_model=request.retrain_model,
        )
        return {
            "status": "success",
            "data": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.error("Training error", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal training error")


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    try:
        result = inference_pipeline(
            generate_narrative_flag=request.generate_narrative,
            dataset_type=request.dataset_type,
            max_structures=request.max_structures,
            include_raw_data=request.include_raw_data,
        )
        return AnalyzeResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.error("Inference error", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal inference error")