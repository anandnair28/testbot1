from datetime import datetime


def compare_time(time_stamp, dur):
    """Takes a time_stamp, and duration (in mins), and returns if
    current time is dur min past that"""
    if time_stamp == None:
        return True, ""
    if dur == 0:
        return True, ""
    time = datetime.fromtimestamp(time_stamp)
    curr_time = datetime.now()
    time_difference1 = curr_time - time
    time_difference2 = int((dur * 60) - time_difference1.seconds)

    mins_left = int(time_difference2 // (dur * 60))
    sec_left = int(time_difference2 % (dur * 60))

    wait_string = "`{}min(s) {}sec`".format(mins_left, sec_left)

    if mins_left == 0:
        wait_string = "`{}sec`".format(sec_left)

    return time_difference1.seconds > (dur * 60), wait_string


# def parse_message(message):
