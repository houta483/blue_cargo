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
from google_sheet import Google_Sheets


class Glucose():
    def click_sorted_button(self):
        count = 0
        webbrowser.open('https://www.libreview.com/dashboard')
        time.sleep(5)
        gui.click(x=1100, y=673, duration=2)
        time.sleep(5)

        while True:
            gui.moveTo(x=210, y=305, duration=2)
            gui.doubleClick()
            time.sleep(5)
            gui.moveTo(x=410, y=305, duration=2)
            gui.doubleClick()
            time.sleep(5)

            if count % 10 == 0:
                self.download_data()
                Google_Sheets(scopes=['https://www.googleapis.com/auth/spreadsheets'],
                              spreadsheet_id='1wwGhXxKS9dXEx6YM5p9qTRLtng1Rr6ASd-y07MCZaVs', sheet_range='Sheet1!A8:I1').main()
                time.sleep(5)
                gui.hotkey('command', 'r')
                time.sleep(5)

            count += 1

    def download_data(self):
        gui.moveTo(x=1346, y=852, duration=2)
        gui.doubleClick()
        time.sleep(5)
        gui.moveTo(x=956, y=576, duration=2)
        gui.click()
        time.sleep(5)


app = Glucose()

if __name__ == '__main__':
    # app.send_data()
    app.click_sorted_button()
