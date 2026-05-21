# 🚚 AI Freight Request Automation

Automates freight request processing using AI — reduce manual work, speed up response time, and eliminate errors.

## What it does

- Extracts shipment details from raw customer messages using GPT-4
- Classifies request type (Quote / Issue / Follow-up)
- Assigns priority and department automatically
- Logs structured data to Google Sheets in real-time
- Backs up daily logs to AWS S3 automatically
- Auto-deletes old logs older than 30 days
- File watcher that detects and uploads new logs to S3 automatically

## Results

- ~70% reduction in processing time
- Eliminated manual data entry errors
- Consistent 5-star client satisfaction

## Tech Stack

- Python, OpenAI GPT-4, Google Sheets API, AWS S3, boto3, gspread

## Project Structure

```
ai-freight-automation/
├── main.py             # Orchestrates the full pipeline
├── extractor.py        # GPT-4 extraction & classification
├── sheets_logger.py    # Logs structured data to Google Sheets
├── s3_logger.py        # Upload, list, delete, and watch logs in S3
├── .env                # API keys (not committed)
├── credentials.json    # Google Cloud credentials (not committed)
└── README.md
```

## S3 Logger Features

| Function | Description |
|---|---|
| `upload_log_to_s3()` | Uploads a local log file to S3 |
| `list_logs_in_s3()` | Lists all log files in the S3 bucket |
| `delete_old_logs()` | Deletes logs older than 30 days automatically |
| `create_daily_log()` | Creates a structured daily `.txt` log file |
| `watch_and_upload()` | Watches a directory and auto-uploads new logs to S3 |

## Deployment

- Deployed on AWS EC2 (t3.micro, Amazon Linux 2023)
- Runs on cloud server 24/7
- Auto-logs to Google Sheets in real-time
- Daily backup to AWS S3
- Auto-cleanup of logs older than 30 days

## Setup

1. Clone the repo
2. Add your `.env` file with `OPENAI_API_KEY`
3. Add your `credentials.json` from Google Cloud
4. Configure AWS credentials via `aws configure`
5. Run `python main.py`
