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
        if os.path.exists('config/token.pickle'):
            with open('config/token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'config/credentials.json', self.scopes)
                creds = flow.run_local_server(port=0)
            with open('config/token.pickle', 'wb') as token:
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

    def parse_csv_data(self):
        csv_data = []
        for final_csv_data_file in os.listdir('./final_csv_data'):
            file_path = os.path.join('./final_csv_data', final_csv_data_file)

            with open(file_path) as csv_data_file:
                csv_reader = csv.reader(csv_data_file)

                for data in csv_reader:
                    csv_data.append(data)

        return csv_data
