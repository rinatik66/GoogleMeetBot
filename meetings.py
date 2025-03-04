import time as t
import schedule
import browser_manager

def setup_schedule():
    # Пример для ежедневного запуска (day = "today") с запуском встречи и записи
    scheduleMeeting("today", "10:02", "10:30", "https://meet.google.com/qkh-wcsd-egv")

def scheduleMeeting(day, startHour, endHour, link):
    if str(day).lower() == "monday":
        schedule.every().monday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().monday.at(startHour).do(browser_manager.startRecording, "recordings/output_" + t.strftime("%Y%m%d_%H%M%S") + ".mp4")
        schedule.every().monday.at(endHour).do(browser_manager.hangUpMeeting)
        schedule.every().monday.at(endHour).do(browser_manager.stopRecording)
    elif str(day).lower() == "tuesday":
        schedule.every().tuesday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().tuesday.at(startHour).do(browser_manager.startRecording, "recordings/output_" + t.strftime("%Y%m%d_%H%M%S") + ".mp4")
        schedule.every().tuesday.at(endHour).do(browser_manager.hangUpMeeting)
        schedule.every().tuesday.at(endHour).do(browser_manager.stopRecording)
    elif str(day).lower() == "wednesday":
        schedule.every().wednesday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().wednesday.at(startHour).do(browser_manager.startRecording, "recordings/output_" + t.strftime("%Y%m%d_%H%M%S") + ".mp4")
        schedule.every().wednesday.at(endHour).do(browser_manager.hangUpMeeting)
        schedule.every().wednesday.at(endHour).do(browser_manager.stopRecording)
    elif str(day).lower() == "thursday":
        schedule.every().thursday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().thursday.at(startHour).do(browser_manager.startRecording, "recordings/output_" + t.strftime("%Y%m%d_%H%M%S") + ".mp4")
        schedule.every().thursday.at(endHour).do(browser_manager.hangUpMeeting)
        schedule.every().thursday.at(endHour).do(browser_manager.stopRecording)
    elif str(day).lower() == "friday":
        schedule.every().friday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().friday.at(startHour).do(browser_manager.startRecording, "recordings/output_" + t.strftime("%Y%m%d_%H%M%S") + ".mp4")
        schedule.every().friday.at(endHour).do(browser_manager.hangUpMeeting)
        schedule.every().friday.at(endHour).do(browser_manager.stopRecording)
    elif str(day).lower() == "saturday":
        schedule.every().saturday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().saturday.at(startHour).do(browser_manager.startRecording, "recordings/output_" + t.strftime("%Y%m%d_%H%M%S") + ".mp4")
        schedule.every().saturday.at(endHour).do(browser_manager.hangUpMeeting)
        schedule.every().saturday.at(endHour).do(browser_manager.stopRecording)
    elif str(day).lower() == "sunday":
        schedule.every().sunday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().sunday.at(startHour).do(browser_manager.startRecording, "recordings/output_" + t.strftime("%Y%m%d_%H%M%S") + ".mp4")
        schedule.every().sunday.at(endHour).do(browser_manager.hangUpMeeting)
        schedule.every().sunday.at(endHour).do(browser_manager.stopRecording)
    elif str(day).lower() == "today":
        schedule.every().day.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().day.at(startHour).do(browser_manager.startRecording, "recordings/output_" + t.strftime("%Y%m%d_%H%M%S") + ".mp4")
        schedule.every().day.at(endHour).do(browser_manager.hangUpMeeting)
        schedule.every().day.at(endHour).do(browser_manager.stopRecording)
