import re
import glob
import io
from selenium import webdriver
import os
import time
import datetime
import pytz
import shutil
from helper_functions import google_sheet
import sys
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

    def get_all_data_from_patients_table(self):
        print("patients_table")
        now = datetime.datetime.now()
        timezone = pytz.timezone("America/Chicago")
        timezoned_time = timezone.localize(now)

        print(timezoned_time)

        dt_string = now.strftime("%m/%d/%y %H:%M:%S")

        row_index = 1
        cell_index = 1

        print("sleep for 10")
        time.sleep(10)

        row = driver.find_element_by_xpath(
            f"/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/table/tbody/tr[{row_index}]"
        )

        cell = driver.find_element_by_xpath(
            f"/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/table/tbody/tr[{row_index}]/td[{cell_index}]"
        )

        while row:
            first_cell = True
            while cell:
                if first_cell == True:
                    with open("csvfile.csv", "a") as file:
                        file.write(dt_string + ",")

                    first_cell = False

                else:
                    with open("csvfile.csv", "a") as file:
                        file.write(str(cell.text + ","))

                    cell_index += 1

                try:
                    cell = driver.find_element_by_xpath(
                        f"/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/table/tbody/tr[{row_index}]/td[{cell_index}]"
                    )
                except:
                    with open("csvfile.csv", "a") as file:
                        file.write("\n")
                    cell = False

            else:
                cell_index = 1
                row_index += 1

                try:
                    row = driver.find_element_by_xpath(
                        f"/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/table/tbody/tr[{row_index}]"
                    )

                    cell = driver.find_element_by_xpath(
                        f"/html/body/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/div[1]/table/tbody/tr[{row_index}]/td[{cell_index}]"
                    )
                except:
                    with open("csvfile.csv", "a") as file:
                        file.write(
                            "-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-,-"
                        )

                    row = False