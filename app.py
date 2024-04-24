from fastapi import FastAPI, HTTPException
import imaplib
from email.parser import BytesParser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
    server = smtplib.SMTP(smtp_address, smtp_port)
    server.starttls()
    try:
        server.login(username, password)
        return server
    except smtplib.SMTPException as e:
        raise HTTPException(status_code=500, detail=f"SMTP login failed: {e}")

@app.get("/transfer-email/")
def transfer_email(imap_address: str, username: str, password: str, smtp_address: str, smtp_port: int, uid: str, receiver_address: str):
    """Endpoint to fetch and transfer an email by its UID."""
    mail = connect_to_imap(imap_address, username, password)
    smtp_server = connect_to_smtp(smtp_address, smtp_port, username, password)
    try:
        result, data = mail.uid('fetch', uid, '(RFC822)')
        if result != 'OK' or not data[0]:
            raise HTTPException(status_code=404, detail="Email not found")

        raw_email = data[0][1]
        msg = BytesParser().parsebytes(raw_email)
        html_content = None
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                html_content = part.get_payload(decode=True).decode(part.get_content_charset('iso-8859-1'), errors='replace')
                break

        # Prepare email to send
        forward_msg = MIMEMultipart()
        forward_msg['From'] = username
        forward_msg['To'] = receiver_address
        forward_msg['Subject'] = "FWD: " + msg.get('Subject', '')
        forward_msg.attach(MIMEText(html_content, 'html'))

        # Send email
        smtp_server.sendmail(username, receiver_address, forward_msg.as_string())
        return {"status": "success", "message": "Email forwarded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        mail.logout()
        smtp_server.quit()

# Pour exécuter l'API localement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
