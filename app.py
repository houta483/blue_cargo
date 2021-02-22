import glob
import time
import requests
import os
import csv
from helper_functions.selenium_navigation import Selenium_Chrome_Class
from helper_functions.google_sheet import Google_Sheets
from googleapiclient.discovery import build
from helper_functions import google_sheet
from helper_functions.glucose_data_helper import Glucose_Data_Helper
from selenium import webdriver


selenium_navigator = Selenium_Chrome_Class(
    username=os.environ["USERNAME"],
    password=os.environ["GLUCOSE_PASSWORD"],
    current_url="https://www.libreview.com/",
)

glucose_data_helper = Glucose_Data_Helper()

google_sheets_module = google_sheet.Google_Sheets(
    scopes=["https://www.googleapis.com/auth/spreadsheets"],
    spreadsheet_id=os.environ["SPREADSHEET_ID"],
    tab_name="",
    sheet_range="A:IZ",
)


if __name__ == "__main__":
    selenium_navigator.start_driver()
    selenium_navigator.country_of_residence()
    selenium_navigator.populate_login_elements()
    selenium_navigator.go_to_patients_page()
    selenium_navigator.loop_through_patients_extracting_filtering_sorting_writing_data(
        google_sheets_module=google_sheets_module
    )

    google_sheets_module.clean_up()