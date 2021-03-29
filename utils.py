from datetime import datetime


def compare_time(time_stamp, dur):
    """Takes a time_stamp, and duration (in mins), and returns if
    current time is dur min past that"""
    if time_stamp == None:
        return True
    time = datetime.fromtimestamp(time_stamp)
    curr_time = datetime.now()
    time_difference = curr_time - time
    return time_difference.seconds > (dur * 60)
