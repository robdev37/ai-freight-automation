import logging
from extractor import extract_freight_details
from sheets_logger import connect_to_sheet, log_freight_request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def process_freight_request(message: str) -> None:
    """
    Full pipeline: extract freight details from message
    and log to Google Sheets automatically.

    Args:
        message: Raw freight request message from customer.
    """
    logger.info("=== New Freight Request Received ===")
    logger.info("Message: %s", message)

    # Step 1: Extract details using OpenAI
    data = extract_freight_details(message)

    if not data:
        logger.error("Extraction failed. Skipping logging.")
        return

    # Step 2: Add original message to data
    data["message"] = message

    # Step 3: Log to Google Sheets
    sheet = connect_to_sheet("AI Freight Workflow System")
    log_freight_request(sheet, data)

    logger.info("=== Request Processed Successfully! ===")


if __name__ == "__main__":
    # Test with multiple messages
    test_messages = [
        "Please provide a quote for shipment from San Diego to Las Vegas, 6 pallets.",
        "Shipment from Dallas to Atlanta, 8 pallets is delayed. Customer requesting ETA.",
        "Quote ny to boston 2 pallets asap"
    ]

    for message in test_messages:
        process_freight_request(message)
        print("---")