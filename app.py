from fastapi import FastAPI, HTTPException
import imaplib
import email
from email.parser import BytesParser
import logging

app = FastAPI()

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_imap(imap_address, username, password):
    mail = imaplib.IMAP4_SSL(imap_address)
    mail.login(username, password)
    mail.select('inbox')  # Vous pouvez ajuster ceci si nécessaire
    return mail

@app.get("/fetch-email-thread")
def fetch_email_thread(imap_address: str, username: str, password: str, email_uid: str):
    """Endpoint to fetch email thread by UID."""
    try:
        mail = connect_to_imap(imap_address, username, password)
        result, data = mail.uid('fetch', email_uid, '(RFC822)')
        if result != 'OK':
            return {"status": "failure", "message": "Email not found"}

        raw_email = data[0][1]
        msg = BytesParser().parsebytes(raw_email)

        thread_emails = []
        email_data = {
            "uid": email_uid,
            "from": msg.get('From'),
            "subject": msg.get('Subject'),
            "date": msg.get('Date'),
            "body_html": msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        }
        thread_emails.append(email_data)

        # Extract references and in-reply-to to find related emails
        references = msg.get('References', '').split() + msg.get('In-Reply-To', '').split()
        unique_ids = set(references)
        for ref_id in unique_ids:
            search_result, search_data = mail.uid('search', None, f'(HEADER Message-ID "{ref_id}")')
            if search_result == 'OK':
                for ref_uid in search_data[0].split():
                    result, data = mail.uid('fetch', ref_uid, '(RFC822)')
                    if result == 'OK':
                        ref_email = BytesParser().parsebytes(data[0][1])
                        email_data = {
                            "uid": ref_uid.decode('utf-8'),
                            "from": ref_email.get('From'),
                            "subject": ref_email.get('Subject'),
                            "date": ref_email.get('Date'),
                            "body_html": ref_email.get_payload(decode=True).decode('utf-8', errors='ignore')
                        }
                        thread_emails.append(email_data)

        if not thread_emails:
            return {"status": "failure", "message": "No email found with the provided UID."}
        
        return {"status": "success", "thread": thread_emails}
    except Exception as e:
        logging.error("An error occurred while trying to fetch the email thread:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

