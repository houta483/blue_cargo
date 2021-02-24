import re
import glob
import io
import os
import time
import datetime
import pytz
import shutil
import sys
import requests
import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

from helper_functions.glucose_data_helper import Glucose_Data_Helper
from helper_functions.captcha_helper import *
from helper_functions.google_sheet import Google_Sheets
from helper_functions import selenium_helper

DOCKER_KEY = os.environ.get("AM_I_IN_A_DOCKER_CONTAINER", False)

if DOCKER_KEY:
    chrome_options = selenium_helper.set_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)
    print("I am running in a Docker container")
elif DOCKER_KEY == False:
    driver = webdriver.Chrome("utils/chromedriver")
    os.environ["GLUCOSE_PASSWORD"] = "French44!"
    os.environ["USERNAME"] = "stevenhoughtonjr1@gmail.com"
    os.environ["SPREADSHEET_ID"] = "1wwGhXxKS9dXEx6YM5p9qTRLtng1Rr6ASd-y07MCZaVs"
    print("I am on local machine")


class Selenium_Chrome_Class:
    def __init__(self, username, password, current_url):
        self.username = username
        self.password = password
        self.current_url = current_url
        self.token = None

    def wait_for_page_to_load(self, driver, id_of_element):
        print("wait_for_page_to_load")
        timeout = 10

        try:
            page_is_ready = WebDriverWait(driver=driver, timeout=timeout).until(
                EC.presence_of_element_located((By.ID, id_of_element))
            )
            print("Page is ready!")

        except TimeoutException:
            print("Loading took too much time!")

    def start_driver(self):
        print("start_driver")
        driver.get("https://www.libreview.com/")
        self.wait_for_page_to_load(driver=driver, id_of_element="submit-button")

        return driver

    def country_of_residence(self) -> None:
        print("country_of_residence")
        self.wait_for_page_to_load(driver=driver, id_of_element="country-select")

        country_of_residence_element = driver.find_element_by_id("country-select")
        country_of_residence_usa = driver.find_element_by_xpath(
            "//*[@id='country-select']/option[47]"
        )

        try:
            country_of_residence_usa.click()
            submit_button = driver.find_element_by_id("submit-button")
            submit_button.click()
            self.current_url = driver.current_url

        except:
            raise BaseException("Could not submit the country of residence")

    def populate_login_elements(self) -> None:
        print("populate_login_element")
        self.wait_for_page_to_load(driver=driver, id_of_element="loginForm-email-input")

        login_element = driver.find_element_by_id("loginForm-email-input")
        password_element = driver.find_element_by_id("loginForm-password-input")
        login_button_element = driver.find_element_by_id("loginForm-submit-button")
        login_element.send_keys(self.username)
        password_element.send_keys(self.password)

        try:
            login_button_element.click()
            self.wait_for_page_to_load(
                driver=driver, id_of_element="meterUpload-meterImage-image"
            )

            token = driver.execute_script(
                "return window.sessionStorage.getItem('token')"
            )
            self.token = json.loads(token)["token"]
        except:
            raise BaseException("You could not login so a cookie was not set")

    def go_to_patients_page(self) -> None:
        print("go_to_patients_page")
        self.wait_for_page_to_load(
            driver=driver, id_of_element="main-header-dashboard-icon"
        )

        patients_button_element = driver.find_element_by_id(
            "main-header-dashboard-icon"
        )
        patients_button_element.click()

    def go_to_patient_page(self, patients_cell) -> None:
        print("go_to_patient_page")

        time.sleep(3)

        patients_cell.click()

    def go_to_profile_of_patient(self, driver) -> None:
        print("go_to_profile_of_patient")
        self.wait_for_page_to_load(
            driver=driver, id_of_element="profile-nav-button-container"
        )

        profile_button = driver.find_element_by_id("profile-nav-button-container")
        profile_button.click()

    def click_on_hyperlink_to_get_glucose_data(self, driver) -> None:
        print("click_on_hyperlink_to_get_glucose_data")

        self.wait_for_page_to_load(
            driver=driver, id_of_element="patient-profile-data-download-button"
        )

        download_glucose_data_hyperlink = driver.find_element_by_xpath(
            '//*[@id="patient-profile-data-download-button"]'
        )
        download_glucose_data_hyperlink.click()

    def return_to_dashboard(self, driver) -> None:
        print("return_to_dashboard")

        driver.get("https://www.libreview.com/dashboard")

    def increment_patients_cell(self, driver, x):
        print("increment_patients_cell")

        self.wait_for_page_to_load(
            driver=driver, id_of_element="download-current-view-link"
        )

        try:
            patients_cell = driver.find_element_by_xpath(
                f"/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/table/tbody/tr[{x}]/td[1]/div"
            )
        except:
            patients_cell = False

        return patients_cell

    def loop_through_patients_extracting_filtering_sorting_writing_data(
        self, google_sheets_module
    ) -> None:
        print("loop_through_patients_extracting_filtering_sorting_writing_data")

        x = 1

        time.sleep(3)

        patients_cell = driver.find_element_by_xpath(
            f"/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/table/tbody/tr[{x}]/td[1]/div"
        )

        while patients_cell:
            self.go_to_patient_page(patients_cell=patients_cell)
            self.go_to_profile_of_patient(driver=driver)
            self.click_on_hyperlink_to_get_glucose_data(driver=driver)

            time.sleep(3)
            k_parameter = get_k_parameter_re_captcha_v2(driver=driver)

            time.sleep(3)
            captcha_id_returned_after_posting = re_captcha_v2_post(
                driver=driver, k_parameter=k_parameter
            )

            time.sleep(3)
            captcha_answer_token = re_captcha_v2_get(
                driver=driver, captcha_id=captcha_id_returned_after_posting
            )

            time.sleep(3)
            second_bearer_token, second_request_url = captcha_request_one(
                driver=driver,
                bearer_token=self.token,
                answer_token=captcha_answer_token,
            )

            time.sleep(3)
            client_for_third_request, endpoint_for_third_request = captcha_request_two(
                driver=driver,
                second_bearer_token=second_bearer_token,
                second_request_url=second_request_url,
            )

            time.sleep(3)
            endpoint_for_fourth_request = captcha_request_three(
                driver=driver,
                request_client=client_for_third_request,
                endpoint_for_third_request=endpoint_for_third_request,
            )

            time.sleep(3)
            name, glucose_data = captcha_request_four(
                driver=driver, endpoint_for_fourth_request=endpoint_for_fourth_request
            )

            time.sleep(3)
            write_glucose_data_to_local_file(name=name, glucose_data=glucose_data)

            Glucose_Data_Helper().sort_drop_replace_add_horizontal_write_etc(name=name)

            google_sheets_module.tab_name = name
            google_sheets_module.get_credentials()
            current_sheets = google_sheets_module.get_current_sheets()
            google_sheets_module.create_sheet_if_not_exist(
                name=name, current_sheets=current_sheets
            )

            incoming_from_csv_glucose_data = google_sheets_module.load_local_csv_data(
                glucose_file=f"filtered_glucose_data/filtered_{name}_data.csv"
            )

            final_data = incoming_from_csv_glucose_data

            google_sheets_module.upload_data(final_data=final_data)

            x += 1

            time.sleep(5)
            self.return_to_dashboard(driver=driver)

            time.sleep(5)
            patients_cell = self.increment_patients_cell(driver=driver, x=x)