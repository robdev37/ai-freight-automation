import boto3
import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "robdigitalph@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ALERT_RECIPIENT = "robdigitalph@gmail.com"
COST_THRESHOLD = 10.00  # USD — alert if spending exceeds this

# ──────────────────────────────────────────────
# GET AWS COST
# ──────────────────────────────────────────────

def get_aws_cost():
    """
    Gets current month AWS cost using Cost Explorer.
    Returns total cost in USD.
    """
    try:
        client = boto3.client("ce", region_name="ap-southeast-1")

        today = datetime.today()
        start = today.replace(day=1).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")

        response = client.get_cost_and_usage(
            TimePeriod={"Start": start, "End": end},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"]
        )

        cost = float(
            response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Amount"]
        )
        unit = response["ResultsByTime"][0]["Total"]["UnblendedCost"]["Unit"]

        logger.info("Current AWS cost: %.2f %s", cost, unit)
        return cost, unit

    except Exception as e:
        logger.error("Failed to get AWS cost: %s", e)
        return None, None

# ──────────────────────────────────────────────
# SEND EMAIL ALERT
# ──────────────────────────────────────────────

def send_email_alert(cost, unit, threshold):
    """
    Sends a Gmail alert when AWS cost exceeds threshold.
    """
    try:
        subject = f"🚨 AWS Cost Alert — ${cost:.2f} {unit} exceeded threshold!"
        today = datetime.now().strftime("%Y-%m-%d %H:%M")

        body = f"""
        ====================================
        🚚 AI Freight Automation — AWS Cost Alert
        ====================================

        ⚠️  Your AWS spending has exceeded the threshold!

        📅 Date         : {today}
        💰 Current Cost : ${cost:.2f} {unit}
        🎯 Threshold    : ${threshold:.2f} {unit}
        📈 Over by      : ${cost - threshold:.2f} {unit}

        ====================================
        Services to check:
        - EC2 (t3.micro)
        - S3 (freight-automation-logs)
        - Cost Explorer
        ====================================

        Please review your AWS Console:
        https://console.aws.amazon.com/billing

        — AI Freight Automation System
        """

        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = ALERT_RECIPIENT
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        logger.info("Alert email sent to %s", ALERT_RECIPIENT)
        return True

    except Exception as e:
        logger.error("Failed to send email: %s", e)
        return False

# ──────────────────────────────────────────────
# SEND DAILY SUMMARY (regardless of threshold)
# ──────────────────────────────────────────────

def send_daily_summary(cost, unit):
    """
    Sends a daily cost summary email.
    """
    try:
        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        status = "✅ Within budget" if cost < COST_THRESHOLD else "⚠️ Over budget"

        subject = f"📊 AWS Daily Cost Summary — ${cost:.2f} {unit}"
        body = f"""
        ====================================
        🚚 AI Freight Automation — Daily Cost Summary
        ====================================

        📅 Date         : {today}
        💰 Current Cost : ${cost:.2f} {unit}
        🎯 Threshold    : ${COST_THRESHOLD:.2f} {unit}
        📊 Status       : {status}

        ====================================
        Keep monitoring your AWS usage!
        https://console.aws.amazon.com/billing
        ====================================

        — AI Freight Automation System
        """

        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = ALERT_RECIPIENT
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        logger.info("Daily summary sent to %s", ALERT_RECIPIENT)
        return True

    except Exception as e:
        logger.error("Failed to send summary: %s", e)
        return False

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # Test email directly without AWS
    send_daily_summary(2.50, "USD")
    print("Test email sent!")