from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import json
import re
import sys

import config
from utils import remove_emoji
from stravaAPI import get_strava_run_ids


def fetch_strava_activities(num_of_activities=6, format=False, driver=False):
    # website login details
    strava_login = config.STRAVA_LOGIN
    # driver profile 
    options = webdriver.chrome.options.Options()
    options.add_argument("--disable-extensions")
    # use Chrome to access web (will update chrome driver if needed)
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    # open the website
    driver.get("https://www.strava.com/login")
    # add username and password and login
    name_box = driver.find_element_by_name("email")
    name_box.send_keys(strava_login.get("email"))
    pass_box = driver.find_element_by_name("password")
    pass_box.send_keys(strava_login.get("password"))
    login_button = driver.find_element_by_id("login-button").click()
    # filter the feed to only my activities
    following_button = driver.find_element_by_id("feed-filter-btn").click()
    your_activities = driver.find_element_by_xpath(
        "//a[@href='/dashboard?feed_type=my_activity']"
    ).click()
    # use strava API to get ids for latest runs
    ids = get_strava_run_ids(num_of_activities)
    # get i latest runs and run details
    strava_activities = {}
    for i, id in enumerate(ids):
        try:
            content = driver.find_element_by_xpath(
                f'//div[@id="Activity-{id}" and @class="activity feed-entry card"]'
            )
            entry_body = content.find_element_by_class_name("entry-body")
            title = entry_body.find_elements_by_css_selector("a")[0].text
            if len(entry_body.find_elements_by_css_selector("a")) > 1:
                description = entry_body.find_elements_by_css_selector("a")[1].text
            else:
                description = ""
            title = remove_emoji(title)
            description = remove_emoji(description)
            distance = entry_body.find_elements_by_css_selector("b")[0].text
            pace = entry_body.find_elements_by_css_selector("b")[1].text
            time = entry_body.find_elements_by_css_selector("b")[2].text
        except:
            try:
                content = driver.find_element_by_xpath(
                    f'//li[@id="Activity-{id}" and @class="activity child-entry"]'
                )
                entry_body = content.find_element_by_xpath(
                    '//div[@class="entry-body entry-inset"]'
                )
                title = entry_body.find_elements_by_css_selector("a")[0].text
                if len(entry_body.find_elements_by_css_selector("a")) > 1:
                    description = entry_body.find_elements_by_css_selector("a")[1].text
                else:
                    description = ""
                title = remove_emoji(title)
                description = remove_emoji(description)
                distance = entry_body.find_elements_by_css_selector("b")[0].text
                pace = entry_body.find_elements_by_css_selector("b")[1].text
                time = entry_body.find_elements_by_css_selector("b")[2].text
            except:
                print("No activity with id found")
        if title:
            strava_activities[f"activity_{i}"] = {
                "title": title,
                "description": description,
                "distance": distance,
                "time": time,
                "pace": pace,
            }
    # nicely format into a json file
    if format:
        strava_activities = json.dumps(strava_activities, indent=2)

    if driver:
        return driver, strava_activities
    else:
        # quit driver
        driver.quit()
        return strava_activities


if __name__ == "__main__":
    activities = fetch_strava_activities()
    print(activities)
