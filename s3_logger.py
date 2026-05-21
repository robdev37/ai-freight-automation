import boto3
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BUCKET_NAME = "freight-automation-logs"
REGION = "ap-southeast-2"

s3_client = boto3.client("s3", region_name=REGION)


def upload_log_to_s3(local_file: str, s3_key: str) -> bool:
    """
    Uploads a local file to S3 bucket.

    Args:
        local_file: Path to local file to upload.
        s3_key: Destination path/name in S3 bucket.

    Returns:
        True if upload successful, False otherwise.
    """
    try:
        logger.info("Uploading %s to S3...", local_file)
        s3_client.upload_file(local_file, BUCKET_NAME, s3_key)
        logger.info("Successfully uploaded to s3://%s/%s", BUCKET_NAME, s3_key)
        return True
    except Exception as e:
        logger.error("S3 upload failed: %s", e)
        return False


def create_daily_log(data: list) -> str:
    """
    Creates a daily log file from freight request data.

    Args:
        data: List of freight request dicts.

    Returns:
        Path to the created log file.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"freight-log-{today}.txt"

    with open(filename, "w") as f:
        f.write(f"Freight Log — {today}\n")
        f.write("=" * 50 + "\n\n")
        for i, entry in enumerate(data, 1):
            f.write(f"Entry {i}:\n")
            for key, value in entry.items():
                f.write(f"  {key}: {value}\n")
            f.write("\n")

    logger.info("Log file created: %s", filename)
    return filename


if __name__ == "__main__":
    test_data = [
        {
            "message": "Urgent truckload from Cebu to Manila",
            "request_type": "Quote",
            "origin": "Cebu",
            "destination": "Manila",
            "priority": "High",
            "department": "Sales"
        },
        {
            "message": "Shipment from Davao delayed",
            "request_type": "Issue",
            "origin": "Davao",
            "destination": "BGC",
            "priority": "High",
            "department": "Operations"
        }
    ]

    log_file = create_daily_log(test_data)
    today = datetime.now().strftime("%Y-%m-%d")
    s3_key = f"logs/{today}/{log_file}"
    upload_log_to_s3(log_file, s3_key)