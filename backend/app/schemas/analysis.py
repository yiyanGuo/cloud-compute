from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AnalysisRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    message: str
    started_at: datetime
    finished_at: datetime | None
