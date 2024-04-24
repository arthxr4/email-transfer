from fastapi import FastAPI, HTTPException
from imbox import Imbox
import logging

app = FastAPI()

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.get("/fetch-emails-from")
def fetch_emails_from(imap_address: str, username: str, password: str, sender_email: str):
    """Endpoint to fetch emails sent from a specific email address."""
    try:
        with Imbox(imap_address, username=username, password=password, ssl=True) as imbox:
            # Fetch emails sent from a specific email address
            messages = imbox.messages(sent_from=sender_email)
            emails = []
            for uid, message in messages:
                email_info = {
                    "uid": uid,
                    "from": message.sent_from,
                    "to": message.sent_to,
                    "subject": message.subject,
                    "date": message.date,
                    "plain_body": message.body['plain'][0] if message.body['plain'] else "No plain text content available",
                    "html_body": message.body['html'][0] if message.body['html'] else "No HTML content available"
                }
                emails.append(email_info)

            if emails:
                return {"status": "success", "emails": emails}
            else:
                return {"status": "failure", "message": "No emails found from the specified sender."}
    except Exception as e:
        logging.error("An error occurred while trying to fetch emails:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
