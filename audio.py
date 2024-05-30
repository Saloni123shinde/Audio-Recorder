import pyaudio
import wave
import numpy as np

class AudioRecorder:
    def __init__(self):
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 2
        self.rate = 44100  # Record at 44100 samples per second
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.recording = False
        self.level_callback = None

    def start_recording(self):
        self.frames = []
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunk)
        self.recording = True

    def stop_recording(self, file_name):
        self.recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        wf = wave.open(file_name, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def record(self):
        if self.recording:
            data = self.stream.read(self.chunk)
            self.frames.append(data)
            if self.level_callback:
                self.level_callback(self.get_audio_level(data))

    def get_audio_level(self, data):
        audio_data = np.frombuffer(data, dtype=np.int16)
        level = np.abs(audio_data).mean()
        return level
import tkinter as tk
from tkinter import ttk, filedialog
import threading
from PIL import Image, ImageTk

class AudioRecorderApp:
    def __init__(self, root):
        self.recorder = AudioRecorder()
        self.recorder.level_callback = self.update_level_meter
        self.is_recording = False
        self.root = root
        self.root.title("Creative Audio Recorder")
        
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Helvetica', 12))

        self.start_img = ImageTk.PhotoImage(Image.open("C:/Users/91741/Desktop/sart.jpg").resize((50, 50)))
        self.stop_img = ImageTk.PhotoImage(Image.open("C:/Users/91741/Desktop/stop.jpg").resize((50, 50)))

        self.start_button = ttk.Button(root, image=self.start_img, command=self.start_recording)
        self.start_button.pack(pady=20)

        self.stop_button = ttk.Button(root, image=self.stop_img, command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=20)

        self.status_label = ttk.Label(root, text="Status: Ready", font=('Helvetica', 14))
        self.status_label.pack(pady=10)

        self.level_meter = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate')
        self.level_meter.pack(pady=10)

    def start_recording(self):
        self.is_recording = True
        self.status_label.config(text="Status: Recording...")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.recorder.start_recording()
        self.recording_thread = threading.Thread(target=self.record)
        self.recording_thread.start()

    def stop_recording(self):
        self.is_recording = False
        self.status_label.config(text="Status: Saving...")
        self.recorder.stop_recording(filedialog.asksaveasfilename(defaultextension=".wav",
                                                                  filetypes=[("WAV files", "*.wav")]))
        self.status_label.config(text="Status: Ready")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def record(self):
        while self.is_recording:
            self.recorder.record()

    def update_level_meter(self, level):
        self.level_meter['value'] = min(level / 32768 * 100, 100)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioRecorderApp(root)
    root.mainloop()
