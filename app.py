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

@app.post("/forward-email/")
async def forward_email(imap_address: str, username: str, password: str, uid: str, smtp_address: str, smtp_port: int, receiver_address: str):
    """Endpoint to fetch an email by UID and forward it to another email address, ensuring the original sender's address is used in Reply-To for history parts."""
    mail = connect_to_imap(imap_address, username, password)
    try:
        result, data = mail.uid('fetch', uid, '(RFC822)')
        if result != 'OK' or not data[0]:
            raise HTTPException(status_code=404, detail="Email not found")

        raw_email = data[0][1]
        email_msg = message_from_bytes(raw_email)

        smtp_server = connect_to_smtp(smtp_address, smtp_port, username, password)
        forward_msg = MIMEMultipart("alternative")
        forward_msg['From'] = username  # Use your own email address here
        forward_msg['To'] = receiver_address
        forward_msg['Subject'] = "Fwd: " + email_msg.get('Subject', '')
        forward_msg['Reply-To'] = username  # Replies to this email go to your address

        # Prepare and attach the original email content as quoted history
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == 'text/html':
                    html_content = part.get_payload(decode=True).decode(part.get_content_charset('iso-8859-1'), errors='replace')
                    quoted_html = f"<blockquote><small>From: {email_msg.get('From')}<br>Reply-To: {email_msg.get('From')}</small><br>{html_content}</blockquote>"
                    forward_msg.attach(MIMEText(quoted_html, 'html'))
        else:
            html_content = email_msg.get_payload(decode=True).decode(email_msg.get_content_charset('iso-8859-1'), errors='replace')
            quoted_html = f"<blockquote><small>From: {email_msg.get('From')}<br>Reply-To: {email_msg.get('From')}</small><br>{html_content}</blockquote>"
            forward_msg.attach(MIMEText(quoted_html, 'html'))

        smtp_server.send_message(forward_msg)
        smtp_server.quit()

        return {"status": "success", "message": "Email forwarded successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        mail.logout()

# To run the API locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
