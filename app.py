from fastapi import FastAPI, HTTPException
from imbox import Imbox
import logging

app = FastAPI()

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.get("/fetch-email-thread")
def fetch_email_thread(imap_address: str, username: str, password: str, email_uid: str):
    """Endpoint to fetch email thread by UID."""
    try:
        with Imbox(imap_address, username=username, password=password, ssl=True) as imbox:
            messages = imbox.messages(uid__range=f"{email_uid}:{email_uid}")
            thread_emails = []
            for uid, message in messages:
                email_data = {
                    "uid": uid,
                    "from": message.sent_from,
                    "subject": message.subject,
                    "date": message.date,
                    "body_html": message.body.get('html', '')  # Récupérer le contenu HTML du corps de l'email
                }
                thread_emails.append(email_data)

                # Tentative de récupération des emails liés
                if 'in-reply-to' in message.headers:
                    related_uid = message.headers['in-reply-to']
                    related_messages = imbox.messages(uid__range=f"{related_uid}:{related_uid}")
                    for rel_uid, rel_message in related_messages:
                        email_data = {
                            "uid": rel_uid,
                            "from": rel_message.sent_from,
                            "subject": rel_message.subject,
                            "date": rel_message.date,
                            "body_html": rel_message.body.get('html', '')  # Récupérer le contenu HTML du corps de l'email
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
