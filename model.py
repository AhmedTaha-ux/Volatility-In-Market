import os
from glob import glob

import pandas as pd
import joblib
from arch import arch_model
from settings import MODEL_DIRECTORY, API_KEY
from AlphaVantageAPI import AlphaVantageAPI

class GarchModel:

    class GarchModel:
        """
        A class for training and managing GARCH models for volatility forecasting.

        This class facilitates the creation, training, prediction, and serialization of GARCH
        models for a given stock symbol. It interacts with an AlphaVantageAPI instance to
        retrieve or update data, utilizes pandas for data manipulation, employs the ARCH library
        for model fitting, and leverages joblib for model persistence.

        Attributes:
            symbol (str): The stock symbol for which the model is being built.
            repo (object): An object representing a data repository (implementation details
                           depend on the specific library or custom solution used).
            use_new_data (bool): A flag indicating whether to retrieve and use the latest
                                 data from the AlphaVantage API before training.
            model_directory (str): The directory path for storing trained model files (default
                                    is defined in `settings.MODEL_DIRECTORY`).
            model (arch.arch_model, optional): The fitted GARCH model (initialized as None).
            aic (float, optional): The Akaike Information Criterion (AIC) value of the fitted
                                   model (initialized as None).
            bic (float, optional): The Bayesian Information Criterion (BIC) value of the fitted
                                   model (initialized as None).

        Methods:
            wrangle_data(self, n_observations: int) -> None:
                Retrieves or updates data for the symbol, cleans it, and calculates returns.
                If `use_new_data` is True, fetches data from the AlphaVantage API and
                updates the data repository. Reads data from the repository, sorts it by
                date, and calculates percentage returns as the difference in closing prices.

            fit(self, p: int, q: int) -> None:
                Fits a GARCH model to the returns data using the specified `p` (number
                of lagged ARCH terms) and `q` (number of lagged GARCH terms).
                Utilizes the `arch` library's `arch_model` function for model fitting. Stores
                the fitted model, its AIC, and BIC values in the corresponding attributes.

            __clean_prediction(self, prediction: pd.Series) -> dict:
                Processes a volatility prediction for a given horizon. Internal method, not
                intended for external use. Creates date indices for the prediction, flattens
                the values (assuming a single volatility series), and takes the square root
                to transform from variance to standard deviation. Returns the prediction
                as a dictionary.

            predict_volatility(self, horizon: int = 5) -> dict:
                Predicts future volatility for the specified `horizon` (number of days).
                Employs the fitted model's `forecast` method to generate predictions.
                Calls the internal `__clean_prediction` method to format and return the
                volatility forecast as a dictionary.

            dump(self) -> str:
                Saves the trained model to a file. Generates a unique filename using the
                current timestamp and symbol, and stores the model using `joblib.dump`.
                Returns the filepath where the model is saved.

            load(self) -> None:
                Loads a previously trained model for the symbol. Searches for model files
                matching the symbol in the `model_directory` using a glob pattern. If a
                model is found, loads it using `joblib.load`. Raises an exception if no
                model is found for the symbol.
        """

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

        df = self.repo.read_table(table_name=self.symbol, limit=n_observations+1)
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