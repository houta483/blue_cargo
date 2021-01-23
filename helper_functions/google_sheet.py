from __future__ import print_function
from collections import OrderedDict
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
        self.credentials = None
        self.current_df_from_online = []

    def main(self):
        self.get_credentials()
        self.sheet_range = "Max1!A:I"
        self.current_df_from_online = self.pull_sheet_data()

        service = build('sheets', 'v4', credentials=self.credentials)

        if (self.current_df_from_online != None):
            print('there is data already in the sheet')

            incoming_data = self.parse_csv_data()
            combined_values = self.current_df_from_online + incoming_data

            filtered_combined_values = self.clean_up_dataframe_and_remove_duplicates(
                combined_values)

            resource = {
                "majorDimension": "ROWS",
                "values": filtered_combined_values
            }

            service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=self.sheet_range,
                body=resource,
                valueInputOption="USER_ENTERED"
            ).execute()

        else:

            values_to_add = self.parse_csv_data()
            duplicates_removed_data = self.clean_up_dataframe_and_remove_duplicates(
                values_to_add)

            resource = {
                "majorDimension": "ROWS",
                "values": duplicates_removed_data
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

    def clean_up_dataframe_and_remove_duplicates(self, passed_values=None):
        if (passed_values == None):
            unique_values_array = OrderedDict((tuple(x), x)
                                              for x in self.current_df_from_online).values()
        else:
            unique_values_array = OrderedDict((tuple(x), x)
                                              for x in passed_values).values()
        return list(unique_values_array)

    def pull_sheet_data(self):
        service = build('sheets', 'v4', credentials=self.credentials)
        sheet = service.spreadsheets()

        result = sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range=self.sheet_range
        ).execute()

        values = result.get('values', [])
        value_to_return = None

        if not values:
            print('No data found.')
            value_to_return = None
        else:
            rows = sheet.values().get(spreadsheetId=self.spreadsheet_id,
                                      range=self.sheet_range
                                      ).execute()
            data_frame = rows.get('values')
            print("COMPLETE: Data copied")
            value_to_return = data_frame

        return value_to_return

    def get_credentials(self):
        if os.path.exists('config/token.pickle'):
            with open('config/token.pickle', 'rb') as token:
                self.credentials = pickle.load(token)

        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'config/credentials.json', self.scopes)
                self.credentials = flow.run_local_server(port=0)
            with open('config/token.pickle', 'wb') as token:
                pickle.dump(self.credentials, token)
