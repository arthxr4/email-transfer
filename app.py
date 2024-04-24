from fastapi import FastAPI, HTTPException
import imaplib
from email import policy
from email.parser import BytesParser

app = FastAPI()

def connect_to_imap(imap_address, username, password):
    try:
        mail = imaplib.IMAP4_SSL(imap_address)
        mail.login(username, password)
        mail.select('inbox')
        return mail
    except imaplib.IMAP4.error as e:
        raise HTTPException(status_code=500, detail=f"IMAP login failed: {e}")

@app.get("/get-email/")
def get_email(imap_address: str, username: str, password: str, uid: str):
    """Endpoint to fetch an email by its UID."""
    mail = connect_to_imap(imap_address, username, password)
    try:
        result, data = mail.uid('fetch', uid, '(RFC822)')
        if result != 'OK' or not data[0]:
            raise HTTPException(status_code=404, detail="Email not found")

        raw_email = data[0][1]
        msg = BytesParser(policy=policy.default).parsebytes(raw_email)

        body_text = None
        body_html = None
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = part.get("Content-Disposition")
                if content_type == 'text/plain' and 'attachment' not in content_disposition:
                    body_text = part.get_payload(decode=True).decode(part.get_content_charset(), errors='replace')
                elif content_type == 'text/html' and 'attachment' not in content_disposition:
                    body_html = part.get_payload(decode=True).decode(part.get_content_charset(), errors='replace')
        else:
            # Handle singlepart messages
            if msg.get_content_type() == 'text/plain':
                body_text = msg.get_payload(decode=True).decode(msg.get_content_charset(), errors='replace')
            elif msg.get_content_type() == 'text/html':
                body_html = msg.get_payload(decode=True).decode(msg.get_content_charset(), errors='replace')

        email_details = {
            "from": msg.get('From'),
            "to": msg.get('To'),
            "subject": msg.get('Subject'),
            "date": msg.get('Date'),
            "body_text": body_text,
            "body_html": body_html
        }
        return {"status": "success", "email": email_details}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        mail.logout()

# Pour exécuter l'API localement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
