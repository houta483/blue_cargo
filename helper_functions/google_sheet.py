from __future__ import print_function
from collections import OrderedDict
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import csv


class Google_Sheets:
    def __init__(self, scopes):
        self.scopes = scopes
        self.credentials = None

    def get_credentials(self):
        if os.path.exists("config/token.pickle"):
            with open("config/token.pickle", "rb") as token:
                self.credentials = pickle.load(token)

        if not self.credentials or not self.credentials.valid:
            if (
                self.credentials
                and self.credentials.expired
                and self.credentials.refresh_token
            ):
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "config/credentials.json", self.scopes
                )
                self.credentials = flow.run_local_server(port=0)
            with open("config/token.pickle", "wb") as token:
                pickle.dump(self.credentials, token)
