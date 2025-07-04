from PyQt5.QtWidgets import (QLabel, QComboBox, QHBoxLayout)
from PyQt5.QtCore import (Qt)
from pyaudio import PyAudio

class DeviceLayout(QHBoxLayout):

    def __init__(self, audio: PyAudio):
        super().__init__()

        self.audio = audio

        self.input_combo = QComboBox()
        self.output_combo = QComboBox()
        self.input_combo.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.output_combo.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.addWidget(QLabel("Input:"))
        self.addWidget(self.input_combo)

        self.addWidget(QLabel("Output:"))
        self.addWidget(self.output_combo)

        self.refresh_audio_devices()

    def refresh_audio_devices(self):
        for i in range(self.audio.get_device_count()):
            dev = self.audio.get_device_info_by_index(i)
            name = str(dev["name"])  # Ensure name is a string
            if int(dev["maxInputChannels"]) > 0:
                self.input_combo.addItem(name, userData=i)
            if int(dev["maxOutputChannels"]) > 0:
                self.output_combo.addItem(name, userData=i)