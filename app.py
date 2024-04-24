from fastapi import FastAPI, HTTPException
import imaplib
from email.parser import BytesParser

app = FastAPI()

def connect_to_imap(imap_address, username, password):
    try:
        mail = imaplib.IMAP4_SSL(imap_address)
        mail.login(username, password)
        mail.select('inbox')  # Sélectionner la boîte de réception
        return mail
    except imaplib.IMAP4.error as e:
        raise HTTPException(status_code=500, detail=f"IMAP login failed: {e}")

@app.get("/get-html-content/")
def get_html_content(imap_address: str, username: str, password: str, uid: str):
    """Endpoint to fetch the HTML content of an email by its UID."""
    mail = connect_to_imap(imap_address, username, password)
    try:
        result, data = mail.uid('fetch', uid, '(RFC822)')
        if result != 'OK' or not data[0]:
            raise HTTPException(status_code=404, detail="Email not found")

        raw_email = data[0][1]
        msg = BytesParser().parsebytes(raw_email)

        # Extraire le contenu HTML
        html_content = None
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/html':
                    html_content = part.get_payload(decode=True).decode(part.get_content_charset('iso-8859-1'), errors='replace')
                    break  # Arrête dès que le contenu HTML est trouvé
        else:
            if msg.get_content_type() == 'text/html':
                html_content = msg.get_payload(decode=True).decode(msg.get_content_charset('iso-8859-1'), errors='replace')

        return {"status": "success", "html_content": html_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        mail.logout()

# Pour exécuter l'API localement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
