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

# from helper_functions import google_sheet
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from helper_functions.captcha_helper import *

# from helper_functions import selenium_helper

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

    def start_driver(self):
        print("start_driver")
        driver.get("https://www.libreview.com/")
        print("sleep 5")
        time.sleep(5)
        return driver

    def country_of_residence(self):
        print("country_of_residence")
        print("sleep 5")
        time.sleep(5)

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

    def populate_login_elements(self):
        print("populate_login_element")
        print("sleep 5")
        time.sleep(5)

        login_element = driver.find_element_by_id("loginForm-email-input")
        password_element = driver.find_element_by_id("loginForm-password-input")
        login_button_element = driver.find_element_by_id("loginForm-submit-button")
        login_element.send_keys(self.username)
        password_element.send_keys(self.password)

        try:
            login_button_element.click()
            time.sleep(3)

            token = driver.execute_script(
                "return window.sessionStorage.getItem('token')"
            )
            self.token = json.loads(token)["token"]
        except:
            raise BaseException("You could not login so a cookie was not set")

    def go_to_patients_page(self):
        print("go_to_patients_page")
        print("sleep 5")
        time.sleep(5)
        patients_button_element = driver.find_element_by_id(
            "main-header-dashboard-icon"
        )
        patients_button_element.click()

    def go_to_patient_page(self, patients_cell):
        patients_cell.click()

    def go_to_profile_of_patient(self, driver):
        profile_button = driver.find_element_by_id("profile-nav-button-container")
        profile_button.click()

    def click_on_hyperlink_to_get_glucose_data(self, driver):
        download_glucose_data_hyperlink = driver.find_element_by_xpath(
            '//*[@id="patient-profile-data-download-button"]'
        )
        download_glucose_data_hyperlink.click()

    def return_to_dashboard(self, driver):
        driver.get("https://www.libreview.com/dashboard")

    def increment_patients_cell(self, driver, x):
        try:
            patients_cell = driver.find_element_by_xpath(
                f"/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/table/tbody/tr[{x}]/td[1]/div"
            )
        except:
            patients_cell = False

        return patients_cell

    def click_on_patients_cell_in_table(self) -> None:
        print("patients_table")
        x = 1

        print("sleep for 10")
        time.sleep(10)

        patients_cell = driver.find_element_by_xpath(
            f"/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/table/tbody/tr[{x}]/td[1]/div"
        )

        while patients_cell:
            time.sleep(5)
            self.go_to_patient_page(patients_cell=patients_cell)

            time.sleep(5)
            self.go_to_profile_of_patient(driver=driver)

            time.sleep(5)
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
            glucose_data = captcha_request_four(
                driver=driver, endpoint_for_fourth_request=endpoint_for_fourth_request
            )

            write_glucose_data_to_file(glucose_data=glucose_data)

            x += 1

            self.return_to_dashboard(driver=driver)
            time.sleep(5)

            patients_cell = self.increment_patients_cell(driver=driver, x=x)
            time.sleep(5)