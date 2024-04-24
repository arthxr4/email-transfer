from fastapi import FastAPI, HTTPException
from imbox import Imbox
import logging

app = FastAPI()

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.get("/fetch-email-html")
def fetch_email_html(imap_address: str, username: str, password: str, uid: str):
    """Endpoint to fetch the HTML content of an email by UID."""
    try:
        with Imbox(imap_address, username=username, password=password, ssl=True) as imbox:
            # Fetch email by UID
            status, messages = imbox.messages(uid=uid)
            if not messages:
                return {"status": "failure", "message": "No email found with the provided UID."}
            for uid, message in messages:
                html_content = message.body['html'][0] if message.body['html'] else "No HTML content available"
                return {"status": "success", "uid": uid, "html_content": html_content}
    except Exception as e:
        logging.error("An error occurred while trying to fetch the email:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
