from predict import PredictRequest


class PredictResponse(PredictRequest):
    success: bool
    forecast: dict
    message: str
