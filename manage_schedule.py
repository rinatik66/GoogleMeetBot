import meetings
import argparse

def main():
    parser = argparse.ArgumentParser(description='Управление расписанием встреч')
    subparsers = parser.add_subparsers(dest='command', help='Команды')

    # Команда для добавления встречи
    add_parser = subparsers.add_parser('add', help='Добавить новую встречу')
    add_parser.add_argument('--day', required=True, help='День недели или "today"')
    add_parser.add_argument('--start', required=True, help='Время начала (HH:MM)')
    add_parser.add_argument('--end', required=True, help='Время окончания (HH:MM)')
    add_parser.add_argument('--link', required=True, help='Ссылка на встречу')
    add_parser.add_argument('--name', required=True, help='Название встречи')

    # Команда для удаления встречи
    remove_parser = subparsers.add_parser('remove', help='Удалить встречу')
    remove_parser.add_argument('--name', required=True, help='Название встречи для удаления')

    # Команда для просмотра расписания
    subparsers.add_parser('list', help='Показать текущее расписание')

    # Команда для обновления расписания
    subparsers.add_parser('update', help='Обновить расписание из файла')

    # Команда для очистки расписания
    subparsers.add_parser('clear', help='Очистить всё расписание')

    args = parser.parse_args()

    if args.command == 'add':
        meetings.add_meeting(args.day, args.start, args.end, args.link, args.name)
    elif args.command == 'remove':
        meetings.remove_meeting(args.name)
    elif args.command == 'list':
        meetings.list_meetings()
    elif args.command == 'update':
        meetings.update_schedule()
    elif args.command == 'clear':
        meetings.clear_schedule()
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 