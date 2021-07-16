from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import json
import os

import config
from utils import format_time, get_pace, get_dates
from stravaSelenium import fetch_strava_activities


def attackpoint_login(driver=False):
    # website login details
    attackpoint_login = config.ATTACKPOINT_LOGIN
    # use Chrome to access web (will update chrome driver if needed)
    if not driver:
        driver = webdriver.Chrome(ChromeDriverManager().install())
    # open the website
    driver.get(
        "https://www.attackpoint.org/login.jsp?returl=https%3A%2F%2Fwww.attackpoint.org%2F"
    )
    # add username and password and login
    name_box = driver.find_element_by_name("username")
    name_box.send_keys(attackpoint_login.get("username"))
    pass_box = driver.find_element_by_name("password")
    pass_box.send_keys(attackpoint_login.get("password"))
    login_button = driver.find_element_by_xpath("//input[@value='Login']").click()
    # navigate to my ap log
    mylog_button = driver.find_element_by_xpath(
        '//a[@href="/log.jsp/user_13190"]'
    ).click()
    return driver


def fetch_attackpoint_activities(days=3, format=False, driver=False):
    # log into attackpoint
    if not driver:
        driver = webdriver.Chrome(ChromeDriverManager().install())
    driver = attackpoint_login(driver)
    # get activities completed on previous number of days
    dates = get_dates(days=days)
    # loop over each day
    counter = -1
    ap_activities = {}
    for day in dates:
        try:
            check_activity_date = driver.find_element_by_xpath(
                f'//a[@href="/viewlog.jsp/user_13190/period-1/enddate-{day}"]'
            ).click()
        except:
            continue
        # click on edit buttons to edit each activity
        edit_button = driver.find_elements_by_xpath('//*[@title="Edit this entry"]')
        # loop over each activity on given day
        for i, item in enumerate(edit_button):
            edit_button = driver.find_elements_by_xpath('//*[@title="Edit this entry"]')
            # reverse edit_button to get activities in order
            edit_button = edit_button[::-1]
            edit_button[i].click()
            # extract distance and description from each activity
            distance = driver.find_element_by_id("distance").get_attribute("value")
            description = driver.find_element_by_class_name(
                "logtextarea"
            ).get_attribute("value")
            # check if activity has a distance and description and if it does extract time etc.
            if distance:
                counter += 1
                time = driver.find_element_by_id("sessionlength").get_attribute("value")
                avg_hr = driver.find_element_by_id("ahr").get_attribute("value")
                # format time
                minutes = format_time(time)
                pace = get_pace(minutes, distance)
                # add data to dictionary
                run = {
                    "date": day,
                    "distance": distance,
                    "time": time,
                    "minutes": minutes,
                    "pace": pace,
                    "avg_hr": avg_hr,
                    "description": description,
                }
                ap_activities[f"activity_{counter}"] = run
            # go back to activity page
            driver.back()
        driver.back()
    if format:
        ap_activities = json.dumps(ap_activities, indent=2)
    if not driver:
        driver.quit()
    return ap_activities


def update_description(days=2):
    # fetch recent activities from strava
    driver, strava = fetch_strava_activities(
        num_of_activities=int(days * 4), driver=True
    )
    # fetch recent activities from attackpoint
    attackpoint = fetch_attackpoint_activities(days=days, driver=driver)
    # get a list of activity descriptions to post on attackpoint
    descriptions = []
    for i in range(0, min(len(strava), len(attackpoint))):
        # get activity titles and descriptions from the strava data collected
        activity_title = strava[f"activity_{i}"]["title"]
        activity_description = strava[f"activity_{i}"]["description"]
        # prepare description to be posted on attackpoint
        if activity_description:
            activity_post = (
                "\n"
                + activity_title
                + "\n"
                + activity_description
                + "\n<small><a href='https://github.com/jackmleitch/strava2ap_auto'>strava2ap™</a></small>\n\n"
            )
        else:
            activity_post = (
                "\n"
                + activity_title
                + "\n<small><a href='https://github.com/jackmleitch/strava2ap_auto'>strava2ap™</a></small>\n\n"
            )
        descriptions.append(activity_post)
    # counters to keep track of thingf
    counter_activities = -1
    activities_edited = 0
    # if these titles are on strava then dont update activity description on ap
    strava_default_titles = [
        "Morning Run",
        "Lunch Run",
        "Afternoon Run",
        "Evening Run",
        "Night Run",
    ]
    # loop through days
    for day in get_dates(days=days):
        # go onto the days activity
        check_activity_date = driver.find_element_by_xpath(
            f'//a[@href="/viewlog.jsp/user_13190/period-1/enddate-{day}"]'
        ).click()
        edit_button = driver.find_elements_by_xpath('//*[@title="Edit this entry"]')
        # loop over each activity on given day
        for i, item in enumerate(edit_button):
            edit_button = driver.find_elements_by_xpath('//*[@title="Edit this entry"]')
            # reverse edit_button to get activities in order
            edit_button = edit_button[::-1]
            edit_button[i].click()
            distance = driver.find_element_by_id("distance").get_attribute("value")
            # if not a run then ignore
            if not distance:
                driver.back()
            else:
                counter_activities += 1
                description = driver.find_element_by_class_name(
                    "logtextarea"
                ).get_attribute("value")
                # if no description then ignore
                if description:
                    driver.back()
                # if there is no description then we can add one!
                if not description:
                    strava_title = strava[f"activity_{counter_activities}"]["title"]
                    # if title is not on default strava titles
                    if strava_title not in strava_default_titles:
                        activities_edited += 1
                        text_input = driver.find_element_by_class_name("logtextarea")
                        text_input.send_keys(descriptions[counter_activities])
                        submit = driver.find_element_by_xpath(
                            "//input[@value='Submit']"
                        ).click()
                    else:
                        driver.back()
        driver.get("https://www.attackpoint.org/log.jsp/user_13190")
    driver.quit()
    print(f"\n{activities_edited} activity descriptions posted")


if __name__ == "__main__":
    # from keep_alive import keep_alive
    # keep_alive()
    update_description()
