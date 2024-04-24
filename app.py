from fastapi import FastAPI, HTTPException
from imbox import Imbox
import logging

app = FastAPI()

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.get("/fetch-email")
def fetch_email_content(imap_address: str, username: str, password: str, uid: str):
    """Endpoint to fetch the HTML content of an email by UID."""
    try:
        with Imbox(imap_address, username=username, password=password, ssl=True) as imbox:
            messages = imbox.messages(uid=uid)  # Fetch specific UID
            for uid, message in messages:
                html_content = message.body['html'][0] if message.body['html'] else "No HTML content available"
                return {"uid": uid, "html_content": html_content}
        return {"message": "Email with specified UID not found"}
    except Exception as e:
        logging.error("An error occurred while trying to fetch the email:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
