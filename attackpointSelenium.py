from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import json
import math
import config


def format_time(time):
    hh, mm, ss = "", "", ""
    if len(time) > 1:
        ss = time[-2:]
        time_chopped = time[:-2]
    else:
        ss = time
    if len(time_chopped) > 1:
        mm = time_chopped[-2:]
        time_chopped = time_chopped[:-2]
    else:
        mm = time_chopped
    if len(time_chopped) > 0:
        hh = time_chopped
    formatted_time = ""
    if hh:
        hh = int(hh)
    else:
        hh = 0
    if mm:
        mm = int(mm)
    else:
        mm = 0
    if ss:
        ss = int(ss)
    else:
        ss = 0
    minutes = hh * 60 + mm + ss / 60
    return minutes


def get_pace(minutes, distance):
    pace = float(minutes) / float(distance)
    pace_min = math.floor(pace)
    remainder = round(60 * (pace - pace_min))
    return f"{pace_min}:{remainder}"


def fetch_days_activities(todays_date=datetime.today().strftime("%Y-%m-%d")):
    # website login details
    attackpoint_login = config.ATTACKPOINT_LOGIN
    # use Chrome to access web (will update chrome driver if needed)
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
    # get activities completed today
    try:
        check_activity_date = driver.find_element_by_xpath(
            f'//a[@href="/viewlog.jsp/user_13190/period-1/enddate-{todays_date}"]'
        ).click()
    except:
        print(f"No activities on {todays_date}")
    # click on edit buttons to edit each activity
    edit_button = driver.find_elements_by_xpath('//*[@title="Edit this entry"]')
    # loop over each activity
    activities = {}
    counter = -1
    for i, item in enumerate(edit_button):
        edit_button = driver.find_elements_by_xpath('//*[@title="Edit this entry"]')
        edit_button[i].click()
        # extract distance and description from each activity
        distance = driver.find_element_by_id("distance").get_attribute("value")
        description = driver.find_element_by_class_name("logtextarea").get_attribute(
            "value"
        )
        # check if activity has a distance and description and if it does extract time etc.
        if distance and not description:
            counter += 1
            time = driver.find_element_by_id("sessionlength").get_attribute("value")
            avg_hr = driver.find_element_by_id("ahr").get_attribute("value")
            # format time
            minutes = format_time(time)
            pace = get_pace(minutes, distance)
            # add data to dictionary
            run = {
                "date": todays_date,
                "distance": distance,
                "time": time,
                "minutes": minutes,
                "pace": pace,
                "avg_hr": avg_hr,
                "description": description,
            }
            activities[f"run_{counter}"] = run
        # go back to activity page
        driver.back()

    activities_formatted = json.dumps(activities, indent=2)
    driver.quit()
    return activities_formatted


if __name__ == "__main__":
    todays_date = "2021-07-14"
    today = fetch_days_activities()
    print(today)
