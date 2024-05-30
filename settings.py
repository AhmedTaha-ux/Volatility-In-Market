import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_KEY = os.environ.get("API_KEY")
DB_NAME = os.environ.get("DB_NAME")
MODEL_DIRECTORY = os.environ.get("MODEL_DIRECTORY")
