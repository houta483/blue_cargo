from selenium import webdriver
import os
import time
import datetime
import re
import shutil
from PyPDF2 import PdfFileReader, PdfFileWriter
import textract
from helper_functions import helper_functions

os.environ["GLUCOSE_PASSWORD"] = "French44!"
final_directory = "/Users/Tanner/code/products/glucose/pdf_unformatted_data"
PATH = "/Users/Tanner/utils/chromedriver"
# driver = webdriver.Chrome(PATH)


class Selenium_Chrome_Class():
    def __init__(self, username, password, current_url):
        self.username = username
        self.password = password
        self.current_url = current_url

    def start_driver(self):
        driver.get("https://www.libreview.com/")

    def country_of_residence(self):
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
        login_element = driver.find_element_by_id("loginForm-email-input")
        password_element = driver.find_element_by_id(
            "loginForm-password-input")
        login_button_element = driver.find_element_by_id(
            "loginForm-submit-button")
        login_element.send_keys(self.username)
        password_element.send_keys(self.password)
        login_button_element.click()

    def go_to_patients_page(self):
        patients_button_element = driver.find_element_by_id(
            "main-header-dashboard-icon")
        patients_button_element.click()

    def patients_table(self):
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

            glucose_reports_button = driver.find_element_by_xpath(
                "//*[@id='pastGlucoseCard-report-button']")
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
            parameter = driver.find_element_by_xpath(
                f"/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/table/tbody/tr[{x}]/td[1]/div")
            # The data from all users is getting pulled and put into the Downloads file

    def move_files(self):
        current_day = datetime.date.today()
        formatted_date = datetime.date.strftime(current_day, "%m-%d-%Y")
        starting_directory = "/Users/Tanner/Downloads"

        for filename in os.listdir(starting_directory):
            if re.search(formatted_date, str(filename)) and filename.endswith(".pdf"):
                file_path_to_move = os.path.join(starting_directory, filename)
                shutil.move(file_path_to_move, final_directory)
            else:
                continue

    def scrape_pdfs(self, metric):
        data = []
        for files in os.listdir(final_directory):
            if files.endswith(".pdf"):
                file_path_to_scrape = os.path.join(final_directory, files)
                pdf_file_path = file_path_to_scrape
                file_base_name = pdf_file_path.replace('.pdf', '')
                pdf = PdfFileReader(pdf_file_path)
                daily_log_pages = [pdf.numPages-3, pdf.numPages-2]
                pdfWriter = PdfFileWriter()

                for page_num in daily_log_pages:
                    pdfWriter.addPage(pdf.getPage(page_num))

                with open('{0}.pdf'.format(file_base_name), 'wb') as f:
                    pdfWriter.write(f)
                    f.close()

                if (metric == 'avg'):
                    with open('{0}.pdf'.format(file_base_name), "rb") as in_f:
                        input1 = PdfFileReader(in_f)
                        output = PdfFileWriter()
                        output_two = PdfFileWriter()
                        numPages = input1.getNumPages()

                        for i in range(numPages):
                            page = input1.getPage(i)
                            page.cropBox.lowerLeft = (30, 820)
                            page.cropBox.lowerRight = (80, 820)
                            page.cropBox.upperLeft = (30, 80)
                            page.cropBox.upperRight = (80, 80)
                            output.addPage(page)

                        with open(f"extracted_data/date_{files}".format(file_base_name), "wb") as out_f:
                            output.write(out_f)

                        for i in range(numPages):
                            page_two = input1.getPage(i)
                            page_two.cropBox.lowerLeft = (360, 820)
                            page_two.cropBox.lowerRight = (410, 820)
                            page_two.cropBox.upperLeft = (360, 80)
                            page_two.cropBox.upperRight = (410, 80)
                            output_two.addPage(page_two)

                        with open(f"extracted_data/avg_glucose{files}".format(file_base_name), "wb") as out_f:
                            output.write(out_f)

                elif (metric == 'max'):
                    print('add code here for daily max')


app = Selenium_Chrome_Class(
    username="stevenhoughtonjr1@gmail.com", password=os.environ['GLUCOSE_PASSWORD'], current_url="https://www.libreview.com/")
# app.start_driver()
# app.country_of_residence()
# app.populate_login_elements()
# app.go_to_patients_page()
# app.patients_table()
# app.move_files()
app.scrape_pdfs('avg')
