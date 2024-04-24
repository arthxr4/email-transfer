from fastapi import FastAPI, HTTPException
from imbox import Imbox
import logging

app = FastAPI()

# Configurer le logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.get("/test-imap-connection")
def test_imap_connection(imap_address: str, username: str, password: str):
    """Endpoint to test IMAP connection."""
    try:
        with Imbox(imap_address, username=username, password=password, ssl=True) as imbox:
            if imbox.connection:
                return {"status": "success", "message": "Successfully connected to the IMAP server."}
            else:
                return {"status": "failure", "message": "Failed to connect to the IMAP server."}
    except Exception as e:
        logging.error("An error occurred while trying to connect to the IMAP server:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
