import email
import smtplib
import ssl
from decouple import config
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from random import random
from random import uniform
import webbrowser
import pyautogui as gui
import rumps
import time
import threading
import os


def send_data(self):
    subject = "Automated Retrieval of Glucose Data"
    body = "Please find glucose data attached"
    sender_email = "houghtonglucose@gmail.com"
    receiver_email = "stevenhoughtonjr@gmail.com"
    password = config('GLUCOSE_PASSWORD')

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email
    message.attach(MIMEText(body, "plain"))

    for file in os.listdir("/Users/Tanner/Downloads"):
        if file.startswith("LV_StevenHoughton"):
            filename = f"/Users/Tanner/Downloads/{file}"
            print(filename)
        else:
            print('there is not a file')

    with open(filename, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    message.attach(part)
    text = message.as_string()
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)

    for file in os.listdir("/Users/Tanner/Downloads"):
        if file.startswith("LV_StevenHoughton"):
            filename = f"/Users/Tanner/Downloads/{file}"
            os.remove(filename)
            print('Removed File')
        else:
            print('there is not a file')
