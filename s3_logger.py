import boto3
import logging
import os
import time
import threading
from datetime import datetime, timezone, timedelta
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


# ──────────────────────────────────────────────
# UPLOAD
# ──────────────────────────────────────────────

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


# ──────────────────────────────────────────────
# LIST
# ──────────────────────────────────────────────

def list_logs_in_s3(prefix: str = "logs/") -> list:
    """
    Lists all log files in the S3 bucket under the given prefix.

    Args:
        prefix: S3 key prefix to filter results (default: 'logs/').

    Returns:
        List of dicts with keys: key, size, last_modified.
    """
    try:
        logger.info("Listing objects in s3://%s/%s", BUCKET_NAME, prefix)
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

        if response.get("KeyCount", 0) == 0:
            logger.info("No objects found under prefix: %s", prefix)
            return []

        files = []
        for obj in response.get("Contents", []):
            files.append({
                "key": obj["Key"],
                "size_kb": round(obj["Size"] / 1024, 2),
                "last_modified": obj["LastModified"].strftime("%Y-%m-%d %H:%M:%S UTC")
            })
            logger.info("  Found: %s (%.2f KB)", obj["Key"], obj["Size"] / 1024)

        logger.info("Total: %d file(s) found.", len(files))
        return files

    except Exception as e:
        logger.error("S3 list failed: %s", e)
        return []


# ──────────────────────────────────────────────
# DELETE
# ──────────────────────────────────────────────

def delete_old_logs(days_old: int = 30, prefix: str = "logs/") -> int:
    """
    Deletes S3 log files older than a specified number of days.

    Args:
        days_old: Files older than this many days will be deleted.
        prefix: S3 key prefix to filter (default: 'logs/').

    Returns:
        Number of files deleted.
    """
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days_old)
        logger.info("Deleting logs older than %d days (before %s)...", days_old, cutoff.date())

        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)

        if response.get("KeyCount", 0) == 0:
            logger.info("No objects to delete.")
            return 0

        to_delete = [
            {"Key": obj["Key"]}
            for obj in response.get("Contents", [])
            if obj["LastModified"] < cutoff
        ]

        if not to_delete:
            logger.info("No files older than %d days found.", days_old)
            return 0

        s3_client.delete_objects(
            Bucket=BUCKET_NAME,
            Delete={"Objects": to_delete}
        )

        for obj in to_delete:
            logger.info("Deleted: %s", obj["Key"])

        logger.info("Deleted %d file(s) total.", len(to_delete))
        return len(to_delete)

    except Exception as e:
        logger.error("S3 delete failed: %s", e)
        return 0


# ──────────────────────────────────────────────
# FILE WATCHER
# ──────────────────────────────────────────────

def watch_and_upload(watch_dir: str = ".", prefix: str = "logs/", poll_interval: int = 10):
    """
    Watches a local directory for new .txt log files and auto-uploads them to S3.

    Args:
        watch_dir: Local directory to watch (default: current dir).
        prefix: S3 key prefix for uploaded files (default: 'logs/').
        poll_interval: Seconds between directory scans (default: 10).
    """
    logger.info("Watching directory '%s' for new log files (every %ds)...", watch_dir, poll_interval)
    seen_files = set(
        f for f in os.listdir(watch_dir)
        if f.endswith(".txt") and f.startswith("freight-log-")
    )
    logger.info("Existing files ignored: %d", len(seen_files))

    try:
        while True:
            time.sleep(poll_interval)
            current_files = set(
                f for f in os.listdir(watch_dir)
                if f.endswith(".txt") and f.startswith("freight-log-")
            )
            new_files = current_files - seen_files

            for filename in new_files:
                local_path = os.path.join(watch_dir, filename)
                today = datetime.now().strftime("%Y-%m-%d")
                s3_key = f"{prefix}{today}/{filename}"
                logger.info("New log detected: %s — uploading...", filename)
                success = upload_log_to_s3(local_path, s3_key)
                if success:
                    seen_files.add(filename)

    except KeyboardInterrupt:
        logger.info("File watcher stopped.")


# ──────────────────────────────────────────────
# LOG CREATOR
# ──────────────────────────────────────────────

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


# ──────────────────────────────────────────────
# MAIN — Demo all features
# ──────────────────────────────────────────────

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

    # 1. Create and upload daily log
    log_file = create_daily_log(test_data)
    today = datetime.now().strftime("%Y-%m-%d")
    s3_key = f"logs/{today}/{log_file}"
    upload_log_to_s3(log_file, s3_key)

    # 2. List all logs in S3
    print("\n--- S3 Log Listing ---")
    files = list_logs_in_s3()
    for f in files:
        print(f"  {f['key']} | {f['size_kb']} KB | {f['last_modified']}")

    # 3. Delete logs older than 30 days
    print("\n--- Deleting Old Logs ---")
    deleted = delete_old_logs(days_old=30)
    print(f"  Deleted {deleted} old log(s).")

    # 4. Start file watcher in background thread (optional)
    # Uncomment to enable:
    # watcher_thread = threading.Thread(target=watch_and_upload, daemon=True)
    # watcher_thread.start()
    # watcher_thread.join()