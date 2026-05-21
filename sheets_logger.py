import gspread
import logging
from google.oauth2.service_account import Credentials
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def connect_to_sheet(sheet_name: str) -> gspread.Worksheet:
    """
    Connects to a Google Sheet using service account credentials.

    Args:
        sheet_name: Name of the Google Sheet to connect to.

    Returns:
        The first worksheet of the specified Google Sheet.
    """
    logger.info("Connecting to Google Sheets...")
    creds = Credentials.from_service_account_file(
        "credentials.json", scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1
    logger.info("Connected successfully!")
    return sheet


def log_freight_request(sheet: gspread.Worksheet, data: dict) -> None:
    """
    Logs extracted freight data as a new row in Google Sheets.

    Args:
        sheet: The worksheet to write to.
        data: Dict containing freight request details.
    """
    timestamp = datetime.now().strftime("%m/%d/%y %I:%M %p")
    row = [
        data.get("message", ""),
        data.get("request_type", ""),
        f"Origin: {data.get('origin')} | Destination: {data.get('destination')} | Qty: {data.get('quantity')}",
        data.get("priority", ""),
        data.get("department", ""),
        data.get("recommended_action", ""),
        "New",
        timestamp
    ]
    sheet.append_row(row)
    logger.info("Row logged to Google Sheets: %s", row)


if __name__ == "__main__":
    sheet = connect_to_sheet("AI Freight Workflow System")

    test_data = {
        "message": "Urgent full truckload from Houston to Chicago, 18 pallets ASAP.",
        "request_type": "Issue",
        "origin": "Houston",
        "destination": "Chicago",
        "quantity": 18,
        "priority": "High",
        "department": "Operations",
        "recommended_action": "Arrange full truckload ASAP"
    }

    log_freight_request(sheet, test_data)
    print("Done! Check your Google Sheet!")