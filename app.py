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
def fetch_and_send_email_as_reply(imap_address: str, username: str, password: str, uid: str, smtp_address: str, smtp_port: int, receiver_address: str, personal_message: str):
    """Endpoint to fetch an email by UID and send it as a reply with a personal message to another email address."""
    mail = connect_to_imap(imap_address, username, password)
    try:
        result, data = mail.uid('fetch', uid, '(RFC822)')
        if result != 'OK' or not data[0]:
            raise HTTPException(status_code=404, detail="Email not found")

        raw_email = data[0][1]
        email_msg = message_from_bytes(raw_email)
        content = None

        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == 'text/plain':
                    content = part.get_payload(decode=True).decode(part.get_content_charset('utf-8') or 'utf-8')
                    break  # Assumes that the first text/plain part is the main content
        else:
            content = email_msg.get_payload(decode=True).decode(email_msg.get_content_charset('utf-8') or 'utf-8')

        if content is None:
            content = "No readable content was found in the email."

        smtp_server = connect_to_smtp(smtp_address, smtp_port, username, password)
        forward_msg = MIMEMultipart("alternative")
        forward_msg['From'] = username
        forward_msg['To'] = receiver_address
        forward_msg['Subject'] = "RE: " + email_msg.get('Subject', '')
        forward_msg['In-Reply-To'] = email_msg.get('Message-ID')
        forward_msg['References'] = email_msg.get('References', email_msg.get('Message-ID'))

        personal_msg_part = MIMEText(f"test: {personal_message}\n\n", 'plain')
        forward_msg.attach(personal_msg_part)

        quoted_content = "\n".join([f"> {line}" for line in content.splitlines()])
        quoted_part = MIMEText(quoted_content, 'plain')
        forward_msg.attach(quoted_part)

        smtp_server.send_message(forward_msg)
        smtp_server.quit()

        return {"status": "success", "message": "Email fetched and replied with personal message successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        mail.logout()

# To run the API locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
