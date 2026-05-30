
## Latest Update
- Added Zapier automation support for external integrations
- Connected Gmail inbox — bot now reads and processes real emails automatically
- Added confidence scoring (0.0–1.0) to every extraction
- Auto-drafts professional reply emails per request type
- Added `email_parser.py` to project

---
🎥 System Demo

Watch the full walkthrough here:

👉 https://your-youtube-link

---


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
- Stores and queries freight data in MySQL database
- REST API with FastAPI for receiving and processing freight requests
- Webhook endpoint for real-time event notifications
- AWS cost monitoring with automated Gmail alerts

## Results

- ~70% reduction in processing time
- Eliminated manual data entry errors
- Consistent 5-star client satisfaction

## Tech Stack

- Python, OpenAI GPT-4, Google Sheets API, AWS S3, boto3, gspread
- MySQL, PyMySQL, FastAPI, Uvicorn
- AWS Cost Explorer, Gmail SMTP

## Project Structure

```
ai-freight-automation/
├── main.py             # Orchestrates the full pipeline
├── extractor.py        # GPT-4 extraction & classification
├── sheets_logger.py    # Logs structured data to Google Sheets
├── s3_logger.py        # Upload, list, delete, and watch logs in S3
├── mysql_reporter.py   # Python MySQL daily report generator
├── freight_api.py      # FastAPI REST API with webhook support
├── cost_alert.py       # AWS cost monitor with Gmail alert
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

## REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `GET` | `/freight` | List all freight requests |
| `GET` | `/freight/summary` | Summary by type and priority |
| `POST` | `/freight` | Create a new freight request |
| `POST` | `/webhook` | Receive webhook event payloads |

## AWS Cost Alert

Monitors AWS monthly spending via boto3 and Cost Explorer. Sends automated Gmail alerts when spending exceeds the threshold ($10.00 USD), plus a daily summary email with current cost and budget status.

| Function | Description |
|---|---|
| `get_aws_cost()` | Fetches current month AWS cost via Cost Explorer |
| `send_daily_summary()` | Sends daily cost summary email via Gmail |
| `send_email_alert()` | Sends alert email when cost exceeds threshold |

## MySQL Daily Report

Connects Python to MySQL (`freight_db`) and generates automated daily reports including total requests, priority breakdown, and department summary.

## Deployment

- Deployed on AWS EC2 (t3.micro, Amazon Linux 2023)
- Runs on cloud server 24/7
- Auto-logs to Google Sheets in real-time
- Daily backup to AWS S3
- Auto-cleanup of logs older than 30 days
- REST API running via Uvicorn on port 8000
- Daily AWS cost alert via Gmail

## Setup

1. Clone the repo
2. Add your `.env` file with `OPENAI_API_KEY`, `GMAIL_ADDRESS`, `GMAIL_APP_PASSWORD`
3. Add your `credentials.json` from Google Cloud
4. Configure AWS credentials via `aws configure`
5. Set up MySQL and run `python mysql_reporter.py`
6. Start the API with `python freight_api.py`
7. Run cost alert with `python cost_alert.py`
8. Run the full pipeline with `python main.py`
