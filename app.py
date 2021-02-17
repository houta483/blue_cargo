import glob
import time
import requests
import os
import csv
from helper_functions.selenium_navigation import Selenium_Chrome_Class
from helper_functions.google_sheet import Google_Sheets
from googleapiclient.discovery import build
from helper_functions import google_sheet
from selenium import webdriver


selenium_navigator = Selenium_Chrome_Class(
    username=os.environ["USERNAME"],
    password=os.environ["GLUCOSE_PASSWORD"],
    current_url="https://www.libreview.com/",
)

google_sheets_module = google_sheet.Google_Sheets(
    scopes=["https://www.googleapis.com/auth/spreadsheets"],
)


if __name__ == "__main__":
    selenium_navigator.start_driver()
    selenium_navigator.country_of_residence()
    selenium_navigator.populate_login_elements()
    selenium_navigator.go_to_patients_page()
    selenium_navigator.click_on_patients_cell_in_table()

    google_sheets_module.get_credentials()
    google_sheets_module.upload_data()
    google_sheets_module.clean_up()