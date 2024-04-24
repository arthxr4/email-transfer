from fastapi import FastAPI
from imbox import Imbox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

def c(l):
    if len(l) == 0:
        return ''
    else:
        return l[0]

def send_email(server_address, sender_address, password, recipient_address, subject, text, html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_address
    msg['To'] = recipient_address

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    msg.attach(part1)
    msg.attach(part2)

    s = smtplib.SMTP(server_address)
    s.starttls()  # Correction ici (était 'mail.starttls()', ce qui est incorrect)
    
    s.login(sender_address, password)
    s.sendmail(sender_address, recipient_address, msg.as_string())
    s.quit()

def fetch_email(server_address, username, password, uid):
    with Imbox(server_address, username=username, password=password, ssl=True, ssl_context=None, starttls=False) as imbox:
        for uid, message in imbox.messages():
            plain_body = c(message.body['plain'])
            html_body = c(message.body['html'])
            yield message.subject, plain_body, html_body

@app.get("/transport-email")
async def main(server_address_imap, server_address_smtp, username, password, uid, recipient_address):
    print("Init")
    for subject, text, html in fetch_email(server_address_imap, username, password, uid):
        print("Sending email with HTML content:", html)
        send_email(server_address_smtp, username, password, recipient_address, subject, text, html)
        return {"status": "Success", "message": "Email sent"}

    return {"status": "Failed", "message": "No email found or error sending email"}

# Note: Ne pas exécuter app.run() directement ici si vous déployez sur un serveur
# Utilisez plutôt une commande uvicorn pour démarrer le serveur dans votre environnement de déploiement
