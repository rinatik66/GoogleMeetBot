import os
import subprocess
import threading
import time as t
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from utils import *
from record_audio import start_recording, stop_recording

# XPaths для элементов управления в Google Meet
MIC_XPATH = "//div[@role='button' and @aria-label='Выключить микрофон']"
WEBCAM_XPATH = "//div[@role='button' and @aria-label='Выключить камеру']"
JOIN_XPATH = "//button[.//span[contains(text(),'Присоединиться')]]"
OPTION_XPATH = "//button[@aria-label='Ещё']"
CHAT_BTN_XPATH = "//button[@aria-label='Начать чат со всеми участниками']"
CHAT_SELECTCHAT_BTN_XPATH = "//div[@data-panel-id='2']"
CHAT_TEXT_XPATH = "textarea"
HANG_UP_BTN_XPATH = "//button[@aria-label='Покинуть видеовстречу']"
CHAT_CLOSE_BTN_XPATH = "//button[@aria-label='Закрыть']"

# Константы для настройки таймаутов
PAGE_LOAD_TIMEOUT = 30  # секунд для загрузки страницы
ELEMENT_TIMEOUT = 20    # секунд для ожидания элементов
MAX_RETRIES = 3        # максимальное количество попыток подключения

browser = None
RECORDING_PROCESS = None
current_recording_file = None

def initFirefox():
    global browser
    service = Service(executable_path=FIREFOX_DVD_DIR)
    profile = webdriver.FirefoxProfile(FIREFOX_PROFILE)
    options = Options()
    options.profile = profile
    browser = webdriver.Firefox(service=service, options=options)
    browser.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    print("Firefox запущен.")

def wait_for_page_load():
    """Ожидание полной загрузки страницы"""
    try:
        WebDriverWait(browser, PAGE_LOAD_TIMEOUT).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        t.sleep(5)  # Дополнительная пауза для загрузки динамического контента
    except TimeoutException:
        print("Превышено время ожидания загрузки страницы")
        return False
    return True

def safe_click_button(by, selector, timeout=ELEMENT_TIMEOUT, retries=3):
    """Безопасный клик по элементу с повторными попытками"""
    for attempt in range(retries):
        try:
            element = WebDriverWait(browser, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            # Прокрутка к элементу
            browser.execute_script("arguments[0].scrollIntoView(true);", element)
            t.sleep(1)  # Пауза после прокрутки
            element.click()
            return True
        except ElementClickInterceptedException:
            print(f"Попытка {attempt + 1}: Элемент перекрыт, ожидаем...")
            t.sleep(2)
        except Exception as e:
            print(f"Попытка {attempt + 1}: Ошибка при клике: {str(e)}")
            t.sleep(2)
    return False

def joinMeeting(link):
    global browser
    if link == '':
        return
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Попытка подключения {attempt + 1} из {MAX_RETRIES}")
            browser.get(link)
            
            if not wait_for_page_load():
                continue
                
            # Последовательно пытаемся отключить микрофон и камеру
            if not safe_click_button(By.XPATH, MIC_XPATH):
                print("Не удалось отключить микрофон")
            
            if not safe_click_button(By.XPATH, WEBCAM_XPATH):
                print("Не удалось отключить камеру")
            
            # Пытаемся присоединиться к встрече
            if safe_click_button(By.XPATH, JOIN_XPATH):
                print("Успешно присоединились к встрече")
                return True
                
        except Exception as e:
            print(f"Ошибка при попытке {attempt + 1}: {str(e)}")
            t.sleep(5)  # Пауза перед следующей попыткой
            
    print("Не удалось присоединиться к встрече после всех попыток")
    return False

def sendChatMsg(text):
    global browser
    if not safe_click_button(By.XPATH, CHAT_BTN_XPATH):
        return False
    
    if not safe_click_button(By.XPATH, CHAT_SELECTCHAT_BTN_XPATH):
        return False
        
    try:
        chat_input = WebDriverWait(browser, ELEMENT_TIMEOUT).until(
            EC.element_to_be_clickable((By.TAG_NAME, CHAT_TEXT_XPATH))
        )
        chat_input.send_keys(text + "\n")
        t.sleep(1)
        
        if not safe_click_button(By.XPATH, CHAT_CLOSE_BTN_XPATH):
            print("Не удалось закрыть чат")
            
        return True
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {str(e)}")
        return False

def hangUpMeeting():
    try:
        return safe_click_button(By.XPATH, HANG_UP_BTN_XPATH)
    except Exception as e:
        print("Ошибка при завершении встречи:", e)
        return False

def startRecordingUnified(output_filename):
    global RECORDING_PROCESS, current_recording_file
    # Запускаем единую запись аудио и видео через ffmpeg
    process, actual_filename = start_recording(output_filename=output_filename)
    RECORDING_PROCESS = process
    current_recording_file = actual_filename

def stopRecordingUnified():
    global RECORDING_PROCESS, current_recording_file
    if RECORDING_PROCESS is not None:
        stop_recording(RECORDING_PROCESS)
        print("Unified recording saved to", current_recording_file)
        RECORDING_PROCESS = None
        current_recording_file = None
