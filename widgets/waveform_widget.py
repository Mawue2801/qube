import os
import numpy as np
import pyaudio
from pydub import AudioSegment
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPixmap, QPen
from PyQt5.QtCore import Qt, QTimer, QPointF, pyqtSignal, QObject

class WaveformWidget(QWidget):
    audio_finished = pyqtSignal()  # Define the signal for audio completion

    def __init__(self):
        super().__init__()
        self.setMinimumSize(350, 350)
        self.num_lines = 720
        self.data = np.zeros(self.num_lines)
        self.filtered_data = np.zeros(self.num_lines)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_waveform)
        self.timer.start(16)  # roughly 60 FPS
        self.audio_segment = None
        self.audio_stream = None
        self.audio_data = None
        self.position = 0
        self.audio_played = False

        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.dirname(script_dir)
        assets_dir = os.path.join(root_dir, "assets")

        logo_path = os.path.join(assets_dir, "images/logo.png")

        self.logo = QPixmap(logo_path)
        self.logo_aspect_ratio = self.logo.width() / self.logo.height()
        self.filter_window_size = 10

    def load_audio_file(self, file_path):
        self.audio_segment = AudioSegment.from_file(file_path)
        self.audio_data = np.array(self.audio_segment.get_array_of_samples())
        self.audio_data = self.audio_data / np.max(np.abs(self.audio_data))
        self.position = 0
        self.audio_played = False

        self.p = pyaudio.PyAudio()
        self.audio_stream = self.p.open(format=pyaudio.paInt16,
                                  channels=self.audio_segment.channels,
                                  rate=self.audio_segment.frame_rate,
                                  output=True)

    def update_waveform(self):
        if self.audio_data is None or self.audio_played:
            return

        chunk_size = 1024
        if self.position + chunk_size >= len(self.audio_data):
            self.audio_played = True
            self.reset_waveform()
            if self.audio_stream and not self.audio_stream.is_stopped():
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.p.terminate()

            self.audio_finished.emit()  # Emit the signal when audio playback is complete

        if not self.audio_played:
            audio_chunk = self.audio_data[self.position:self.position + chunk_size]
            self.position += chunk_size

            audio_chunk_int16 = (audio_chunk * 32767).astype(np.int16)
            if self.audio_stream and not self.audio_stream.is_stopped():
                self.audio_stream.write(audio_chunk_int16.tobytes())

            self.data = np.abs(np.fft.fft(audio_chunk))[:self.num_lines]
            max_value = np.max(self.data)
            if max_value != 0:
                self.data = self.data / max_value

            self.filtered_data = np.convolve(self.data, np.ones(self.filter_window_size) / self.filter_window_size, mode='same')
            self.update()

    def reset_waveform(self):
        self.data = np.zeros(self.num_lines)
        self.filtered_data = np.zeros(self.num_lines)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        size = min(self.rect().width(), self.rect().height())
        radius = size * 0.2

        center = self.rect().center()

        logo_size = min(radius * 2, radius * 2 * self.logo_aspect_ratio * 0.5)
        scaled_logo = self.logo.scaled(int(logo_size), int(logo_size), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_rect = scaled_logo.rect()
        logo_rect.moveCenter(center)
        painter.drawPixmap(logo_rect, scaled_logo)

        pen = QPen(QColor(51, 1, 69))
        pen.setWidth(2)
        painter.setPen(pen)

        for i in range(self.num_lines):
            angle = np.radians(i * 360 / self.num_lines)
            length = self.filtered_data[i] * 100
            x1 = radius * np.cos(angle) + center.x()
            y1 = radius * np.sin(angle) + center.y()
            x2 = (radius + length) * np.cos(angle) + center.x()
            y2 = (radius + length) * np.sin(angle) + center.y()
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
