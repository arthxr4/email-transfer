from fastapi import FastAPI, HTTPException
import imaplib

app = FastAPI()

def connect_to_imap(imap_address, username, password):
    try:
        # Connexion au serveur IMAP en utilisant SSL
        mail = imaplib.IMAP4_SSL(imap_address)
        # Authentification
        mail.login(username, password)
        return mail
    except imaplib.IMAP4.error as e:
        raise HTTPException(status_code=500, detail=f"IMAP login failed: {e}")

@app.get("/connect-imap/")
def connect_imap_endpoint(imap_address: str, username: str, password: str):
    """Endpoint to connect to IMAP server and list mailboxes."""
    mail = connect_to_imap(imap_address, username, password)
    # Liste tous les dossiers/boîtes aux lettres dans le compte
    status, mailboxes = mail.list()
    if status == 'OK':
        mailbox_list = [mailbox.decode('utf-8') for mailbox in mailboxes]
        return {"status": "success", "mailboxes": mailbox_list}
    else:
        raise HTTPException(status_code=500, detail="Failed to list mailboxes.")
