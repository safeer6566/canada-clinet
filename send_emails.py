import os
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
SHEET_ID = os.environ.get("SHEET_ID")

# Google Sheet CSV URL
sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def send_test_emails():
    try:
        # Sheet ka data read karein
        df = pd.read_csv(sheet_url)
        
        # Sirf pehle 3 clients select karein
        df_test = df.head(3)
        
        # App Password se spaces remove karein
        clean_password = EMAIL_PASSWORD.replace(" ", "") if EMAIL_PASSWORD else ""

        # Port 465 (SSL) connection use karein
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(EMAIL_USER, clean_password)
        print("✅ Connected to Gmail SSL SMTP server successfully.")

        for index, row in df_test.iterrows():
            email = row.get("Email Address")
            first_name = row.get("First Name", "")
            last_name = row.get("Last Name", "")
            
            # Name combine karein
            name = f"{first_name} {last_name}".strip()
            if not name:
                name = "Client"

            if pd.notna(email) and str(email).strip():
                to_email = str(email).strip()
                
                subject = "Test Email from Bot"
                body = f"Hi {name},\n\nThis is a test email from our automated system!"

                msg = MIMEMultipart()
                msg['From'] = EMAIL_USER
                msg['To'] = to_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                try:
                    server.sendmail(EMAIL_USER, to_email, msg.as_string())
                    print(f"✅ Email sent to {name} ({to_email})")
                except Exception as e:
                    print(f"❌ Failed to send email to {to_email}: {e}")
                
                # 2 Seconds delay
                time.sleep(2)

        # Connection close karein
        server.quit()
        print("✅ Finished sending emails.")

    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    send_test_emails()
