from imbox import Imbox
from fastapi import FastAPI
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = FastAPI()

def c(l):
    if len(l)==0:
        return ''
    else:
        return l[0]


def send_email(server_address, sender_address, password, recipient_address, subject, text, html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_address
    msg['To'] = recipient_address

    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(text, 'html')
    
    msg.attach(part1)
    msg.attach(part2)

    s = smtplib.SMTP(server_address)
    mail.starttls()
    
    s.login(sender_address, password)
    s.sendmail(sender_address, recipient_address, msg.as_string())
    s.quit()

def fetch_email(sender_address, username, password, uid):
    with Imbox(sender_address, username=username, password=password, ssl=True, ssl_context=None, starttls=False) as imbox:   
        for d, message in imbox.fetch_by_uid(uid):
            print(message.body)
            yield message.subject,c(message.body['plain']),c(message.body['html'])

            
@app.get("/transport-email")
def main(server_address_imap, server_address_smtp, username, password, uid, recipient_address):
    print("Init")
    for subject, text, html in fetch_email(server_address_imap, username, password, uid):
      print(html)
        send_email(server_address_smtp, username, password, recipient_address, subject, text, html)
        return {"status": "Success", "message": "Email sent"}

    return {"status": "Failed", "message": "No email found or error sending email"}

app.run()