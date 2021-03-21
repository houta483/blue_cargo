import time
import json
import math
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


driver = webdriver.Chrome("utils/chromedriver")


class Selenium_Chrome_Class:
    def __init__(self, websites_to_scrape):
        self.websites_to_scrape = websites_to_scrape
        self.table = []
        self.data = {}

    def start_driver(self):
        print("start_driver")
        driver.get(self.websites_to_scrape[0])
        return driver

    def loop_through_pages(self):
        for index, end_point in enumerate(self.websites_to_scrape):
            if (index == 0):
                self.get_data_from_WHCorp_table(driver=driver)
                self.format_WHCorp_data(driver=driver)
            else:
                driver.get(end_point)
                self.american_storage_populate_template(driver=driver)

    def get_data_from_WHCorp_table(self, driver):
        print("get_data_from_WHCorp_table")

        my_table = driver.find_element_by_xpath("/html/body/div/table")
        rows = my_table.find_elements(By.TAG_NAME, "tr")

        for row_index, row in enumerate(rows):
            if (len(row.find_elements(By.TAG_NAME, "th"))):
                col = row.find_elements(By.TAG_NAME, "th")
                for index, my_row in enumerate(col):
                    if (index == 0):
                        self.table.append([])
                    self.table[row_index].append(my_row.text)

            if (len(row.find_elements(By.TAG_NAME, "td"))):
                col = row.find_elements(By.TAG_NAME, "td")
                for index, my_row in enumerate(col):
                    self.table[row_index].append(my_row.text)

    def format_shifts_helper_function(self, shifts_array):
        formatted_shifts = [[], []]
        for shift in shifts_array:
            if (shift == "" or shift == None):
                morning_or_afternoon = formatted_shifts[0].append("")
                time = formatted_shifts[1].append("")

            else:
                my_shift = shift.split(" ", 1)
                morning_or_afternoon = my_shift[0]
                time = my_shift[1][1:-1]

            formatted_shifts[0].append(morning_or_afternoon)
            formatted_shifts[1].append(time)

        return formatted_shifts

    def format_WHCorp_data(self, driver):
        print("format_WHCorp_data")
        number_of_weeks = len(self.table) - 2

        days_of_week = self.table[0][1:]

        shifts = self.table[1][1:]
        morning_or_afternoon, time = self.format_shifts_helper_function(shifts)
        time.append("")
        time.append("")
        morning_or_afternoon.append("")
        morning_or_afternoon.append("")

        week_label = self.table[2][0].lower()
        open_or_close = self.table[2][1:]

        for week_index in range(number_of_weeks):
            self.data[week_label] = {
                "WHCorp": []
            }

            for index in range(7):
                if (days_of_week[index] == "Saturday" or days_of_week[index] == "Sunday"):
                    entry_one = {
                        "Weekday": days_of_week[index],
                        "Shift": "CLOSED",
                        "Opening hours": "CLOSED",
                        "Avaliability": "CLOSED"
                    }

                    entry_two = {
                        "Weekday": days_of_week[index],
                        "Shift": "CLOSED",
                        "Opening hours": "CLOSED",
                        "Avaliability": "CLOSED"
                    }

                else:
                    entry_one = {
                        "Weekday": days_of_week[index],
                        "Shift": "Morning",
                        "Opening hours": time[index*2],
                        "Avaliability": open_or_close[index*2]
                    }

                    entry_two = {
                        "Weekday": days_of_week[index],
                        "Shift": "Afternoon",
                        "Opening hours": time[index*2 + 1],
                        "Avaliability": open_or_close[index*2 + 1]
                    }

                self.data[week_label]["WHCorp"].append(entry_one)
                self.data[week_label]["WHCorp"].append(entry_two)

    def format_american_storage_weeks_and_days(self, weeks, days, opening_hours):
        weeks = [week.text.lower() for week in weeks]
        days = [day.text for day in days]
        opening_hours = [open_hours.text for open_hours in opening_hours]
        formatted_days = []

        weeks_count = -1
        for day in days:
            if ("Monday morning" in day):
                weeks_count += 1
                formatted_days.append([day])
            else:
                formatted_days[weeks_count].append(day)

        return [weeks, formatted_days, opening_hours]

    def format_opening_hours(self, opening_hours):
        hours = opening_hours.split("day ")[1]
        hours = hours.replace('→', ':', 2)
        hours = hours.split("/")
        morning_hours = hours[0]
        afternoon_hours = hours[1]

        return[morning_hours, afternoon_hours]

    def american_storage_populate_template(self, driver):
        weeks = driver.find_elements(By.TAG_NAME, "h2")
        days = driver.find_elements(By.TAG_NAME, "li")
        opening_hours = driver.find_elements_by_class_name("opening-hour")
        weeks, days, opening_hours = self.format_american_storage_weeks_and_days(
            weeks=weeks, days=days, opening_hours=opening_hours)

        for index, week in enumerate(weeks):
            open_hours = self.format_opening_hours(opening_hours[index])
            open_hours_key = {
                "morning": f"{open_hours[0]}",
                "afternoon": f"{open_hours[1]}"
            }

            if (week not in self.data):
                self.data[week] = {}

            self.data[week]["AmericanStorage"] = []

            for day in days[index]:
                weekday = day.split(" ")[0]
                shift = day.split(" ")[1][0:-1]
                avaliability = day.split(":")[1][1:]

                self.data[week]["AmericanStorage"].append({
                    "Weekday": f"{weekday}",
                    "Shift": f"{shift}",
                    "Opening Hours": f"{open_hours_key[shift]}",
                    "Avaliability": f"{avaliability}"
                })
