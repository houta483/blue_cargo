from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import csv


class Google_Sheets():
    def __init__(self, scopes, spreadsheet_id, sheet_range):
        self.scopes = scopes
        self.spreadsheet_id = spreadsheet_id
        self.sheet_range = sheet_range

    def main(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('sheets', 'v4', credentials=creds)

        resource = {
            "majorDimension": "ROWS",
            "values": self.parse_csv_data()
        }

        service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=self.sheet_range,
            body=resource,
            valueInputOption="USER_ENTERED"
        ).execute()
        self.remove_used_files()

    def parse_csv_data(self):
        csv_data = []
        for file in os.listdir(""):
            if file.startswith("LV_StevenHoughton"):
                filename = f"/Users/Tanner/Downloads/{file}"
                print("This is the file we are looking for")
            else:
                print('there is not a file')

        with open(filename) as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            for data in csvReader:
                csv_data.append(data)
            return csv_data

    def remove_used_files(self):
        for file in os.listdir("/Users/Tanner/Downloads"):
            if file.startswith("LV_StevenHoughton"):
                filename = f"/Users/Tanner/Downloads/{file}"
                os.remove(filename)
                print('Removed File')
            else:
                print('there is not a file')
