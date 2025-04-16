import os
import time
import subprocess
from pathlib import Path
from datetime import datetime
from vad_processor import VADProcessor

class AutoProcessor:
    def __init__(self):
        self.input_dir = "recordings"
        self.wav_dir = "recordings_wav"
        self.processed_dir = "recordings_processed"
        self.vad_processor = VADProcessor()
        self.processed_files = set()
        
        # Создаем необходимые директории
        os.makedirs(self.wav_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Загружаем список уже обработанных файлов
        self._load_processed_files()

    def _load_processed_files(self):
        """Загружаем список уже обработанных файлов"""
        processed_files_path = os.path.join(self.processed_dir, ".processed_files.txt")
        if os.path.exists(processed_files_path):
            with open(processed_files_path, 'r') as f:
                self.processed_files = set(f.read().splitlines())

    def _save_processed_files(self):
        """Сохраняем список обработанных файлов"""
        processed_files_path = os.path.join(self.processed_dir, ".processed_files.txt")
        with open(processed_files_path, 'w') as f:
            f.write('\n'.join(self.processed_files))

    def convert_to_wav(self, input_file):
        """Конвертирует видеофайл в WAV"""
        input_path = os.path.join(self.input_dir, input_file)
        output_path = os.path.join(self.wav_dir, os.path.splitext(input_file)[0] + '.wav')
        
        print(f"Конвертация {input_file} в WAV...")
        
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
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при конвертации {input_file}: {e.stderr.decode()}")
            return None

    def process_new_files(self):
        """Обрабатывает новые файлы в директории"""
        for filename in os.listdir(self.input_dir):
            if filename in self.processed_files:
                continue
                
            if not filename.endswith(('.mp4', '.mov')):
                continue
                
            print(f"\nОбнаружен новый файл: {filename}")
            
            # Конвертируем в WAV
            wav_path = self.convert_to_wav(filename)
            if not wav_path:
                continue
                
            # Обрабатываем VAD
            output_path = os.path.join(self.processed_dir, os.path.basename(wav_path))
            try:
                self.vad_processor.process_audio(wav_path, output_path)
                print(f"VAD обработка завершена: {output_path}")
                self.processed_files.add(filename)
                self._save_processed_files()
            except Exception as e:
                print(f"Ошибка при обработке VAD: {str(e)}")

    def run(self):
        """Запускает бесконечный цикл мониторинга"""
        print("Запуск автоматического процессора...")
        print("Мониторинг папки recordings для новых файлов")
        print("Поддерживаемые форматы: .mp4, .mov")
        print("Нажмите Ctrl+C для остановки")
        
        try:
            while True:
                self.process_new_files()
                time.sleep(10)  # Проверяем каждые 10 секунд
        except KeyboardInterrupt:
            print("\nОстановка процессора...")

if __name__ == "__main__":
    processor = AutoProcessor()
    processor.run() 