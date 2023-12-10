import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage


def trigger_email(receiver_email, email_body):
    # set up the SMTP server
    smtp_server = "smtp-relay.sendinblue.com"
    smtp_port = 587
    smtp_username = "coolbrofhts@gmail.com"
    smtp_password = "a3mABR5XfTgwKNtO"

    # set up the email message
    sender_email = "coolbrofhts@gmail.com"
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = "AVISHKAR-23 NOTIFICATION"
    body = email_body
    message.attach(MIMEText(body, 'plain'))

    # send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        print("Email sent successfully!")
