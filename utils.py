import re
import sys
import math


def remove_emoji(string):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese char
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r"", string)


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
