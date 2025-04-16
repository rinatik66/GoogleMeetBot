from browser_manager import initChrome, joinMeeting, hangUpMeeting
import time

def test_meet_connection():
    print("Начинаем тестирование подключения к Google Meet...")
    
    # Инициализируем Chrome
    initChrome()
    
    try:
        # Тестовая ссылка на Google Meet
        test_link = "https://meet.google.com/afv-qcrq-nxq"
        
        print("Пытаемся подключиться к встрече...")
        if joinMeeting(test_link):
            print("Успешно подключились к встрече!")
            # Ждем 30 секунд для проверки стабильности соединения
            time.sleep(30)
        else:
            print("Не удалось подключиться к встрече")
            
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
    finally:
        # Завершаем встречу
        print("Завершаем встречу...")
        hangUpMeeting()
        print("Тест завершен")

if __name__ == "__main__":
    test_meet_connection() 