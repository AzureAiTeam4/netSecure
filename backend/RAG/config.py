import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_KEY = os.environ["AZURE_OPENAI_API_KEY"]
AZURE_OPENAI_DEPLOYMENT = os.environ["AZURE_OPENAI_DEPLOYMENT"]

AZURE_SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
AZURE_SEARCH_KEY = os.environ["AZURE_SEARCH_KEY"]
AZURE_SEARCH_INDEX = os.environ["AZURE_SEARCH_INDEX_NAME"]
AZURE_SEARCH_SEMANTIC_CONFIG = os.environ["AZURE_SEARCH_SEMANTIC_CONFIG"]

SEARCH_TOP_K = 3
