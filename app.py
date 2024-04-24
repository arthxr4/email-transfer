from fastapi import FastAPI, HTTPException
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

@app.post("/send-email/")
def send_email(smtp_address: str, smtp_port: int, username: str, password: str, receiver_address: str):
    """Endpoint to send a simple 'Hello World' email."""
    try:
        # Configuration du serveur SMTP avec SSL
        server = smtplib.SMTP_SSL(smtp_address, smtp_port)
        server.login(username, password)  # Connexion au serveur SMTP

        # Création du message
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = receiver_address
        msg['Subject'] = "Hello from FastAPI"
        body = "Hello World"
        msg.attach(MIMEText(body, 'plain'))

        # Envoi de l'email
        server.send_message(msg)
        server.quit()
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Pour exécuter l'API localement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
