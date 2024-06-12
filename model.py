import os
from glob import glob

import pandas as pd
import joblib
from arch import arch_model
from settings import MODEL_DIRECTORY, API_KEY
from alphavantageapi import AlphaVantageAPI


class GarchModel:

    def __init__(self, symbol, repo, use_new_data, model_directory=MODEL_DIRECTORY):

        self.symbol = symbol
        self.repo = repo
        self.use_new_data = use_new_data
        self.model_directory = model_directory

    def wrangle_data(self, n_observations):
        if self.use_new_data:
            API = AlphaVantageAPI(API_KEY)
            new_data = API.get_daily(symbol=self.symbol)
            self.repo.insert_table(table_name=self.symbol, records=new_data, if_exists="replace")

        df = self.repo.read_table(table_name=self.symbol, limit=n_observations + 1)
        df.sort_index(ascending=True, inplace=True)
        df["return"] = df["close"].pct_change() * 100

        self.data = df["return"].dropna()

    def fit(self, p, q):
        self.model = arch_model(
            self.data,
            p=p,
            q=q,
            rescale=False
        ).fit(disp=False)

        self.aic = self.model.aic
        self.bic = self.model.bic

    def __clean_prediction(self, prediction):

        start = prediction.index[0] + pd.DateOffset(days=1)

        prediction_dates = pd.bdate_range(start=start, periods=prediction.shape[1])

        prediction_index = [d.isoformat() for d in prediction_dates]

        data = prediction.values.flatten() ** 0.5

        prediction_formatted = pd.Series(data, index=prediction_index)

        return prediction_formatted.to_dict()

    def predict_volatility(self, horizon=5):

        prediction = self.model.forecast(horizon=horizon, reindex=False).variance

        prediction_formatted = self.__clean_prediction(prediction)

        return prediction_formatted

    def dump(self):

        timestamp = pd.Timestamp.now().isoformat().replace(":", "_")

        filepath = os.path.join(self.model_directory, f"{timestamp}_{self.symbol}.pkl")

        joblib.dump(self.model, filepath)

        return filepath

    def load(self):

        pattern = os.path.join(self.model_directory, f"*{self.symbol}.pkl")
        try:
            model_path = sorted(glob(pattern))[-1]

        except IndexError:
            raise Exception(f"No model trained for {self.symbol}.")

        self.model = joblib.load(model_path)
