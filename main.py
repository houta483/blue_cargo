from selenium_navigator import Selenium_Chrome_Class
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json


selenium_navigator = Selenium_Chrome_Class(
    websites_to_scrape=["https://bluecargo.julink.fr/site1/index.html",
                        "https://bluecargo.julink.fr/site2/index.html"]
)


if __name__ == "__main__":
    selenium_navigator.start_driver()
    selenium_navigator.loop_through_pages()
    json_object = json.dumps(selenium_navigator.data, indent=4)
    print(json_object)
