#!/bin/bash

if [ ! -f processor.pid ]; then
    echo "PID файл не найден. Процессор может быть не запущен."
    exit 1
fi

PID=$(cat processor.pid)

if ! kill $PID 2>/dev/null; then
    echo "Процессор не запущен"
    rm processor.pid
    exit 1
fi

echo "Остановка процессора (PID: $PID)..."
rm processor.pid
echo "Процессор остановлен" 