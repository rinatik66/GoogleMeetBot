import os
import subprocess
import sys
import selenium
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import os
from enum import Enum
import threading
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

import time as t
from utils import *

recording_process = None

'''Locating by xpath here is the best thing to do here, since google Meet changes selectors, classes name and all that sort of stuff for every meeting
    XPaths remaing the same, but a slight change by them would make this program fail.
    The xpath is found clicking by inspecting the element of the searched button, and finding the parent div tthat has role="button" tag
'''

# Кнопка выключения микрофона
MIC_XPATH = "//div[@role='button' and @aria-label='Выключить микрофон']"

# Кнопка выключения камеры
WEBCAM_XPATH = "//div[@role='button' and @aria-label='Выключить камеру']"

# Кнопка присоединения (ищем кнопку, в которой содержится текст "Присоединиться")
JOIN_XPATH = "//button[.//span[contains(text(),'Присоединиться')]]"

# Кнопка меню дополнительных опций ("Ещё")
OPTION_XPATH = "//button[@aria-label='Ещё']"

# Кнопка чата для начала общения со всеми участниками
CHAT_BTN_XPATH = "//button[@aria-label='Начать чат со всеми участниками']"

# (Если требуется) кнопка выбора конкретного чата – можно попробовать такой селектор,
# но его может потребоваться доработать, если в интерфейсе несколько подобных элементов.
CHAT_SELECTCHAT_BTN_XPATH = "//div[@data-panel-id='2']"

# Текстовое поле чата – оставляем, как есть, поскольку это тег textarea
CHAT_TEXT_XPATH = "textarea"

# Кнопка завершения встречи (отключения)
HANG_UP_BTN_XPATH = "//button[@aria-label='Покинуть видеовстречу']"

# Кнопка закрытия панели чата
CHAT_CLOSE_BTN_XPATH = "//button[@aria-label='Закрыть']"


browser = None

from selenium.webdriver.firefox.service import Service

def startRecording(*args, **kwargs):
    global RECORDER_PROCESS
    if not os.path.exists("recordings"):
        os.makedirs("recordings")
    filename = "recordings/meeting_recording_" + t.strftime("%Y%m%d_%H%M%S") + ".mp4"
    # Обновлённая команда: используем индекс устройств "3:0" (экран и микрофон black hole)
    cmd = [
        "ffmpeg",
        "-f", "avfoundation",
        "-framerate", "30",
        "-video_size", "960x480",
        "-i", "3:0",  # поменяйте на "3:0", если хотите использовать black hole
        "-ar", "48000",
        "-y", filename
    ]
    print("Starting screen recording with command:", " ".join(cmd))
    RECORDER_PROCESS = subprocess.Popen(cmd)
    print("Recording started, saving to", filename)


def stopRecording(*args, **kwargs):
    global RECORDER_PROCESS
    if RECORDER_PROCESS is not None:
        RECORDER_PROCESS.terminate()
        try:
            RECORDER_PROCESS.wait(timeout=10)
        except subprocess.TimeoutExpired:
            RECORDER_PROCESS.kill()
        print("Recording stopped.")
        RECORDER_PROCESS = None


def initFirefox():
    global browser
    service = Service(executable_path=FIREFOX_DVD_DIR)
    profile = webdriver.FirefoxProfile(FIREFOX_PROFILE)
    options = Options()
    options.profile = profile
    browser = webdriver.Firefox(service=service, options=options)


def joinMeeting(link):
    global browser

    if link == '':
        return

    try:
        browser.get(link)
        t.sleep(15)
        print("Trying to join meeting")
        clickButton(By.XPATH, MIC_XPATH)
        clickButton(By.XPATH, WEBCAM_XPATH)
        clickButton(By.XPATH, JOIN_XPATH)
    except:
        # In this way, in case of any error we can try again
        print("Failed to join meeting, trying again in 60 secs")
        t.sleep(60)
        joinMeeting(link)


def clickButton(by, selector):
    global browser
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((by, selector))).click()
    t.sleep(1)

def writeText(by, selector, text):
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((by, selector))).clear()
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((by, selector))).send_keys(text + "\n")

def sendChatMsg(text):
    global browser
    # Открыть окно чата
    clickButton(By.XPATH, CHAT_BTN_XPATH)
    # Выбрать нужный чат (если требуется)
    clickButton(By.XPATH, CHAT_SELECTCHAT_BTN_XPATH)
    # Записать сообщение – используем тег текстового поля
    writeText(By.TAG_NAME, CHAT_TEXT_XPATH, text)
    t.sleep(1)
    # Закрыть окно чата
    clickButton(By.XPATH, CHAT_CLOSE_BTN_XPATH)


def checkStarted():
    try:
        clickButton(By.XPATH, OPTION_XPATH)
    except:
        return False
    return True

def hangUpMeeting():
    try:
        clickButton(By.XPATH, HANG_UP_BTN_XPATH)
    except:
        return False
    return True
