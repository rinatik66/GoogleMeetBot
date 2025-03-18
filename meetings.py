import time as t
import schedule
import browser_manager
from datetime import datetime
import csv
import os
import tempfile
import shutil

SCHEDULE_FILE = "schedule.csv"
CSV_HEADERS = ['Name', 'When', 'Start', 'End', 'Link']

def load_schedule():
    """Загружает расписание из CSV файла"""
    if not os.path.exists(SCHEDULE_FILE):
        # Создаем файл с заголовками если его нет
        with open(SCHEDULE_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(CSV_HEADERS)
        return []
    
    meetings = []
    with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
        # Пропускаем BOM если есть
        content = f.read()
        if content.startswith('\ufeff'):
            content = content[1:]
        
        # Читаем CSV из строки
        reader = csv.DictReader(content.splitlines(), delimiter=';')
        for row in reader:
            try:
                meetings.append({
                    'name': row['Name'].strip(),
                    'day': row['When'].strip(),
                    'start_time': row['Start'].strip(),
                    'end_time': row['End'].strip(),
                    'link': row['Link'].strip()
                })
            except KeyError as e:
                print(f"Ошибка в формате CSV: отсутствует колонка {e}")
                continue
            except Exception as e:
                print(f"Ошибка при чтении строки: {e}")
                continue
    return meetings

def save_schedule(meetings):
    """Сохраняет расписание в CSV файл с использованием временного файла"""
    # Создаем временный файл
    temp_fd, temp_path = tempfile.mkstemp(suffix='.csv')
    try:
        with os.fdopen(temp_fd, 'w', encoding='utf-8', newline='') as temp_file:
            writer = csv.writer(temp_file, delimiter=';')
            writer.writerow(CSV_HEADERS)
            for meeting in meetings:
                writer.writerow([
                    meeting['name'],
                    meeting['day'],
                    meeting['start_time'],
                    meeting['end_time'],
                    meeting['link'].rstrip('%')
                ])
        
        # Пытаемся заменить оригинальный файл
        try:
            shutil.move(temp_path, SCHEDULE_FILE)
        except PermissionError:
            print(f"Ошибка: Не удалось сохранить изменения в {SCHEDULE_FILE}.")
            print("Пожалуйста, закройте файл в Excel или других программах и попробуйте снова.")
            return False
        return True
    except Exception as e:
        print(f"Ошибка при сохранении расписания: {e}")
        return False
    finally:
        # Удаляем временный файл если он все еще существует
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass

def clear_schedule():
    """Очищает текущее расписание"""
    schedule.clear()
    # Создаем пустой файл только с заголовками
    try:
        with open(SCHEDULE_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(CSV_HEADERS)
        print("Расписание очищено")
    except PermissionError:
        print(f"Ошибка: Не удалось очистить {SCHEDULE_FILE}.")
        print("Пожалуйста, закройте файл в Excel или других программах и попробуйте снова.")

def update_schedule():
    """Обновляет расписание из файла"""
    # Очищаем текущее расписание
    schedule.clear()
    
    # Загружаем новое расписание
    meetings = load_schedule()
    
    # Применяем каждую встречу
    for meeting in meetings:
        scheduleMeeting(
            meeting['day'],
            meeting['start_time'],
            meeting['end_time'],
            meeting['link'],
            meeting['name']
        )
    
    print(f"Расписание обновлено. Загружено {len(meetings)} встреч.")

def add_meeting(day, start_time, end_time, link, name):
    """Добавляет новую встречу в расписание"""
    meetings = load_schedule()
    
    # Добавляем новую встречу
    meetings.append({
        'name': name,
        'day': day,
        'start_time': start_time,
        'end_time': end_time,
        'link': link
    })
    
    # Сохраняем обновленное расписание
    if save_schedule(meetings):
        # Обновляем активное расписание только если сохранение прошло успешно
        update_schedule()
        print(f"Встреча '{name}' добавлена в расписание")
    else:
        print(f"Не удалось добавить встречу '{name}' в расписание")

def remove_meeting(name):
    """Удаляет встречу из расписания по имени"""
    meetings = load_schedule()
    
    # Фильтруем встречи, исключая встречу с указанным именем
    updated_meetings = [m for m in meetings if m['name'] != name]
    
    if len(updated_meetings) < len(meetings):
        # Сохраняем обновленное расписание
        if save_schedule(updated_meetings):
            # Обновляем активное расписание только если сохранение прошло успешно
            update_schedule()
            print(f"Встреча '{name}' удалена из расписания")
        else:
            print(f"Не удалось удалить встречу '{name}' из расписания")
    else:
        print(f"Встреча '{name}' не найдена в расписании")

def list_meetings():
    """Выводит список всех запланированных встреч"""
    meetings = load_schedule()
    if not meetings:
        print("Расписание пусто")
        return
    
    print("\nТекущее расписание:")
    for meeting in meetings:
        print(f"- {meeting['name']}: {meeting['day']} {meeting['start_time']}-{meeting['end_time']}")

def setup_schedule():
    """Инициализация расписания при запуске"""
    # Всегда загружаем из файла
    update_schedule()

def scheduleMeeting(day, startHour, endHour, link, name):
    """Планирует встречу в schedule"""
    def start_meeting_and_record():
        print(f"Запуск встречи '{name}' по ссылке {link}")
        browser_manager.joinMeeting(link)
        # Формируем имя файла записи: имя конференции + текущая метка времени
        filename = f"recordings/{t.strftime('%Y%m%d_%H%M%S')}_{name}.mp4"
        browser_manager.startRecordingUnified(filename)
    
    def stop_meeting_and_record():
        print(f"Завершение встречи '{name}'")
        browser_manager.hangUpMeeting()
        browser_manager.stopRecordingUnified()
    
    if str(day).lower() == "today":
        schedule.every().day.at(startHour).do(start_meeting_and_record)
        schedule.every().day.at(endHour).do(stop_meeting_and_record)
    else:
        # Обработка для других дней недели
        days = {
            "monday": schedule.every().monday,
            "tuesday": schedule.every().tuesday,
            "wednesday": schedule.every().wednesday,
            "thursday": schedule.every().thursday,
            "friday": schedule.every().friday,
            "saturday": schedule.every().saturday,
            "sunday": schedule.every().sunday
        }
        
        day_schedule = days.get(str(day).lower())
        if day_schedule:
            day_schedule.at(startHour).do(start_meeting_and_record)
            day_schedule.at(endHour).do(stop_meeting_and_record)
        else:
            print(f"Неверный день недели: {day}")