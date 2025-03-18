import subprocess
import argparse
from datetime import datetime
import os
import signal
import time

def start_recording(output_filename=None, duration=None):
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"audio_recording_{timestamp}.wav"
    
    # Создаём директорию для выходного файла если нужно
    output_dir = os.path.dirname(output_filename)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Базовая команда для записи аудио
    cmd = [
        "ffmpeg",
        "-f", "avfoundation",
        "-i", ":BlackHole",
        "-af", "volume=2.5",  # Увеличиваем громкость до 250%
    ]
    
    # Добавляем длительность, если указана
    if duration:
        cmd.extend(["-t", str(duration)])
    
    # Добавляем выходной файл
    cmd.extend([output_filename])
    
    # Запускаем процесс с возможностью отправки команд через stdin
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    return process, output_filename

def stop_recording(process):
    if process.poll() is None:  # Если процесс всё ещё работает
        try:
            # Отправляем 'q' для плавной остановки
            process.communicate(input=b'q', timeout=10)
        except subprocess.TimeoutExpired:
            # Если не удалось остановить плавно, пробуем terminate()
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Если и это не сработало, используем kill()
                process.kill()
                process.wait()

def main():
    parser = argparse.ArgumentParser(description='Record audio from BlackHole')
    parser.add_argument('--duration', type=int, help='Recording duration in seconds')
    args = parser.parse_args()

    print(f"Starting audio recording{f' for {args.duration} seconds' if args.duration else ''}")
    process, output_file = start_recording(duration=args.duration)
    
    try:
        if args.duration:
            # Если указана длительность, ждём завершения
            process.wait()
        else:
            # Иначе ждём Ctrl+C
            while process.poll() is None:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping recording...")
    finally:
        stop_recording(process)
        print(f"Recording saved to: {output_file}")

if __name__ == "__main__":
    main()
