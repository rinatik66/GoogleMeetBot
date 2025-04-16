#!/bin/bash

# Проверяем, запущен ли уже процессор
if pgrep -f "python auto_processor.py" > /dev/null; then
    echo "Процессор уже запущен"
    exit 1
fi

# Запускаем процессор в фоновом режиме
nohup python auto_processor.py > processor.log 2>&1 &

# Сохраняем PID процесса
echo $! > processor.pid

echo "Процессор запущен (PID: $(cat processor.pid))"
echo "Логи доступны в processor.log" 