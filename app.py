from fastapi import FastAPI, HTTPException
from imbox import Imbox
import logging

app = FastAPI()

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.get("/fetch-email-by-uid")
def fetch_email_by_uid(imap_address: str, username: str, password: str, email_uid: str):
    """Endpoint to fetch email details by UID."""
    logging.info(f"Attempting to fetch email with UID: {email_uid}")
    try:
        with Imbox(imap_address, username=username, password=password, ssl=True) as imbox:
            # Fetch all messages
            all_messages = imbox.messages()
            for uid, message in all_messages:
                if uid == email_uid:
                    email_info = {
                        "uid": uid,
                        "from": [{"name": sender.get('name'), "email": sender.get('email')} for sender in message.sent_from],
                        "to": [{"name": recipient.get('name'), "email": recipient.get('email')} for recipient in message.sent_to],
                        "subject": message.subject,
                        "date": message.date,
                        "headers": message.headers,
                        "plain_body": message.body['plain'][0] if message.body['plain'] else "No plain text content available",
                        "html_body": message.body['html'][0] if message.body['html'] else "No HTML content available",
                        "attachments": [{"filename": attachment.get('filename')} for attachment in message.attachments]
                    }
                    return {"status": "success", "email": email_info}
            return {"status": "failure", "message": "No email found with the provided UID."}
    except Exception as e:
        logging.error("An error occurred while trying to fetch the email:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
