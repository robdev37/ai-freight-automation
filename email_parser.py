import os
import base64
import json
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from extractor import run_freight_pipeline

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def get_unread_emails(service, max_results=5):
    results = service.users().messages().list(
        userId="me", labelIds=["INBOX"], q="is:unread", maxResults=max_results
    ).execute()
    messages = results.get("messages", [])
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        headers = msg_data["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown")
        body = ""
        payload = msg_data["payload"]
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data", "")
                    body = base64.urlsafe_b64decode(data).decode("utf-8")
                    break
        elif "body" in payload:
            data = payload["body"].get("data", "")
            body = base64.urlsafe_b64decode(data).decode("utf-8")
        emails.append({"id": msg["id"], "subject": subject, "sender": sender, "body": body})
    return emails


def process_emails():
    print("🔌 Connecting to Gmail...")
    service = get_gmail_service()

    print("📬 Fetching unread emails...")
    emails = get_unread_emails(service, max_results=5)

    if not emails:
        print("✅ No unread emails found.")
        return

    print(f"📧 Found {len(emails)} unread email(s)\n")

    for i, email in enumerate(emails, 1):
        print(f"{'='*60}")
        print(f"EMAIL {i}: {email['subject']}")
        print(f"FROM: {email['sender']}")
        print(f"{'='*60}")

        full_message = f"Subject: {email['subject']}\n\n{email['body']}"
        result = run_freight_pipeline(full_message)

        if result:
            print("\n📦 CLASSIFICATION:")
            print(json.dumps(result["classification"], indent=2))
            print("\n✉️  DRAFT REPLY:")
            print(result["reply"])
        else:
            print("⚠️ Could not process this email.")

        print()
        time.sleep(8)  # wait 8 seconds between emails


if __name__ == "__main__":
    process_emails()