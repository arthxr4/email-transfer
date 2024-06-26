from fastapi import FastAPI, HTTPException
import imaplib
from email.parser import BytesParser
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

@app.post("/fetch-and-send-email/")
def fetch_and_send_email(imap_address: str, username: str, password: str, uid: str, smtp_address: str, smtp_port: int, receiver_address: str):
    """Endpoint to fetch an HTML email content by UID and send it to another email address."""
    # Connect to IMAP and fetch the email
    mail = connect_to_imap(imap_address, username, password)
    try:
        result, data = mail.uid('fetch', uid, '(RFC822)')
        if result != 'OK' or not data[0]:
            raise HTTPException(status_code=404, detail="Email not found")

        raw_email = data[0][1]
        msg = BytesParser().parsebytes(raw_email)

        html_content = None
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/html':
                    html_content = part.get_payload(decode=True).decode(part.get_content_charset('iso-8859-1'), errors='replace')
                    break
        else:
            if msg.get_content_type() == 'text/html':
                html_content = msg.get_payload(decode=True).decode(msg.get_content_charset('iso-8859-1'), errors='replace')

        # Connect to SMTP and send the email
        smtp_server = connect_to_smtp(smtp_address, smtp_port, username, password)
        forward_msg = MIMEMultipart()
        forward_msg['From'] = username
        forward_msg['To'] = receiver_address
        forward_msg['Subject'] = "FWD: " + msg.get('Subject', '')
        forward_msg.attach(MIMEText(html_content, 'html'))
        smtp_server.send_message(forward_msg)
        smtp_server.quit()

        return {"status": "success", "message": "Email fetched and forwarded successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        mail.logout()

# Pour exécuter l'API localement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
