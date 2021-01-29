from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


def set_chrome_options() -> None:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("download.default_directory=downloads")

    chrome_prefs = {}

    chrome_prefs["profile.default_content_settings.popups"] = 0

    chrome_prefs["download.default_directory"] = "downloads"

    # chrome_options.experimental_options["prefs"] = chrome_prefs
    # chrome_prefs["profile.default_content_settings"] = {"images": 2}

    chrome_options.add_experimental_option("prefs", chrome_prefs)
    return chrome_options
