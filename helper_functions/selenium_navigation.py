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
from helper_functions import google_sheet
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
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

    def get_k_parameter_re_captcha_v2(self, driver) -> str:
        iframe_with_k_parameter = driver.find_element_by_xpath(
            '//*[@id="exportData-reCAPTCHA"]/div/div/div/div/iframe'
        )
        src_attribute = iframe_with_k_parameter.get_attribute("src")
        regex_pattern = "((k=).+?(?=&))"
        k_parameter = re.search(regex_pattern, src_attribute).group()[2:]

        return k_parameter

    def re_captcha_v2_post(self, driver) -> str:
        print("re_captcha_v2_post")
        post_api_endpoint = "http://2captcha.com/in.php"

        api_key = os.getenv("CAPTCHA_API_KEY")
        post_method = "userrecaptcha"
        post_google_key = self.get_k_parameter_re_captcha_v2(driver=driver)
        post_page_url = driver.current_url

        post_api_params = {
            "key": api_key,
            "method": post_method,
            "googlekey": post_google_key,
            "pageurl": post_page_url,
        }

        id_re_captcha_v2 = requests.post(
            url=post_api_endpoint, params=post_api_params, json=1
        ).text[3:]
        time.sleep(20)

        return id_re_captcha_v2

    def g_recaptcha_response(self, driver, answer_token) -> None:
        javascript_make_textarea_visible_string = (
            f"document.getElementById('g-recaptcha-response').style.display = 'inline'"
        )
        driver.execute_script(javascript_make_textarea_visible_string)
        time.sleep(3)

        javascript_add_innerHTML_string = f"document.getElementById('g-recaptcha-response').innerHTML='{answer_token}';"
        driver.execute_script(javascript_add_innerHTML_string)
        time.sleep(3)

        javascript_make_button_visible_string = f"document.getElementById('exportData-modal-download-button').disabled = false;"
        driver.execute_script(javascript_make_button_visible_string)
        time.sleep(3)

    def submit_finished_captcha(self, driver):
        print("submit_finished_captcha")
        submit_captcha_button = driver.find_element_by_xpath(
            '//*[@id="exportData-modal-download-button"]'
        )
        submit_captcha_button.click()

    def re_captcha_v2_get(self, driver) -> None:
        print("re_captcha_v2_get")
        get_api_endpoint = "http://2captcha.com/res.php"

        api_key = os.getenv("CAPTCHA_API_KEY")
        get_action = "get"
        get_id = self.re_captcha_v2_post(driver=driver)

        get_api_params = {"key": api_key, "action": get_action, "id": get_id}

        answer_token = requests.get(url=get_api_endpoint, params=get_api_params).text

        recount = 1
        wait_time = 10

        while answer_token == "CAPCHA_NOT_READY":
            print(
                f"CAPCHA_NOT_READY for the {recount} time and will wait {wait_time} seconds now"
            )

            time.sleep(wait_time)

            recount += 1
            wait_time += 10

            answer_token = requests.get(
                url=get_api_endpoint, params=get_api_params
            ).text

        print("answer token received")
        trimmed_answer_token = answer_token[3:]
        self.g_recaptcha_response(driver=driver, answer_token=trimmed_answer_token)
        time.sleep(5)

        self.submit_finished_captcha(driver=driver)

    def click_on_patients_cell_in_table(self) -> None:
        print("patients_table")
        x = 1

        print("sleep for 10")
        time.sleep(10)

        patients_cell = driver.find_element_by_xpath(
            f"/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/table/tbody/tr[{x}]/td[1]/div"
        )

        while patients_cell:
            self.go_to_patient_page(patients_cell=patients_cell)
            time.sleep(5)

            self.go_to_profile_of_patient(driver=driver)
            time.sleep(5)

            self.click_on_hyperlink_to_get_glucose_data(driver=driver)
            time.sleep(5)

            self.get_k_parameter_re_captcha_v2(driver=driver)
            time.sleep(5)

            id_of_captcha = self.re_captcha_v2_get(driver=driver)

            x += 1

            self.return_to_dashboard(driver=driver)
            time.sleep(5)

            patients_cell = self.increment_patients_cell(driver=driver, x=x)
            time.sleep(5)