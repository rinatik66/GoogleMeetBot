# Google Meet Bot

**GoogleMeetBot** — это автоматизированный бот для подключения к конференциям Google Meet в заданное время с функцией записи аудио. Бот использует Mozilla Firefox для управления браузером и FFmpeg для записи аудио через BlackHole.

## Особенности

- Автоматическое подключение к конференциям по расписанию
- Запись аудио через BlackHole с увеличенной громкостью (250%)
- Автоматическое отключение микрофона и камеры при входе
- Сохранение записей в папку `recordings/`
- Динамическое обновление расписания без перезапуска бота
- Планирование встреч через CSV файл или командную строку
- Отладка: логирование действий и скриншоты для диагностики

## Требования

- Python 3.8+
- Mozilla Firefox – [скачать](https://www.mozilla.org/ru/firefox/new/)
- Geckodriver – [скачать](https://github.com/mozilla/geckodriver/releases)
  - Для Mac M1/M2: используйте версию geckodriver-v0.36.0-macos-aarch64.tar.gz
- FFmpeg – `brew install ffmpeg` (MacOS)
- BlackHole 2ch – [скачать](https://existential.audio/blackhole/)
- Зависимости Python – перечислены в файле requirements.txt

## Установка

1. Клонируйте репозиторий:
```bash
git clone <URL_репозитория>
cd GoogleMeetBot
```

2. Создайте и активируйте виртуальное окружение:
```bash
# MacOS/Linux:
python3 -m venv venv
source venv/bin/activate

# Windows:
python -m venv venv
venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Установите Geckodriver:
```bash
# Распакуйте и переместите в /usr/local/bin
chmod +x /usr/local/bin/geckodriver
```

5. Установите и настройте BlackHole:
- Установите BlackHole 2ch
- Настройте системный звук на вывод через BlackHole
- Проверьте, что Google Meet использует BlackHole как устройство вывода

## Настройка

### Firefox Profile

1. Откройте Firefox и введите `about:profiles` в адресной строке
2. Создайте новый профиль для бота
3. В новом профиле:
   - Войдите в Google Account
   - Разрешите доступ к микрофону и камере для meet.google.com
   - Настройте автоматическое разрешение для медиа-устройств
4. Скопируйте путь из поля "Корневой каталог"

### Конфигурация проекта

1. Отредактируйте `utils.py`:
```python
FIREFOX_DVD_DIR = '/usr/local/bin/geckodriver'
FIREFOX_PROFILE = '/Users/yourusername/Library/Application Support/Firefox/Profiles/xxxxxx.default-release'
```

### Расписание встреч

Расписание хранится в `schedule.csv`:
```csv
Name;When;Start;End;Link
Daily Meeting;today;10:00;10:30;https://meet.google.com/xxx-xxxx-xxx
Weekly Sync;monday;15:00;16:00;https://meet.google.com/yyy-yyyy-yyy
```

## Использование

### Запуск бота
```bash
python gmeet_bot.py
```

### Управление расписанием

1. Через CSV файл:
   - Отредактируйте `schedule.csv` напрямую
   - Бот автоматически подхватит изменения

2. Через командную строку:
```bash
# Добавить встречу
python manage_schedule.py add --day today --start "10:00" --end "10:30" --link "https://meet.google.com/xxx" --name "Daily"

# Удалить встречу
python manage_schedule.py remove --name "Daily"

# Посмотреть расписание
python manage_schedule.py list
```

### Тестирование записи
```bash
# Запись 15 секунд
python record_audio.py --duration 15

# Запись до Ctrl+C
python record_audio.py
```

## Структура проекта

- `gmeet_bot.py` - основной скрипт бота
- `meetings.py` - управление расписанием
- `browser_manager.py` - управление браузером
- `record_audio.py` - запись аудио
- `schedule.csv` - файл расписания
- `manage_schedule.py` - управление расписанием
- `utils.py` - общие утилиты

## Селекторы (XPath)

Актуальные селекторы для Google Meet:
```python
MIC_XPATH = "//div[@role='button' and @aria-label='Выключить микрофон']"
WEBCAM_XPATH = "//div[@role='button' and @aria-label='Выключить камеру']"
JOIN_XPATH = "//button[.//span[contains(text(),'Присоединиться')]]"
HANG_UP_BTN_XPATH = "//button[@aria-label='Покинуть видеовстречу']"
```

## Решение проблем

1. Проблемы с FFmpeg:
```bash
brew install ffmpeg
```

2. Проблемы с записью аудио:
- Проверьте установку BlackHole
- Проверьте настройки звука
- Проверьте громкость системы

3. Проблемы с подключением:
- Проверьте профиль Firefox
- Проверьте селекторы
- Добавьте скриншоты для отладки:
```python
browser.save_screenshot("debug.png")
```

4. Если файл расписания заблокирован:
- Закройте файл в Excel
- Дождитесь завершения текущей операции

## Примечания

- Интерфейс Meet может меняться - периодически проверяйте селекторы
- Поддерживается одна встреча одновременно
- Записи сохраняются с меткой времени
- Громкость записи увеличена на 250%

## Лицензия

MIT License. См. файл LICENSE.