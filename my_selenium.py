from six.moves.urllib.request import urlopen
import re
import glob
import io
from selenium import webdriver
import os
import time
import datetime
import re
import shutil
from PyPDF2 import PdfFileReader, PdfFileWriter
import textract
from helper_functions import helper_functions
from helper_functions import google_sheet
import pdftotext
from pdf2docx import parse
from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path

os.environ["GLUCOSE_PASSWORD"] = "French44!"
final_directory = "/Users/Tanner/code/products/glucose/original_data"
PATH = "/Users/Tanner/utils/chromedriver"
driver = webdriver.Chrome(PATH)


class Selenium_Chrome_Class():
    def __init__(self, username, password, current_url):
        self.username = username
        self.password = password
        self.current_url = current_url

    def start_driver(self):
        print('start_driver')
        driver.get("https://www.libreview.com/")

    def country_of_residence(self):
        print('country_of_residence')
        driver.implicitly_wait(10)
        country_of_residence_element = driver.find_element_by_id(
            "country-select")
        country_of_residence_usa = driver.find_element_by_xpath(
            "//*[@id='country-select']/option[47]")
        country_of_residence_usa.click()
        submit_button = driver.find_element_by_id("submit-button")
        submit_button.click()
        self.current_url = driver.current_url

    def populate_login_elements(self):
        print('populate_login_element')
        login_element = driver.find_element_by_id("loginForm-email-input")
        password_element = driver.find_element_by_id(
            "loginForm-password-input")
        login_button_element = driver.find_element_by_id(
            "loginForm-submit-button")
        login_element.send_keys(self.username)
        password_element.send_keys(self.password)
        login_button_element.click()

    def go_to_patients_page(self):
        print('go_to_patients_page')
        patients_button_element = driver.find_element_by_id(
            "main-header-dashboard-icon")
        patients_button_element.click()

    def patients_table(self):
        print('patients_table')
        x = 1
        time.sleep(10)

        parameter = driver.find_element_by_xpath(
            f"/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/table/tbody/tr[{x}]/td[1]/div")

        while parameter:
            parameter.click()
            profile_button = driver.find_element_by_id(
                "profile-nav-button-container")
            profile_button.click()
            print('profile_button')
            time.sleep(10)

            glucose_history_button = driver.find_element_by_xpath(
                "//*[@id='reports-nav-button-container']")
            glucose_history_button.click()
            print('glucose_history_button')
            time.sleep(10)

            try:
                glucose_reports_button = driver.find_element_by_id(
                    "newGlucose-glucoseReports-button")
                glucose_reports_button.click()
                print('glucose_repots_button')
                time.sleep(10)
            except:
                glucose_reports_button = driver.find_element_by_id(
                    "pastGlucoseCard-report-button")
                glucose_reports_button.click()
                print('glucose_repots_button')
                time.sleep(10)

            download_glucose_report_button = driver.find_element_by_id(
                "reports-print-button")
            download_glucose_report_button.click()
            print('download_glucose_report_button')
            time.sleep(10)

            x += 1
            driver.get("https://www.libreview.com/dashboard")
            time.sleep(10)

            try:
                parameter = driver.find_element_by_xpath(
                    f"/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/table/tbody/tr[{x}]/td[1]/div")
            except:
                parameter = False

    def move_files(self):
        print('move_files')
        current_day = datetime.date.today()
        formatted_date = datetime.date.strftime(current_day, "%m-%d-%Y")
        starting_directory = "/Users/Tanner/Downloads"

        for filename in os.listdir(starting_directory):
            if re.search(formatted_date, str(filename)) and filename.endswith(".pdf"):
                file_path_to_move = os.path.join(starting_directory, filename)
                filename = filename.replace(" ", "")
                os.rename(file_path_to_move, f'original_data/{filename}')
            else:
                continue

    def extract_data(self, metric):
        print('preprocess_pdfs')
        data = []
        for files in os.listdir(final_directory):
            file_path_to_scrape = os.path.join(final_directory, files)
            pdfWriter = PdfFileWriter()
            writable_pdf = PdfFileReader(file_path_to_scrape)

            if files.endswith(".pdf"):
                with open(file_path_to_scrape, "rb") as f:
                    pdf = pdftotext.PDF(f)

                if (metric == 'avg'):
                    pages = helper_functions.find_correct_pages(
                        "Weekly Summary", pdf)
                    print(pages)

                    new_pdf = helper_functions.write_data_to_txt_file(
                        pages=pages, writable_pdf=writable_pdf,
                        where_to_save_pdf="truncated_data", person=files)

                    helper_functions.filter_txt_data(person=files)

                elif (metric == 'max'):
                    print('add code here for daily max')

    def upload_data(self):
        helper_functions.txt_to_csv()

        google_sheets_module = google_sheet.Google_Sheets(scopes=['https://www.googleapis.com/auth/spreadsheets'],
                                                          spreadsheet_id='1wwGhXxKS9dXEx6YM5p9qTRLtng1Rr6ASd-y07MCZaVs', sheet_range='Sheet1!A8:I1')
        google_sheets_module.main()

    def clean_up(self):
        print('clean_up')
        list_of_dirs = [glob.glob('preprocessed_data/*'),
                        glob.glob('truncated_data/*'),
                        glob.glob('ocr_jpg_data/*')]

        for directory in list_of_dirs:
            for files in directory:
                os.remove(files)


app = Selenium_Chrome_Class(
    username="stevenhoughtonjr1@gmail.com", password=os.environ['GLUCOSE_PASSWORD'], current_url="https://www.libreview.com/")
# app.start_driver()
# app.country_of_residence()
# app.populate_login_elements()
# app.go_to_patients_page()
# app.patients_table()
app.move_files()
app.extract_data('avg')
app.upload_data()
# app.clean_up()
