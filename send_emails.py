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

# Exact Tab Name from Google Sheet
TAB_NAME = "unsubscribed_members_export_670"

# Daily Limit set to 100 emails
MAX_DAILY_EMAILS = 100

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
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"'{TAB_NAME}'!A:D").execute()
        rows = result.get('values', [])

        if not rows or len(rows) <= 1:
            print("❌ Sheet mein koi contact data nahi mila.")
            return

        print(f"🔹 Total rows found in sheet: {len(rows) - 1}")
        
        sent_count = 0

        for i in range(1, len(rows)):
            if sent_count >= MAX_DAILY_EMAILS:
                print(f"🛑 Daily Limit reached! ({MAX_DAILY_EMAILS} emails sent). Stopping bot for today.")
                break

            row = rows[i]

            email = row[0].strip() if len(row) > 0 and row[0] else ""
            first_name = row[1].strip() if len(row) > 1 and row[1] else ""
            last_name = row[2].strip() if len(row) > 2 and row[2] else ""
            status = row[3].strip() if len(row) > 3 and row[3] else ""

            if not email:
                continue

            # Skip already processed contacts
            if status.upper() in ["SENT", "OPENED"]:
                print(f"⏩ Skipped (Already Status: {status}): {email}")
                continue

            # Handle Name: Agar First Name blank ho to greeting hi nahi aayegi
            full_name = f"{first_name} {last_name}".strip()
            if full_name:
                greeting_html = f'<h2 style="font-size: 22px; color: #1a1a1a; margin-top: 0;">Hi <strong>{full_name}</strong>,</h2>'
            else:
                greeting_html = ''

            subject = "High-Quality 3D Product Animation & Rendering"

            # Large Font & Clear Formatting (18px Text Size)
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
              <meta charset="utf-8">
            </head>
            <body style="font-family: Arial, sans-serif; font-size: 18px; line-height: 1.8; color: #222222; background-color: #f4f6f8; margin: 0; padding: 20px;">
              <div style="max-width: 650px; margin: 0 auto; background-color: #ffffff; padding: 35px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); border: 1px solid #dcdcdc;">
                
                {greeting_html}
                
                <p style="font-size: 18px;">I am a <strong>Professional 3D Artist</strong> specializing in Blender, and I help brands and online stores turn their products into premium, eye-catching 3D visuals or custom work related to 3D.</p>
                
                <h3 style="font-size: 20px; color: #0056b3; margin-top: 25px; margin-bottom: 12px;"><strong>My Services Include:</strong></h3>
                <ul style="font-size: 18px; padding-left: 25px; margin-top: 0; line-height: 2.0;">
                  <li><strong>3D Product Modeling</strong></li>
                  <li><strong>Photorealistic Product Rendering</strong> for Website / Amazon / E-commerce</li>
                  <li><strong>3D Product Animation</strong> (Product reveal, 360 rotation)</li>
                  <li><strong>NFT Collection Design & 3D Animation</strong></li>
                  <li><strong>3D Logo Animation & Mockups</strong></li>
                  <li><strong>Architectural Visualization</strong> (Interior / Exterior)</li>
                  <li><strong>3D Explainer Videos</strong></li>
                </ul>
                
                <div style="background-color: #eef6ff; border-left: 6px solid #0056b3; padding: 20px; margin: 25px 0; border-radius: 6px;">
                  <p style="margin: 0; color: #003366; font-size: 20px; font-weight: bold;">Free Sample Offer:</p>
                  <p style="margin: 8px 0 0 0; font-size: 18px; color: #111111;">I'd love to show you what I can do. I'm happy to create a <strong>free sample render</strong> of one of your products with no obligation, so you can see the quality for yourself before deciding anything.</p>
                </div>

                <div style="text-align: center; margin: 35px 0;">
                  <a href="https://wa.link/u4hb6v" style="background-color: #25D366; color: #ffffff; padding: 15px 30px; text-decoration: none; font-size: 20px; font-weight: bold; border-radius: 6px; display: inline-block;">Message on WhatsApp (+92 348 0639328)</a>
                </div>

                <p style="font-size: 18px;">You can also check out my portfolio here: <a href="https://www.fiverr.com/safeer5d" style="color: #0056b3; font-weight: bold; text-decoration: underline;">Fiverr Portfolio</a></p>
                
                <p style="font-size: 18px;">Looking forward to working with you!</p>
                
                <hr style="border: 0; border-top: 2px solid #eeeeee; margin-top: 35px; margin-bottom: 25px;">
                
                <p style="margin-bottom: 0; font-size: 18px;">
                  <strong>Best regards,</strong><br>
                  <span style="font-size: 20px; font-weight: bold; color: #1a1a1a;">Safeer</span><br>
                  <span style="color: #555555; font-weight: bold;">3D Artist | Blender Specialist</span>
                </p>
              </div>
            </body>
            </html>
            """

            message = MIMEMultipart("alternative")
            message['to'] = email
            message['subject'] = subject

            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            try:
                # 1. Send Email
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
                print(f"✅ [{sent_count}/{MAX_DAILY_EMAILS}] Sent to {email} & marked SENT in sheet.")

            except Exception as send_err:
                print(f"❌ Failed to send to {email}: {send_err}")

            time.sleep(1)

        if sent_count == 0:
            print("ℹ️ No un-sent emails found. All rows are already SENT or OPENED.")

    except Exception as e:
        print(f"❌ Execution Error: {e}")

if __name__ == "__main__":
    send_and_track_emails()
