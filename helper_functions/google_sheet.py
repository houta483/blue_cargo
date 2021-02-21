from __future__ import print_function

import os.path
import pickle
import csv
import glob, os

from collections import OrderedDict
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pprint import pprint
from googleapiclient import discovery


class Google_Sheets:
    def __init__(self, scopes, spreadsheet_id, tab_name, sheet_range):
        self.scopes = scopes
        self.credentials = None
        self.spreadsheet_id = spreadsheet_id
        self.tab_name = tab_name
        self.sheet_range = sheet_range

    def get_credentials(self) -> None:
        print("get_credentials")

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

    def get_current_glucose_data_from_online(self) -> None:
        print("get_current_glucose_data_from_online")

        service = build("sheets", "v4", credentials=self.credentials)
        sheet = service.spreadsheets()

        result = (
            sheet.values()
            .get(spreadsheetId=self.spreadsheet_id, range=self.sheet_range)
            .execute()
        )

        values = result.get("values", [])
        value_to_return = None

        if not values:
            print("No data found.")
            value_to_return = None
        else:
            rows = (
                sheet.values()
                .get(spreadsheetId=self.spreadsheet_id, range=self.sheet_range)
                .execute()
            )
            data_frame = rows.get("values")
            value_to_return = data_frame
            current_glucose_data = data_frame

            return current_glucose_data

    def load_local_csv_data(self, glucose_file):
        print("load_local_csv_data")

        csv_data = []

        with open(f"{glucose_file}") as csv_data_file:
            csv_reader = csv.reader(csv_data_file)

            for daily_input in csv_reader:
                csv_data.append(daily_input)

        incoming_glucose_data = csv_data

        return incoming_glucose_data

    def get_current_sheets(self):
        service = build("sheets", "v4", credentials=self.credentials)

        sheet_metadata = (
            service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        )

        sheets = sheet_metadata.get("sheets", "")

        current_sheets = []

        for sheet in sheets:
            current_sheets.append(sheet["properties"]["title"])

        return current_sheets

    def create_sheet_if_not_exist(self, name, current_sheets):

        service = build("sheets", "v4", credentials=self.credentials)
        gsheet_id = self.spreadsheet_id
        spreadsheets = service.spreadsheets()
        sheet_name = name

        if name not in current_sheets:
            try:
                request_body = {
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": sheet_name,
                                    "tabColor": {
                                        "red": 0.44,
                                        "green": 0.99,
                                        "blue": 0.50,
                                    },
                                }
                            }
                        }
                    ]
                }

                response = spreadsheets.batchUpdate(
                    spreadsheetId=gsheet_id, body=request_body
                ).execute()

                print(response)
                sheet_already_exists = False

            except Exception as e:
                print(e)

        else:
            print(f"The sheet for {name} already exists")
            sheet_already_exists = True

        return sheet_already_exists

    def upload_data(self, final_data) -> None:
        # MAKE ONE TAB PER PERSON

        print("upload_data")

        service = build("sheets", "v4", credentials=self.credentials)
        resource = {"majorDimension": "ROWS", "values": final_data}

        service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=f"{self.tab_name}!{self.sheet_range}",
            body=resource,
            valueInputOption="USER_ENTERED",
        ).execute()

    def clean_up(self):
        print("final clean_up")
        directories = ["glucose_data", "filtered_glucose_data"]

        for directory in directories:
            length = len(os.listdir(directory))
            for index, file in enumerate(os.listdir(directory)):
                if index == length:
                    break

                file_path = os.path.join(directory, file)
                os.remove(file_path)
