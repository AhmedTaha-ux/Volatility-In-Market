from pydantic import BaseModel


class FitRequest(BaseModel):
    symbol: str
    use_new_data: bool
    n_observations: int
    p: int
    q: int
