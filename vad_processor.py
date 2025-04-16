import os
import wave
import webrtcvad
import numpy as np
from pathlib import Path
from collections import deque

class VADProcessor:
    def __init__(self, aggressiveness=2):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.frame_duration = 30  # ms
        self.sample_rate = 16000  # Hz
        self.frame_size = int(self.sample_rate * self.frame_duration / 1000)
        self.padding_duration = 300  # 300ms тишины до и после речи
        self.padding_frames = int(self.padding_duration / self.frame_duration)
        self.speech_window = 5  # Количество фреймов в скользящем окне

    def read_wave(self, path):
        with wave.open(path, 'rb') as wf:
            sample_rate = wf.getframerate()
            if sample_rate != self.sample_rate:
                raise ValueError(f"Sample rate must be {self.sample_rate} Hz")
            pcm_data = wf.readframes(wf.getnframes())
            return pcm_data

    def write_wave(self, path, audio):
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio)

    def process_audio(self, input_path, output_path):
        # Создаем директорию для выходных файлов, если она не существует
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Читаем аудиофайл
        audio = self.read_wave(input_path)
        
        # Разбиваем аудио на фреймы
        frames = [audio[i:i + self.frame_size * 2] for i in range(0, len(audio), self.frame_size * 2)]
        
        # Определяем, какие фреймы содержат речь, используя скользящее окно
        is_speech_list = []
        window = deque(maxlen=self.speech_window)
        
        # Сначала определяем речь для каждого фрейма
        for frame in frames:
            if len(frame) < self.frame_size * 2:
                is_speech_list.append(False)
                continue
                
            is_speech = self.vad.is_speech(frame, self.sample_rate)
            window.append(is_speech)
            # Считаем фрейм речью, если больше половины окна содержит речь
            is_speech_list.append(sum(window) > len(window) / 2)
        
        # Добавляем паддинг вокруг речи
        speech_frames = []
        padding_buffer = []
        in_speech = False
        
        for i, (frame, is_speech) in enumerate(zip(frames, is_speech_list)):
            if is_speech and not in_speech:
                # Начало речи - добавляем предыдущие фреймы как паддинг
                start_padding = max(0, i - self.padding_frames)
                speech_frames.extend(frames[start_padding:i])
                in_speech = True
            
            if in_speech:
                speech_frames.append(frame)
                
            if not is_speech and in_speech:
                # Конец речи - добавляем следующие фреймы как паддинг
                end_padding = min(len(frames), i + self.padding_frames)
                speech_frames.extend(frames[i:end_padding])
                in_speech = False
        
        # Объединяем фреймы с речью
        processed_audio = b''.join(speech_frames)
        
        # Сохраняем результат
        self.write_wave(output_path, processed_audio)

def process_recordings():
    input_dir = "recordings_wav"
    output_dir = "recordings_processed"
    
    vad_processor = VADProcessor()
    
    # Обрабатываем все .wav файлы в директории recordings_wav
    for filename in os.listdir(input_dir):
        if filename.endswith(".wav"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            print(f"Обработка файла: {filename}")
            try:
                vad_processor.process_audio(input_path, output_path)
                print(f"Файл сохранен: {output_path}")
            except Exception as e:
                print(f"Ошибка при обработке файла {filename}: {str(e)}")

if __name__ == "__main__":
    process_recordings() 