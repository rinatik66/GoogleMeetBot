import os
import subprocess
from pathlib import Path

def convert_mp4_to_wav(input_dir="recordings", output_dir="recordings_wav"):
    # Создаем директорию для WAV файлов, если она не существует
    os.makedirs(output_dir, exist_ok=True)
    
    # Получаем список всех MP4 файлов
    mp4_files = [f for f in os.listdir(input_dir) if f.endswith('.mp4')]
    
    for mp4_file in mp4_files:
        input_path = os.path.join(input_dir, mp4_file)
        output_path = os.path.join(output_dir, os.path.splitext(mp4_file)[0] + '.wav')
        
        print(f"Конвертация {mp4_file} в WAV...")
        
        # Команда ffmpeg для извлечения аудио и конвертации в WAV
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ac", "1",  # Моно
            "-ar", "16000",  # Частота дискретизации 16 кГц
            "-y",  # Перезаписать существующий файл
            output_path
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Успешно: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при конвертации {mp4_file}: {e.stderr.decode()}")

if __name__ == "__main__":
    convert_mp4_to_wav() 