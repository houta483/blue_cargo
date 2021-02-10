import glob
import time
from helper_functions.selenium_navigation import Selenium_Chrome_Class
from helper_functions.google_sheet import Google_Sheets
from googleapiclient.discovery import build
from helper_functions import google_sheet
import os
from selenium import webdriver
import csv
from helper_functions import selenium_helper


class Glucose_Slim:
    def upload_data(self):
        google_sheets_module = google_sheet.Google_Sheets(
            scopes=["https://www.googleapis.com/auth/spreadsheets"],
        )

        google_sheets_module.get_credentials()

        service = build("sheets", "v4", credentials=google_sheets_module.credentials)

        with open("csvfile.csv") as csv_data_file:
            csv_data = []
            csv_reader = csv.reader(csv_data_file)

            for line in csv_reader:
                csv_data.append(line)

            content = csv_data

        resource = {"majorDimension": "ROWS", "values": content}

        service.spreadsheets().values().append(
            spreadsheetId=os.environ["SPREADSHEET_ID"],
            range="Table_Metrics!A:A",
            body=resource,
            valueInputOption="USER_ENTERED",
        ).execute()

    def clean_up(self):
        print("final clean_up")
        os.remove("csvfile.csv")


app = Glucose_Slim()
selenium_navigator = Selenium_Chrome_Class(
    username=os.environ["USERNAME"],
    password=os.environ["GLUCOSE_PASSWORD"],
    current_url="https://www.libreview.com/",
)

if __name__ == "__main__":
    selenium_navigator.start_driver()
    selenium_navigator.country_of_residence()
    selenium_navigator.populate_login_elements()
    selenium_navigator.go_to_patients_page()
    selenium_navigator.get_all_data_from_patients_table()

    app.upload_data()
    app.clean_up()

    print("sleeping for two min to get the timing right")
    time.sleep(720)
