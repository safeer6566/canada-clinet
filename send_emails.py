import os
import base64
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

CLIENT_ID = os.environ.get("GMAIL_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GMAIL_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("GMAIL_REFRESH_TOKEN")
SPREADSHEET_ID = os.environ.get("SHEET_ID")

def get_services():
    creds = Credentials(
        token=None,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        token_uri="https://oauth2.googleapis.com/token"
    )
    gmail_service = build('gmail', 'v1', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    return gmail_service, sheets_service

def send_and_track_emails():
    try:
        gmail_svc, sheets_svc = get_services()

        # Sheet 1 se data fetch karein
        sheet = sheets_svc.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Sheet1!A:D").execute()
        rows = result.get('values', [])

        if not rows:
            print("❌ Sheet mein koi data nahi mila.")
            return

        print(f"🔹 Total rows in sheet: {len(rows) - 1}")

        # Row 1 header hai, isliye loop 1 se start hoga
        for i in range(1, len(rows)):
            row = rows[i]
            
            # Data extract karein
            email = row[0].strip() if len(row) > 0 and row[0] else ""
            first_name = row[1].strip() if len(row) > 1 and row[1] else ""
            last_name = row[2].strip() if len(row) > 2 and row[2] else ""
            status = row[3].strip() if len(row) > 3 and row[3] else ""

            # Skip agar email empty ho ya pehle se SENT likha ho
            if not email:
                continue

            if status.upper() == "SENT":
                print(f"⏩ Skipped (Already Sent): {email}")
                continue

            name = f"{first_name} {last_name}".strip() or "Valued Client"

            # Custom Email Body
            subject = "Testing Email Automation"
            body = f"Hi {name},\n\nYeh aik test email hai. Hope you are doing well!\n\nBest regards,\nOur Team"

            # Email Setup
            message = MIMEMultipart()
            message['to'] = email
            message['subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            try:
                # 1. Email Send Karein
                gmail_svc.users().messages().send(
                    userId='me',
                    body={'raw': raw_message}
                ).execute()

                # 2. Sheet mein Column D par "SENT" Update Karein
                row_num = i + 1
                sheets_svc.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"Sheet1!D{row_num}",
                    valueInputOption="RAW",
                    body={"values": [["SENT"]]}
                ).execute()

                print(f"✅ Email Sent & Marked 'SENT' in Sheet: {email}")

            except Exception as send_err:
                print(f"❌ Failed to send to {email}: {send_err}")

            time.sleep(1) # API rate limit safe rakhne ke liye 1 second delay

    except Exception as e:
        print(f"❌ Script Error: {e}")

if __name__ == "__main__":
    send_and_track_emails()
