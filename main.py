import sqlite3

from settings import DB_NAME
from SQLRepository import SQLRepository
from fastapi import FastAPI
from model import GarchModel
from pydantic import BaseModel


class FitInput(BaseModel):
    symbol: str
    use_new_data: bool
    n_observations: int
    p: int
    q: int


class FitOutput(FitInput):
    success: bool
    message: str


class PredictInput(BaseModel):
    symbol: str
    n_days: int


class PredictOut(PredictInput):
    success: bool
    forecast: dict
    message: str


app = FastAPI()


@app.get("/")
def hello():
    return {"Hello": "World"}


def build_model(symbol, use_new_data):
    connection = sqlite3.connect(database=DB_NAME, check_same_thread=False)

    repo = SQLRepository(connection=connection)

    model = GarchModel(symbol=symbol, repo=repo, use_new_data=use_new_data)

    return model


@app.post("/fit", status_code=200, response_model=dict)
def fit_model(request: FitInput):
    response = request.dict()

    try:
        model = build_model(symbol=request.symbol, use_new_data=request.use_new_data)

        model.wrangle_data(n_observations=request.n_observations)

        model.fit(p=request.p, q=request.q)

        filename = model.dump()

        response["success"] = True
        response["message"] = f"Trained and saved {filename}. AIC: {model.aic}, BIC: {model.bic}"
    except Exception as e:
        response["success"] = False
        response["message"] = str(e)

    return response


@app.post("/predict", status_code=200, response_model=dict)
def get_prediction(request: PredictInput):
    response = request.dict()

    try:
        model = build_model(symbol=request.symbol, use_new_data=False)

        model.load()

        prediction = model.predict_volatility(horizon=request.n_days)

        response["success"] = True
        response["forecast"] = prediction
        response["message"] = ""

    except Exception as e:
        response["success"] = False
        response["forecast"] = {}
        response["message"] = str(e)

    return response
