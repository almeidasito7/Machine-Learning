from typing import Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    generate_narrative: bool = Field(default=True)
    include_raw_data: bool = Field(default=False)
    max_structures: Optional[int] = Field(default=None, ge=1)
    dataset_type: str = Field(default="external")


class TrainRequest(BaseModel):
    retrain_model: bool = Field(default=True)
    save_model: bool = Field(default=True)