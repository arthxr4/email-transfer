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

@app.post("/fetch-and-send-email-as-reply/")
def fetch_and_send_email_as_reply(imap_address: str, username: str, password: str, uid: str, smtp_address: str, smtp_port: int, receiver_address: str, personal_message: str):
    """Endpoint to fetch an HTML email content by UID and send it as a reply with a personal message to another email address."""
    mail = connect_to_imap(imap_address, username, password)
    try:
        result, data = mail.uid('fetch', uid, '(RFC822)')
        if result != 'OK' or not data[0]:
            raise HTTPException(status_code=404, detail="Email not found")

        raw_email = data[0][1]
        msg = BytesParser().parsebytes(raw_email)

        # Setup the email structure
        smtp_server = connect_to_smtp(smtp_address, smtp_port, username, password)
        forward_msg = MIMEMultipart("mixed")
        forward_msg['From'] = username
        forward_msg['To'] = receiver_address
        forward_msg['Subject'] = "RE: " + msg.get('Subject', '')
        forward_msg['In-Reply-To'] = msg.get('Message-ID')
        forward_msg['References'] = msg.get('References', '')

        # Creating a personal message part
        personal_msg_part = MIMEText(f"test: {personal_message}\n\n", 'plain')
        forward_msg.attach(personal_msg_part)

        # Creating a copy of the original message part
        original_msg_part = MIMEText(msg.get_payload(decode=True), 'html')
        forward_msg.attach(original_msg_part)

        # Sending the email
        smtp_server.send_message(forward_msg)
        smtp_server.quit()

        return {"status": "success", "message": "Email fetched and replied with personal message successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        mail.logout()

# Pour exécuter l'API localement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
