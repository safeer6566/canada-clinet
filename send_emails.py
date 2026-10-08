import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
SHEET_ID = os.environ.get("SHEET_ID")

# Google Sheet URL (CSV Format)
sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def send_email(to_email, client_name):
    subject = "Greeting from Our Team"
    body = f"Hi {client_name},\n\nThank you for reaching out. We are glad to connect with you!"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        # Spaces remove kar ke login karein
        server.login(EMAIL_USER, EMAIL_PASSWORD.replace(" ", ""))
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {client_name} ({to_email})")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")

if __name__ == "__main__":
    try:
        df = pd.read_csv(sheet_url)
        
        # Check karein ke Name aur Email column maujood hain
        for index, row in df.iterrows():
            email = row.get("Email")
            name = row.get("Name", "Client")
            
            if pd.notna(email):
                send_email(str(email).strip(), str(name).strip())
    except Exception as e:
        print(f"❌ Google Sheet read karne mein error aaya: {e}")
