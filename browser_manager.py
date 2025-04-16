import os
import subprocess
import threading
import time as t
import random
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from utils import *
from record_audio import start_recording, stop_recording
from selenium.webdriver.common.action_chains import ActionChains

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

# Новые XPath для диалогового окна и ввода имени
CONTINUE_BTN_XPATH = "//span[@jsname='V67aGc' and contains(text(),'Продолжить с отключенными микрофоном и камерой')]"
NAME_INPUT_XPATH = "//input[@jsname='YPqjbf' and @aria-label='Укажите свое имя']"

# Константы для настройки таймаутов
PAGE_LOAD_TIMEOUT = 30  # секунд для загрузки страницы
ELEMENT_TIMEOUT = 20    # секунд для ожидания элементов
MAX_RETRIES = 3        # максимальное количество попыток подключения

browser = None
RECORDING_PROCESS = None
current_recording_file = None

def initChrome():
    global browser
    service = Service(executable_path=CHROME_DRIVER_DIR)
    options = Options()

    # Стелс-режим
    options.add_argument('--incognito')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Эмуляция реального браузера
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Маскировка WebDriver
    options.add_argument('--disable-blink-features')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-site-isolation-trials')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-features=IsolateOrigins,site-per-process')
    options.add_argument('--disable-site-isolation-for-policy')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-notifications')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-translate')
    options.add_argument('--disable-sync')
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-breakpad')
    options.add_argument('--disable-component-extensions-with-background-pages')
    options.add_argument('--disable-features=TranslateUI,BlinkGenPropertyTrees')
    options.add_argument('--disable-ipc-flooding-protection')
    options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
    options.add_argument('--force-color-profile=srgb')
    options.add_argument('--metrics-recording-only')
    options.add_argument('--no-first-run')
    options.add_argument('--password-store=basic')
    options.add_argument('--use-mock-keychain')
    options.add_argument('--use-gl=swiftshader')
    options.add_argument('--window-position=0,0')
    
    # Реалистичный user-agent
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    
    browser = webdriver.Chrome(service=service, options=options)
    
    # Маскировка через CDP
    browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            // Маскировка webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Маскировка Selenium
            Object.defineProperty(navigator, 'selenium', {
                get: () => undefined
            });
            
            // Маскировка __selenium_evaluate
            Object.defineProperty(window, '__selenium_evaluate', {
                get: () => undefined
            });
            
            // Маскировка __selenium_unwrapped
            Object.defineProperty(window, '__selenium_unwrapped', {
                get: () => undefined
            });
            
            // Маскировка _Selenium_IDE_Recorder
            Object.defineProperty(window, '_Selenium_IDE_Recorder', {
                get: () => undefined
            });
            
            // Маскировка ChromeDriver
            Object.defineProperty(window, 'chrome', {
                writable: true,
                value: {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                }
            });
            
            // Эмуляция плагинов
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        name: "PDF Viewer",
                        description: "Portable Document Format",
                        mimeTypes: [
                            {type: "application/pdf", suffixes: "pdf"},
                            {type: "text/pdf", suffixes: "pdf"}
                        ]
                    },
                    {
                        name: "Chrome PDF Viewer",
                        description: "Portable Document Format",
                        mimeTypes: [
                            {type: "application/pdf", suffixes: "pdf"},
                            {type: "text/pdf", suffixes: "pdf"}
                        ]
                    },
                    {
                        name: "Chromium PDF Viewer",
                        description: "Portable Document Format",
                        mimeTypes: [
                            {type: "application/pdf", suffixes: "pdf"},
                            {type: "text/pdf", suffixes: "pdf"}
                        ]
                    },
                    {
                        name: "Microsoft Edge PDF Viewer",
                        description: "Portable Document Format",
                        mimeTypes: [
                            {type: "application/pdf", suffixes: "pdf"},
                            {type: "text/pdf", suffixes: "pdf"}
                        ]
                    },
                    {
                        name: "WebKit built-in PDF",
                        description: "Portable Document Format",
                        mimeTypes: [
                            {type: "application/pdf", suffixes: "pdf"},
                            {type: "text/pdf", suffixes: "pdf"}
                        ]
                    }
                ]
            });
            
            // Эмуляция языков
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ru-RU']
            });
            
            // Эмуляция WebGL
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Google Inc. (Apple)';
                }
                if (parameter === 37446) {
                    return 'ANGLE (Apple, ANGLE Metal Renderer: Apple M2 Pro, Unspecified Version)';
                }
                return getParameter.apply(this, arguments);
            };
            
            // Эмуляция разрешения экрана
            Object.defineProperty(screen, 'width', {
                get: () => 1920
            });
            Object.defineProperty(screen, 'height', {
                get: () => 1080
            });
            Object.defineProperty(screen, 'availWidth', {
                get: () => 1920
            });
            Object.defineProperty(screen, 'availHeight', {
                get: () => 1080
            });
            
            // Эмуляция цветовой глубины
            Object.defineProperty(screen, 'colorDepth', {
                get: () => 24
            });
            Object.defineProperty(screen, 'pixelDepth', {
                get: () => 24
            });
            
            // Эмуляция ориентации
            Object.defineProperty(screen, 'orientation', {
                get: () => ({
                    type: 'landscape-primary',
                    angle: 0
                })
            });
            
            // Эмуляция WebGL
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type, ...args) {
                const context = originalGetContext.apply(this, [type, ...args]);
                if (type === 'webgl') {
                    const originalGetParameter = context.getParameter;
                    context.getParameter = function(parameter) {
                        if (parameter === 37445) {
                            return 'Google Inc. (Apple)';
                        }
                        if (parameter === 37446) {
                            return 'ANGLE (Apple, ANGLE Metal Renderer: Apple M2 Pro, Unspecified Version)';
                        }
                        return originalGetParameter.apply(this, arguments);
                    };
                }
                return context;
            };
            
            // Эмуляция WebRTC
            const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
            navigator.mediaDevices.getUserMedia = function(constraints) {
                return Promise.resolve({
                    getTracks: () => []
                });
            };
        '''
    })
    
    # Установка дополнительных заголовков
    browser.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": user_agent,
        "platform": "MacIntel",
        "acceptLanguage": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "platformVersion": "10_15_7"
    })
    
    # Установка геолокации (Москва)
    browser.execute_cdp_cmd('Emulation.setGeolocationOverride', {
        "latitude": 55.7558,
        "longitude": 37.6173,
        "accuracy": 100
    })
    
    browser.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    print("Chrome запущен в стелс-режиме.")
    
    # Добавляем случайную задержку перед первым действием
    random_delay(2, 4)

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

def random_delay(min_seconds=1, max_seconds=3):
    """Случайная задержка между действиями"""
    delay = random.uniform(min_seconds, max_seconds)
    t.sleep(delay)

def simulate_human_behavior():
    """Имитация случайного поведения пользователя"""
    try:
        # Получаем размеры окна
        window_size = browser.get_window_size()
        max_x = min(window_size['width'] // 4, 50)  # Ограничиваем движение 1/4 ширины или 50px
        max_y = min(window_size['height'] // 4, 50)  # Ограничиваем движение 1/4 высоты или 50px
        
        actions = ActionChains(browser)
        # Случайное движение мыши в пределах безопасной зоны
        for _ in range(random.randint(2, 3)):
            actions.move_by_offset(
                random.randint(-max_x, max_x),
                random.randint(-max_y, max_y)
            )
            random_delay(0.1, 0.2)
        actions.perform()
    except Exception as e:
        print(f"Пропускаем симуляцию движения мыши: {str(e)}")

def human_like_click(element):
    """Имитация человеческого клика с движением мыши"""
    try:
        # Сначала просто перемещаемся к элементу
        actions = ActionChains(browser)
        actions.move_to_element(element)
        actions.perform()
        random_delay(0.2, 0.3)
        
        # Небольшое случайное движение вокруг элемента
        actions = ActionChains(browser)
        actions.move_by_offset(random.randint(-2, 2), random.randint(-2, 2))
        actions.perform()
        random_delay(0.1, 0.2)
        
        # Клик
        element.click()
        random_delay(0.1, 0.2)
    except Exception as e:
        print(f"Ошибка при клике: {str(e)}")
        # Пробуем прямой клик как запасной вариант
        element.click()

def joinMeeting(link):
    global browser
    if link == '':
        return
    
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Попытка подключения {attempt + 1} из {MAX_RETRIES}")
            
            if attempt == 0:
                browser.get(link)
            else:
                print("Перезагружаем страницу...")
                browser.refresh()
            
            if not wait_for_page_load():
                continue
                
            try:
                # Устанавливаем размер окна
                browser.set_window_size(1024, 768)
                random_delay(2, 3)
                
                # Ждем загрузки страницы
                wait_for_page_load()
                print("Страница загружена")
                
                # Проверяем наличие элемента "Подготовка..."
                try:
                    preparation_element = WebDriverWait(browser, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@class='OMfBQ' and @jsname='OQ2Y6' and contains(text(), 'Подготовка')]"))
                    )
                    if preparation_element.is_displayed():
                        print("Обнаружен экран подготовки, открываем конференцию в новой вкладке...")
                        # Открываем текущую ссылку в новой вкладке
                        browser.execute_script("window.open(arguments[0], '_blank');", link)
                        random_delay(1, 2)
                        # Переключаемся на новую вкладку
                        browser.switch_to.window(browser.window_handles[-1])
                        print("Переключились на новую вкладку")
                        random_delay(2, 3)
                except Exception as e:
                    print("Экран подготовки не обнаружен, продолжаем в текущей вкладке")
                
                print("Пытаемся найти и нажать кнопку 'Продолжить с отключенными микрофоном и камерой'...")
                try:
                    continue_button = WebDriverWait(browser, ELEMENT_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, "//span[@jsname='V67aGc' and @class='mUIrbf-vQzf8d' and contains(text(), 'Продолжить с отключенными микрофоном и камерой')]"))
                    )
                    
                    if continue_button.is_displayed():
                        print("Кнопка найдена и видна на странице")
                        print("Прокручиваем страницу до кнопки...")
                        browser.execute_script("arguments[0].scrollIntoView(true);", continue_button)
                        random_delay(1, 2)
                        
                        print("Пытаемся нажать на кнопку...")
                        browser.execute_script("arguments[0].click();", continue_button)
                        print("Кнопка успешно нажата")
                        random_delay(2, 3)
                        
                        # Проверяем успешное подключение к конференции
                        print("Проверяем успешное подключение к конференции...")
                        try:
                            meeting_room_icon = WebDriverWait(browser, ELEMENT_TIMEOUT).until(
                                EC.presence_of_element_located((By.XPATH, "//i[@class='google-material-icons notranslate gxJzEf' and @aria-hidden='true' and contains(text(), 'meeting_room')]"))
                            )
                            if meeting_room_icon.is_displayed():
                                print("Успешно подключились к конференции!")
                                return True
                            else:
                                print("Иконка конференции найдена, но не видна на странице")
                        except Exception as e:
                            print(f"Не удалось найти иконку конференции: {str(e)}")
                    else:
                        print("Кнопка найдена, но не видна на странице")
                except Exception as e:
                    print(f"Не удалось найти или нажать кнопку: {str(e)}")
                
                # Ждем, пока перекрывающий элемент исчезнет
                WebDriverWait(browser, ELEMENT_TIMEOUT).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "rqEaD"))
                )
                print("Перекрывающий элемент исчез")
                
                # Проверяем, не появилось ли сообщение об ошибке доступа
                try:
                    error_message = WebDriverWait(browser, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//h1[@jsname='r4nke' and @class='roSPhc']"))
                    )
                    if error_message.is_displayed():
                        print("Обнаружено сообщение об ошибке доступа!")
                        print(f"Текст ошибки: {error_message.text}")
                        return False
                except:
                    print("Сообщение об ошибке доступа не найдено, продолжаем...")
                
                # Проверяем появление заголовка о микрофоне и камере
                try:
                    mic_cam_header = WebDriverWait(browser, ELEMENT_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, "//h1[@class='sZZjvf' and contains(text(), 'Хотите, чтобы другие участники встречи видели и слышали вас?')]"))
                    )
                    if mic_cam_header.is_displayed():
                        print("Обнаружен заголовок о микрофоне и камере")
                        
                        # Ищем и нажимаем кнопку "Продолжить с отключенными микрофоном и камерой"
                        continue_button = WebDriverWait(browser, ELEMENT_TIMEOUT).until(
                            EC.presence_of_element_located((By.XPATH, "//span[@jsname='V67aGc' and @class='mUIrbf-vQzf8d' and contains(text(), 'Продолжить с отключенными микрофоном и камерой')]"))
                        )
                        
                        if continue_button.is_displayed():
                            print("Найдена кнопка продолжения с отключенными устройствами")
                            browser.execute_script("arguments[0].scrollIntoView(true);", continue_button)
                            random_delay(1, 2)
                            browser.execute_script("arguments[0].click();", continue_button)
                            print("Нажали кнопку продолжить с отключенными микрофоном и камерой")
                            random_delay(2, 3)
                        else:
                            print("Кнопка продолжения не видна на странице")
                except Exception as e:
                    print(f"Ошибка при обработке заголовка о микрофоне и камере: {str(e)}")
                
                # Нажатие кнопки "Продолжить с отключенными микрофоном и камерой"
                button_xpath = "//span[@jsname='V67aGc' and @class='mUIrbf-vQzf8d']"
                print(f"Ищем кнопку по xpath: {button_xpath}")
                
                try:
                    print("Ожидаем появления кнопки...")
                    continue_button = WebDriverWait(browser, ELEMENT_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, button_xpath))
                    )
                    print("Кнопка найдена на странице")
                    
                    print("Проверяем видимость кнопки...")
                    if continue_button.is_displayed():
                        print("Кнопка видна на странице")
                    else:
                        print("Кнопка не видна на странице")
                    
                    print("Проверяем кликабельность кнопки...")
                    if continue_button.is_enabled():
                        print("Кнопка кликабельна")
                    else:
                        print("Кнопка не кликабельна")
                    
                    print("Получаем текст кнопки...")
                    button_text = continue_button.text
                    print(f"Текст кнопки: {button_text}")
                    
                    print("Прокручиваем к кнопке...")
                    browser.execute_script("arguments[0].scrollIntoView(true);", continue_button)
                    random_delay(1, 2)
                    print("Прокрутили к кнопке")
                    
                    print("Пробуем клик через JavaScript...")
                    browser.execute_script("arguments[0].click();", continue_button)
                    print("JavaScript клик выполнен")
                    
                    print("Проверяем, что кнопка исчезла...")
                    try:
                        WebDriverWait(browser, 5).until(
                            EC.invisibility_of_element_located((By.XPATH, button_xpath))
                        )
                        print("Кнопка успешно исчезла после клика")
                    except:
                        print("Кнопка все еще видна после клика")
                    
                    print("Нажали кнопку продолжить с отключенными микрофоном и камерой")
                    random_delay(2, 3)
                except Exception as e:
                    print(f"Ошибка при нажатии на кнопку: {str(e)}")
                    print("Пробуем альтернативный способ клика...")
                    try:
                        print("Пробуем клик через ActionChains...")
                        ActionChains(browser).move_to_element(continue_button).click().perform()
                        print("ActionChains клик выполнен")
                    except Exception as e:
                        print(f"Ошибка при альтернативном клике: {str(e)}")
                        print("Пробуем прямой клик...")
                        continue_button.click()
                        print("Прямой клик выполнен")
                
                # Ввод имени
                print("Пытаемся найти поле для ввода имени...")
                try:
                    name_input = WebDriverWait(browser, ELEMENT_TIMEOUT).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@jsname='YPqjbf' and @aria-label='Укажите свое имя']"))
                    )
                    
                    if name_input.is_displayed():
                        print("Поле для ввода имени найдено")
                        # Прокручиваем к элементу
                        browser.execute_script("arguments[0].scrollIntoView(true);", name_input)
                        random_delay(1, 2)
                        
                        # Фокус на поле ввода
                        name_input.click()
                        random_delay(0.5, 1)
                        
                        # Имитируем ввод через клавиатуру
                        actions = ActionChains(browser)
                        actions.send_keys("Rinat Galyamov")
                        actions.perform()
                        print("Ввели имя через клавиатуру")
                        random_delay(0.8, 1.2)
                        
                        # Ждем появления кнопки "Присоединиться"
                        print("Ожидаем появления кнопки 'Присоединиться'...")
                        join_button = WebDriverWait(browser, ELEMENT_TIMEOUT).until(
                            EC.presence_of_element_located((By.XPATH, "//span[@jsname='V67aGc' and @class='UywwFc-vQzf8d' and contains(text(), 'Присоединиться')]"))
                        )
                        
                        if join_button.is_displayed():
                            print("Кнопка 'Присоединиться' появилась")
                            browser.execute_script("arguments[0].scrollIntoView(true);", join_button)
                            random_delay(1, 2)
                            browser.execute_script("arguments[0].click();", join_button)
                            print("Нажали кнопку 'Присоединиться'")
                            random_delay(2, 3)
                            
                            # Проверяем успешное подключение к конференции
                            print("Проверяем успешное подключение к конференции...")
                            try:
                                meeting_room_icon = WebDriverWait(browser, ELEMENT_TIMEOUT).until(
                                    EC.presence_of_element_located((By.XPATH, "//i[@class='google-material-icons notranslate gxJzEf' and @aria-hidden='true' and contains(text(), 'meeting_room')]"))
                                )
                                if meeting_room_icon.is_displayed():
                                    print("Успешно подключились к конференции!")
                                    return True
                                else:
                                    print("Иконка конференции найдена, но не видна на странице")
                            except Exception as e:
                                print(f"Не удалось найти иконку конференции: {str(e)}")
                        else:
                            print("Кнопка 'Присоединиться' не видна на странице")
                    else:
                        print("Поле для ввода имени не видно на странице")
                except Exception as e:
                    print(f"Ошибка при вводе имени: {str(e)}")
                
                # Отключение микрофона и камеры
                mic_button = WebDriverWait(browser, ELEMENT_TIMEOUT).until(
                    EC.element_to_be_clickable((By.XPATH, MIC_XPATH))
                )
                browser.execute_script("arguments[0].click();", mic_button)
                random_delay(1, 1.5)
                
                camera_button = WebDriverWait(browser, ELEMENT_TIMEOUT).until(
                    EC.element_to_be_clickable((By.XPATH, WEBCAM_XPATH))
                )
                browser.execute_script("arguments[0].click();", camera_button)
                random_delay(1.5, 2)
                
                # Финальное присоединение
                join_button = WebDriverWait(browser, ELEMENT_TIMEOUT).until(
                    EC.element_to_be_clickable((By.XPATH, JOIN_XPATH))
                )
                browser.execute_script("arguments[0].click();", join_button)
                print("Нажали кнопку присоединиться")
                return True
                
            except Exception as e:
                print(f"Ошибка при выполнении действий: {str(e)}")
                continue
                
        except Exception as e:
            print(f"Ошибка при выполнении попытки подключения: {str(e)}")
            continue
            
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
        # Случайная задержка перед завершением
        random_delay(1, 2)
        
        # Находим и кликаем по кнопке завершения встречи
        hang_up_button = WebDriverWait(browser, ELEMENT_TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, HANG_UP_BTN_XPATH))
        )
        
        # Имитируем человеческий клик
        human_like_click(hang_up_button)
        print("Встреча успешно завершена")
        return True
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
