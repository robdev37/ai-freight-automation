import logging
from extractor import extract_freight_details
from sheets_logger import connect_to_sheet, log_freight_request
from s3_logger import create_daily_log, upload_log_to_s3
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

processed_requests = []

def process_freight_request(message: str) -> None:
    """
    Full pipeline: extract → log to Sheets → backup to S3.

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

    # Step 4: Add to processed list for S3 backup
    processed_requests.append(data)

    logger.info("=== Request Processed Successfully! ===")


if __name__ == "__main__":
    test_messages = [
        "Hi, I need a quote for shipping 20 pallets from Cebu to Manila by Friday.",
        "Our delivery from Davao to BGC is already 2 days late, what's the status?",
        "Can you follow up on my shipment order #4521 from last week?"
    ]

    for message in test_messages:
        process_freight_request(message)
        print("---")

    # Step 5: Upload daily log to S3
    if processed_requests:
        log_file = create_daily_log(processed_requests)
        today = datetime.now().strftime("%Y-%m-%d")
        s3_key = f"logs/{today}/{log_file}"
        upload_log_to_s3(log_file, s3_key)