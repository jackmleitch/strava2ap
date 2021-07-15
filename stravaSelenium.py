from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import json
import config

todays_date = datetime.today().strftime("%Y-%m-%d")
# website login details
strava_login = config.STRAVA_LOGIN
# use Chrome to access web (will update chrome driver if needed)
driver = webdriver.Chrome(ChromeDriverManager().install())
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
# get latest runs
strava_activities = {}
div = driver.find_elements_by_class_name("entry-body")
for i in range(0, 5):
    distance = div[i].find_elements_by_css_selector("b")[0].text
    # pace = div[1].find_element_by_css_selector("a").get_attribute("href")
    # pace = div.find_element_by_class_name("stat-text").get_attribute("value")
    print(distance)
# activities[0].click()
# print(activities)
driver.quit()
