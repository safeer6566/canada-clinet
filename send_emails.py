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

# Sheet tab name exact match from screenshot
TAB_NAME = "unsubscribed_members_export_670"

# Testing Limit: Only process 2 un-sent contacts per run
MAX_TEST_EMAILS = 2

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

        sheet = sheets_svc.spreadsheets()
        
        # Exact tab name ke saath Column A se D fetch karein
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"'{TAB_NAME}'!A:D").execute()
        rows = result.get('values', [])

        if not rows or len(rows) <= 1:
            print("❌ Sheet mein koi contact data nahi mila.")
            return

        print(f"🔹 Total rows found in sheet: {len(rows) - 1}")
        
        sent_count = 0

        # Row 1 Headers hain, Row 2 se start karenge
        for i in range(1, len(rows)):
            if sent_count >= MAX_TEST_EMAILS:
                print(f"🛑 Test Limit reached! ({MAX_TEST_EMAILS} emails sent). Stopping bot.")
                break

            row = rows[i]

            email = row[0].strip() if len(row) > 0 and row[0] else ""
            first_name = row[1].strip() if len(row) > 1 and row[1] else ""
            last_name = row[2].strip() if len(row) > 2 and row[2] else ""
            status = row[3].strip() if len(row) > 3 and row[3] else ""

            if not email:
                continue

            # Agar Status SENT ya OPENED ho toh skip karein
            if status.upper() in ["SENT", "OPENED"]:
                print(f"⏩ Skipped (Already Status: {status}): {email}")
                continue

            name = f"{first_name} {last_name}".strip() or "Valued Client"

            # Custom Email Body & Subject
            subject = "Testing Automation Bot"
            body = f"Hi {name},\n\nYeh aapki automated testing email hai. System testing run kar raha hai.\n\nBest regards,\nAutomation Bot"

            message = MIMEMultipart()
            message['to'] = email
            message['subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            try:
                # 1. Email Send
                gmail_svc.users().messages().send(
                    userId='me',
                    body={'raw': raw_message}
                ).execute()

                # 2. Update Column D (Merge Status) to "SENT"
                row_num = i + 1
                sheets_svc.spreadsheets().values().update(
                    spreadsheetId=SPREADSHEET_ID,
                    range=f"'{TAB_NAME}'!D{row_num}",
                    valueInputOption="RAW",
                    body={"values": [["SENT"]]}
                ).execute()

                sent_count += 1
                print(f"✅ [{sent_count}/{MAX_TEST_EMAILS}] Sent to {email} & marked SENT in sheet.")

            except Exception as send_err:
                print(f"❌ Failed to send to {email}: {send_err}")

            time.sleep(1)

        if sent_count == 0:
            print("ℹ️ Koi new un-sent email nahi mili. Pehle se saari SENT/OPENED hain.")

    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    send_and_track_emails()
