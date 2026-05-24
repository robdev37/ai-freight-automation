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
    Now uses JSON mode (guaranteed output) + confidence score.
    """
    logger.info("Extracting freight details from message...")

    system_prompt = """
You are an AI assistant for freight logistics automation.
Extract structured shipment data from unstructured customer messages.

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
Classify request_type into ONLY one of:
- Quote → message contains "quote", "truckload", "pricing", "rate", or "need"
- Follow-up → message contains "follow up", "checking", "status", or "update"
- Issue → message contains "issue", "delay", "damaged", "complaint", or "problem"
Default to "Quote" if unclear.

=====================
PRIORITY RULES
=====================
- High → message contains "urgent", "ASAP", "immediately"
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
- Quote → "Provide shipment quote"
- Follow-up → "Provide status update"
- Issue → "Investigate and resolve issue"
- Incomplete data → "Request missing shipment details from customer"

=====================
OUTPUT FORMAT (JSON only, no explanation)
=====================
{
    "request_type": "Quote|Follow-up|Issue",
    "origin": "city name or Unknown",
    "destination": "city name or Unknown",
    "quantity": "amount or Unknown",
    "priority": "High|Medium",
    "department": "Sales|Operations",
    "recommended_action": "short action string",
    "confidence_score": 0.0 to 1.0
}

confidence_score rules:
- 0.9–1.0 → all key fields present and clear
- 0.7–0.89 → most fields present, minor ambiguity
- 0.5–0.69 → several fields missing or message is vague
- below 0.5 → very unclear, missing most data
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # required for json_object mode
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            response_format={"type": "json_object"},  # ✅ Week 2 upgrade
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


def draft_reply(message: str, classification: dict) -> Optional[str]:
    """
    CALL 2 — Takes classification from extract_freight_details()
    and drafts a professional reply to the customer.
    """
    logger.info("Drafting reply for request type: %s", classification.get("request_type"))

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional freight coordinator named Sarah from FreightOps Team. Write short, friendly, professional reply emails. Always sign off as: Sarah | FreightOps Coordination Team"
                },
                {
                    "role": "user",
                    "content": f"""
Customer message: {message}

Classified as:
- Type: {classification.get('request_type')}
- Priority: {classification.get('priority')}
- Route: {classification.get('origin')} → {classification.get('destination')}
- Quantity: {classification.get('quantity')}
- Action needed: {classification.get('recommended_action')}

Write a reply email to the customer.
"""
                }
            ],
            temperature=0.7
        )

        reply = response.choices[0].message.content
        logger.info("Reply drafted successfully")
        return reply

    except Exception as e:
        logger.error("Failed to draft reply: %s", e)
        return None


def run_freight_pipeline(message: str) -> Optional[dict]:
    """
    Full pipeline: Extract → Draft Reply (2 chained API calls)
    """
    # Call 1: Extract & classify
    classification = extract_freight_details(message)
    if not classification:
        logger.error("Pipeline failed at extraction step")
        return None

    # Call 2: Draft reply based on Call 1 output
    reply = draft_reply(message, classification)
    if not reply:
        logger.error("Pipeline failed at reply drafting step")
        return None

    return {
        "classification": classification,
        "reply": reply
    }


# ─── Quick Test ───────────────────────────────────────────
if __name__ == "__main__":
    test_messages = [
        "Hi I need an urgent quote for 500kg Manila to Dubai",
        "My shipment #1234 has been delayed for 3 days, what's happening?",
        "Just following up on the quote I requested last week"
    ]

    for i, msg in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {msg}")
        print('='*60)
        result = run_freight_pipeline(msg)
        if result:
            print("\n📦 CLASSIFICATION:")
            print(json.dumps(result["classification"], indent=2))
            print("\n✉️  REPLY:")
            print(result["reply"])