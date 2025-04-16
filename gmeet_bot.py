import meetings
import browser_manager
import schedule
import time
import os

# Инициализируем Chrome
browser_manager.initChrome()

# Сохраняем время последней модификации файла расписания
last_modified = os.path.getmtime(meetings.SCHEDULE_FILE)

def check_and_join_meetings():
    """Проверяет расписание и присоединяется к встречам"""
    current_time = time.strftime("%H:%M")
    meetings_to_join = meetings.get_meetings_for_time(current_time)
    
    for meeting in meetings_to_join:
        print(f"\nПытаемся присоединиться к встрече: {meeting['name']}")
        if browser_manager.joinMeeting(meeting['link']):
            print(f"Успешно присоединились к встрече: {meeting['name']}")
            # Ждем 30 секунд для проверки стабильности соединения
            time.sleep(30)
            # Завершаем встречу
            browser_manager.hangUpMeeting()
        else:
            print(f"Не удалось присоединиться к встрече: {meeting['name']}")

def check_schedule_updates():
    """Проверяет, было ли обновлено расписание"""
    global last_modified
    current_modified = os.path.getmtime(meetings.SCHEDULE_FILE)
    if current_modified > last_modified:
        print("\nОбнаружено обновление расписания!")
        meetings.update_schedule()
        last_modified = current_modified

# Проверяем расписание каждую минуту
schedule.every(1).minutes.do(check_and_join_meetings)
# Проверяем обновления расписания каждые 30 секунд
schedule.every(30).seconds.do(check_schedule_updates)

# Инициализируем расписание
meetings.setup_schedule()

print("Бот запущен и готов к работе...")

while True:
    schedule.run_pending()
    time.sleep(1)
