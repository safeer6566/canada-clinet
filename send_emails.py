import os
import time
import pandas as pd
import yagmail

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
SHEET_ID = os.environ.get("SHEET_ID")

sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def send_test_emails():
    if not EMAIL_USER or not EMAIL_PASSWORD:
        print("❌ Error: Secrets missing!")
        return

    clean_user = EMAIL_USER.strip()
    clean_password = EMAIL_PASSWORD.replace(" ", "").strip()

    try:
        # Sheet read karein
        df = pd.read_csv(sheet_url)
        df_test = df.head(3)

        # Yagmail client initialize karein
        yag = yagmail.SMTP(user=clean_user, password=clean_password)
        print("✅ Logged into Gmail via Yagmail successfully!")

        for index, row in df_test.iterrows():
            email = row.get("Email Address")
            first_name = row.get("First Name", "")
            last_name = row.get("Last Name", "")
            
            name = f"{first_name} {last_name}".strip() or "Client"

            if pd.notna(email) and str(email).strip():
                to_email = str(email).strip()
                subject = "Test Email from Bot"
                body = f"Hi {name},\n\nThis is a test email from our automated system!"

                try:
                    yag.send(to=to_email, subject=subject, contents=body)
                    print(f"✅ Email sent to {name} ({to_email})")
                except Exception as e:
                    print(f"❌ Failed to send to {to_email}: {e}")
                
                time.sleep(2)

        print("✅ All test emails processed.")

    except Exception as e:
        print(f"❌ Error occurred: {e}")

if __name__ == "__main__":
    send_test_emails()
