import meetings
import browser_manager
import schedule
import time
import os

browser_manager.initFirefox()

# Сохраняем время последней модификации файла расписания
last_modified = os.path.getmtime(meetings.SCHEDULE_FILE)
meetings.setup_schedule()

def check_schedule_updates():
    """Проверяет, было ли обновлено расписание"""
    global last_modified
    current_modified = os.path.getmtime(meetings.SCHEDULE_FILE)
    if current_modified > last_modified:
        print("\nОбнаружено обновление расписания!")
        meetings.update_schedule()
        last_modified = current_modified

# Проверяем обновления каждые 30 секунд
schedule.every(30).seconds.do(check_schedule_updates)

while True:
    schedule.run_pending()
    time.sleep(1)
