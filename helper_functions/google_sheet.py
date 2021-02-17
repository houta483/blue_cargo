from __future__ import print_function

import os.path
import pickle
import csv

from collections import OrderedDict
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from helper_functions import google_sheet


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

    def upload_data(self):
        google_sheets_module = google_sheet.Google_Sheets(
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )

        google_sheets_module.get_credentials()

        service = build("sheets", "v4", credentials=google_sheets_module.credentials)

        with open("data.csv") as csv_data_file:
            csv_data = []
            csv_reader = csv.reader(csv_data_file)

            for line in csv_reader:
                csv_data.append(line)

            content = csv_data

        resource = {"majorDimension": "ROWS", "values": content}

        service.spreadsheets().values().append(
            spreadsheetId=os.environ["SPREADSHEET_ID"],
            range="Table_Metrics!A:S",
            body=resource,
            valueInputOption="USER_ENTERED",
        ).execute()

    def clean_up(self):
        print("final clean_up")
        os.remove("data.csv")
