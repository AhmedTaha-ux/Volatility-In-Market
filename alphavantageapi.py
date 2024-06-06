from settings import API_KEY
import requests
import pandas as pd

class AlphaVantageAPI:
    def __init__(self, api_key=API_KEY):
        self.__api_key = api_key

    def get_daily(self, symbol, output_size="full"):
        """Get Time Series Stock Data From AlphaVantageAPI

        :param symbol: str
            The name of the equity of your choice
        :param output_size: str, optional
            The number of observations. by default "full".
            Strings compact and full are accepted with the following specifications:
            compact returns only the latest 100 data points;
            full returns the full-length time series of 20+ years of historical data.
        :return: pd.DataFrame
            Columns are 'open', 'high', 'low', 'close', and 'volume'.
            All columns are numeric.
        """
        url = (
            "https://www.alphavantage.co/query?"
            "function=TIME_SERIES_DAILY&"
            f"symbol={symbol}&"
            f"outputsize={output_size}&"
            f"apikey={self.__api_key}"
        )

        # Send reqeust to API
        response = requests.get(url=url)

        response_data = response.json()
        if "Time Series (Daily)" not in response_data.keys():
            raise Exception(
                f"Invalid API Call. Check symbol {symbol} is correct."
            )

        # Read data into DataFrame
        stock_data = response_data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(stock_data, orient="index", dtype=float)

        # Convert index to `DatetimeIndex` named "date"
        df.index = pd.to_datetime(df.index)
        df.index.name = "date"

        # Remove numbering from columns
        df.columns = [c.split(". ")[1] for c in df.columns]

        return df