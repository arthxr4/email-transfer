from fastapi import FastAPI
from imbox import Imbox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

def clean_text(email_body):
    """Returns the first element of a list or an empty string if the list is empty."""
    return email_body[0] if email_body else ''

def send_email(server_address, sender_address, password, recipient_address, subject, text, html):
    """Sends an email using SMTP."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_address
    msg['To'] = recipient_address

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')
    
    msg.attach(part1)
    msg.attach(part2)

    with smtplib.SMTP(server_address) as s:
        s.starttls()  # Secure the connection
        s.login(sender_address, password)
        s.sendmail(sender_address, recipient_address, msg.as_string())

def fetch_email(imap_address, username, password, uid):
    """Fetches emails using the IMAP protocol."""
    with Imbox(imap_address, username=username, password=password, ssl=True) as imbox:
        messages = imbox.messages(uid=uid)  # Fetch specific UID
        for uid, message in messages:
            subject = message.subject
            text = clean_text(message.body['plain'])
            html = clean_text(message.body['html'])
            yield subject, text, html

@app.get("/transport-email")
def transport_email(imap_address: str, smtp_address: str, username: str, password: str, uid: str, recipient_address: str):
    """API endpoint to transfer emails from one account to another."""
    for subject, text, html in fetch_email(imap_address, username, password, uid):
        send_email(smtp_address, username, password, recipient_address, subject, text, html)
        return {"status": "Success", "message": "Email sent"}
    return {"status": "Failed", "message": "No email found or error sending email"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Remove this line if deploying on a platform like Heroku or Raleway
