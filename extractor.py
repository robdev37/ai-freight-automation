import openai
import logging
import json
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))