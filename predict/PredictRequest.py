from pydantic import BaseModel


class PredictRequest(BaseModel):
    symbol: str
    n_days: int
