from fastapi import FastAPI, HTTPException
from imbox import Imbox

app = FastAPI()

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
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
