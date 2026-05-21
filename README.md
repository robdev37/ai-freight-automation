# 🚚 AI Freight Request Automation

Automates freight request processing using OpenAI and Google Sheets.

## What it does
- Extracts shipment details from raw customer messages using GPT-4
- Classifies request type (Quote / Issue / Follow-up)
- Assigns priority and department automatically
- Logs structured data to Google Sheets in real-time

## Results
- ~70% reduction in processing time
- Eliminated manual data entry errors
- Consistent 5-star client satisfaction

## Tech Stack
- Python, OpenAI API, Google Sheets API, gspread

## Setup
1. Clone the repo
2. Add your `.env` file with `OPENAI_API_KEY`
3. Add your `credentials.json` from Google Cloud
4. Run `python main.py`

## Deployment
- Deployed on AWS EC2 (t3.micro, Amazon Linux 2023)
- Runs on cloud server 24/7
- Auto-logs to Google Sheets in real-time
