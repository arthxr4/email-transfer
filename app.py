from fastapi import FastAPI, HTTPException
from imbox import Imbox
import logging

app = FastAPI()

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.get("/fetch-latest-email")
def fetch_latest_email(imap_address: str, username: str, password: str):
    """Endpoint to fetch the latest email received."""
    try:
        with Imbox(imap_address, username=username, password=password, ssl=True) as imbox:
            # Fetch all messages and sort by date in descending order to get the latest
            messages = imbox.messages(sort_by='date', reversed=True)
            for uid, message in messages:
                # Extracting detailed information from the latest email
                email_data = {
                    "uid": uid,
                    "from": message.sent_from,
                    "to": message.sent_to,
                    "subject": message.subject,
                    "date": message.date,
                    "headers": message.headers,
                    "html_body": message.body['html'][0] if message.body['html'] else "No HTML content available",
                    "text_body": message.body['plain'][0] if message.body['plain'] else "No text content available"
                }
                return {"status": "success", "email": email_data}
            return {"status": "failure", "message": "No emails found."}
    except Exception as e:
        logging.error("An error occurred while trying to fetch the latest email:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
