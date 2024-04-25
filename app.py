from fastapi import FastAPI, HTTPException
import imaplib
from email import message_from_bytes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

def connect_to_imap(imap_address, username, password):
    mail = imaplib.IMAP4_SSL(imap_address)
    try:
        mail.login(username, password)
        mail.select('inbox')
        return mail
    except imaplib.IMAP4.error as e:
        raise HTTPException(status_code=500, detail=f"IMAP login failed: {e}")

def connect_to_smtp(smtp_address, smtp_port, username, password):
    server = smtplib.SMTP_SSL(smtp_address, smtp_port)
    try:
        server.login(username, password)
        return server
    except smtplib.SMTPException as e:
        raise HTTPException(status_code=500, detail=f"SMTP login failed: {e}")

@app.post("/fetch-and-send-email-as-reply/")
def fetch_and_send_email_as_reply(imap_address: str, username: str, password: str, uid: str, smtp_address: str, smtp_port: int, receiver_addresses: str):
    """Endpoint to fetch an email by UID and send it as a reply with a simple formatted header to simulate a forwarded email."""
    mail = connect_to_imap(imap_address, username, password)
    try:
        result, data = mail.uid('fetch', uid, '(RFC822)')
        if result != 'OK' or not data[0]:
            raise HTTPException(status_code=404, detail="Email not found")

        raw_email = data[0][1]
        email_msg = message_from_bytes(raw_email)

        smtp_server = connect_to_smtp(smtp_address, smtp_port, username, password)
        forward_msg = MIMEMultipart()
        forward_msg['From'] = username
        forward_msg['To'] = receiver_addresses
        forward_msg['Subject'] = "Fwd: " + email_msg.get('Subject', '')
        forward_msg['Reply-To'] = email_msg.get('From')

        # Simple text formatting for forwarded message header
        header_content = f"""\
---------- Forwarded message ----------
From: {email_msg.get('From')}
Date: {email_msg.get('Date')}
To: {username}
Subject: {email_msg.get('Subject')}
"""

        # Attach the original email content below the header
        body_content = header_content
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == 'text/plain':
                    body_content += "\n" + part.get_payload(decode=True).decode(part.get_content_charset('utf-8'), errors='replace')
        else:
            if email_msg.get_content_type() == 'text/plain':
                body_content += "\n" + email_msg.get_payload(decode=True).decode(email_msg.get_content_charset('utf-8'), errors='replace')

        forward_msg.attach(MIMEText(body_content, 'plain'))

        smtp_server.send_message(forward_msg)
        smtp_server.quit()

        return {"status": "success", "message": "Email fetched and forwarded successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        mail.logout()

# To run the API locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
