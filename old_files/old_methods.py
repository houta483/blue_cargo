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


def currentLocation(self):
    currentX, currentY = gui.position()
    coordinates = [currentX, currentY]
    return coordinates


def glucose_stay_actice(self):
    self.iterations = 0
    while (self.iterations < 1000):
        time.sleep((uniform(0, 10)))
        initialX, initialY = self.currentLocation()

        gui.moveRel(random() * uniform(0, 100), random()
                    * uniform(0, 100), duration=uniform(0, 10))
        time.sleep((uniform(0, 10)))
        gui.moveRel(random() * uniform(-100, 0), random()
                    * uniform(-100, 0), duration=uniform(0, 10))
        time.sleep((uniform(0, 10)))
        gui.moveRel(random() * uniform(0, 100), random()
                    * uniform(0, 100), duration=uniform(0, 10))
        time.sleep((uniform(0, 10)))
        gui.moveRel(random() * uniform(-100, 0), random()
                    * uniform(-100, 0), duration=uniform(0, 10))
        time.sleep((uniform(0, 10)))

        gui.moveTo(initialX, initialY)

        self.iterations += 1
