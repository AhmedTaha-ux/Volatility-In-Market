from fit import FitRequest


class FitResponse(FitRequest):
    success: bool
    message: str
