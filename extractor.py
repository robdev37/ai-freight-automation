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


def extract_freight_details(message: str) -> Optional[dict]:
    """
    Extracts shipment details from a raw freight request message.

    Args:
        message: Raw email or chat message from a customer.

    Returns:
        Dict with keys: request_type, origin, destination,
        quantity, priority, department, recommended_action.
        Returns None if extraction fails.
    """
    logger.info("Extracting freight details from message...")

    prompt = f"""
You are an AI assistant for freight logistics automation.
Your task is to extract structured shipment data from an unstructured customer message.

=====================
EXTRACTION RULES
=====================
- Extract ONLY information explicitly stated in the message.
- Do NOT guess, infer, or invent any missing data.
- If origin, destination, or quantity is missing, return "Unknown".
- Always capitalize city names properly (e.g., Chicago, Dallas).

=====================
CLASSIFICATION RULES
=====================
Classify request_type into ONLY one of the following:
- Quote → if message contains "quote", "truckload", "pricing", "rate", or "need"
- Follow-up → if message contains "follow up", "checking", "status", or "update"
- Issue → if message contains "issue", "delay", "damaged", "complaint", or "problem"
Default to "Quote" if unclear.

=====================
PRIORITY RULES
=====================
- High → if message contains "urgent", "ASAP", "immediately"
- Medium → otherwise

=====================
DEPARTMENT ROUTING
=====================
- Quote → Sales
- Follow-up → Sales
- Issue → Operations

=====================
RECOMMENDED ACTION RULES
=====================
Generate a short, clear action:
- Quote → "Provide shipment quote"
- Follow-up → "Provide status update"
- Issue → "Investigate and resolve issue"
If data is incomplete:
→ "Request missing shipment details from customer"

=====================
OUTPUT REQUIREMENTS
=====================
Return ONLY a JSON object with these fields:
- request_type
- origin
- destination
- quantity
- priority
- department
- recommended_action
- Never return null
- Never leave fields blank
- Use "Unknown" where necessary

Message: {message}

Return JSON only. No explanation.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        raw = response.choices[0].message.content
        result = json.loads(raw)
        logger.info("Extraction successful: %s", result)
        return result

    except json.JSONDecodeError:
        logger.error("Failed to parse JSON from OpenAI response")
        return None
    except Exception as e:
        logger.error("OpenAI API error: %s", e)
        return None