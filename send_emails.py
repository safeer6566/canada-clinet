import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
SHEET_ID = os.environ.get("SHEET_ID")

# Google Sheet CSV URL
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
        server.login(EMAIL_USER, EMAIL_PASSWORD.replace(" ", ""))
        server.sendmail(EMAIL_USER, to_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {client_name} ({to_email})")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")

if __name__ == "__main__":
    try:
        # Sheet madhun data read kara
        df = pd.read_csv(sheet_url)
        
        # Google sheet madhil exact column headers
        for index, row in df.iterrows():
            email = row.get("Email Address")
            first_name = row.get("First Name", "")
            last_name = row.get("Last Name", "")
            
            # Nav ekatra kara
            name = f"{first_name} {last_name}".strip()
            if not name:
                name = "Client"

            if pd.notna(email) and str(email).strip():
                send_email(str(email).strip(), name)
                
    except Exception as e:
        print(f"❌ Google Sheet read kartana error aala: {e}")
