# Volatility In Market

## Description
This project analyzes the volatility of stock market data using a GARCH model. We'll fetch the data from [alphavantage](https://www.alphavantage.co/) and store it in SQL database, preprocess it, and make APIs to fit the model to make predictions, and Predicting the volatility.

## Table of Contents 
1. [Installation](#installation)
2. [Usage](#usage)

## Installation

### Prerequisites
Make sure you have the following software installed on your machine:
- [Python 3.8+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

### Clone the Repository
First, clone the repository to your local machine using Git.
```bash
git clone https://github.com/AhmedTaha-ux/Volatility-In-Market
cd Volatility-In-Market
```

### Install Dependencies
Install the necessary dependencies using `pip`.
```bash
pip install -r requirements.txt
```

### Environment Variables
Set up the necessary environment variables. You can create a `.env` file in the root directory of your project with the following contents:
```env
API_KEY = YOU CAN GET YOUR KEY FROM (https://www.alphavantage.co/support/#api-key)
DB_NAME = YOUR DATABASE NAME
MODEL_DIRECTORY = THE DIRECTORY IN WHICH YOUR DATA IS SAVED
```

## Usage
Once you have installed and set up the project, you can start using it. Below are examples and explanations of how to use the key features of the application.

### Running the Development Server
```bash
uvicorn main:app --reload --workers 1 --host localhost --port 8008
```
or 
```bash
fastapi dev main.py
```

### Creating and Managing Content
1. `/fit` API
    - Creat http request `POST` at `http://127.0.0.1:8008/fit`.
    - Send json contains the following:
        * **symbol**: The name of the equity of your choice. For example: `'symbol': 'IBM'`. you can get the list of available symbol from this [API](https://www.alphavantage.co/query?function=MARKET_STATUS&apikey=demo).
        * **use_new_data**: Boolean input to get new data from alphavantage API or use data from SQL database. For example: `'use_new_data': 'False'`.
        * **n_observations**: The number of observations. For example: `'n_observations': 4000`
        * **p**: Lag order of the symmetric innovation. For example: `'p': 1`.
        * **q**: Lag order of lagged volatility or equivalent. For example: `'q': 1`.
2. `/predict` API
   - Creat http request `POST` at `http://127.0.0.1:8008/predict`
   - Send json contains the following:
      * **symbol**: The name of the equity of your choice. For example: `'symbol': 'IBM'`.
      * **n_days**: The number of days want to predict. For example: `'n_days': 5`.

    