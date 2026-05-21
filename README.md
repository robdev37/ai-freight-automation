# 🚚 AI Freight Request Automation

Automates freight request processing using AI — reduce manual work, speed up response time, and eliminate errors.

## What it does
- Extracts shipment details from raw customer messages using GPT-4
- Classifies request type (Quote / Issue / Follow-up)
- Assigns priority and department automatically
- Logs structured data to Google Sheets in real-time
- Backs up daily logs to AWS S3 automatically

## Results
- ~70% reduction in processing time
- Eliminated manual data entry errors
- Consistent 5-star client satisfaction

## Tech Stack
- Python, OpenAI GPT-4, Google Sheets API, AWS S3, boto3, gspread

## Deployment
- Deployed on AWS EC2 (t3.micro, Amazon Linux 2023)
- Runs on cloud server 24/7
- Auto-logs to Google Sheets in real-time
- Daily backup to AWS S3

## Project Structure

## Setup
1. Clone the repo
2. Add your `.env` file with `OPENAI_API_KEY`
3. Add your `credentials.json` from Google Cloud
4. Configure AWS credentials via `aws configure`
5. Run `python main.py`
