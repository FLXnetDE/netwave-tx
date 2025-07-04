import sys
import socket
import struct
import threading
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout)
from PyQt5.QtGui import QCloseEvent
import keyboard
import pyaudio

from components import DeviceLayout, StatusLayout

# --- Configuration ---
CLIENT_ID = 1999
CHANNEL_ID = 10
UDP_IP = "127.0.0.1"
UDP_PORT = 5000
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
PTT_KEY = "space"

class AudioApp(QWidget):
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("netwave-tx")
        self.setFixedSize(600, 200)

        self.audio = pyaudio.PyAudio()
        self.audio_input = None
        self.audio_output = None

        # Flag to control sending
        self.is_talking = threading.Event()

        # Flag to control app shutdown
        self.shutdown = threading.Event()

        self.init_ui()
        self.init_socket()

        # Threads
        self.threads = [
            threading.Thread(target=self.audio_sender, daemon=True),
            threading.Thread(target=self.audio_receiver, daemon=True),
            threading.Thread(target=self.push_to_talk_monitor, daemon=True)
        ]

        for t in self.threads:
            t.start()

    def init_ui(self):
        layout = QVBoxLayout()

        # Device selection
        self.dev_layout = DeviceLayout(self.audio)
        layout.addLayout(self.dev_layout)

        # Status
        self.status_layout = StatusLayout()
        layout.addLayout(self.status_layout)

        self.setLayout(layout)

    def init_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(("", 0))

    def audio_sender(self):
        while not self.dev_layout.input_combo.count():
            time.sleep(0.1)

        input_index = self.dev_layout.input_combo.currentData()
        self.audio_input = self.audio.open(format=FORMAT,
                                         channels=CHANNELS,
                                         rate=RATE,
                                         input=True,
                                         input_device_index=input_index,
                                         frames_per_buffer=CHUNK)
        
        while not self.shutdown.is_set():

            if self.is_talking.is_set():
                try:
                    self.status_layout.set_tx(True)
                    data = self.audio_input.read(CHUNK, exception_on_overflow=False)
                    packet = struct.pack("!I", CHANNEL_ID) + struct.pack("!I", CLIENT_ID) + data
                    self.sock.sendto(packet, (UDP_IP, UDP_PORT))
                except Exception as err:
                    print(f"[Sender] Error on sending packets :: {err}")

            else:
                self.status_layout.set_tx(False)
                time.sleep(0)

    def audio_receiver(self):
        while not self.dev_layout.output_combo.count():
            time.sleep(0.1)

        output_index = self.dev_layout.output_combo.currentData()
        self.audio_output = self.audio.open(format=FORMAT,
                                         channels=CHANNELS,
                                         rate=RATE,
                                         output=True,
                                         output_device_index=output_index,
                                         frames_per_buffer=CHUNK)
        
        rx_grace_period = 0.2  # seconds
        last_rx_time = 0

        self.sock.settimeout(0.05)

        while not self.shutdown.is_set():
            received_valid_packet = False
            try:
                packet, _ = self.sock.recvfrom(4096)
                if len(packet) > 8:
                    recv_channel, = struct.unpack("!I", packet[:4])
                    if recv_channel == CHANNEL_ID:
                        self.audio_output.write(packet[8:])

                        last_rx_time = time.time()
                        received_valid_packet = True
            except socket.timeout:
                pass
            except Exception as err:
                print(f"[Receiver] Error on receiving packets :: {err}")

            # Update timestamp only if valid packet
            if received_valid_packet:
                last_rx_time = time.time()

            # RX indicator logic
            rx_active = time.time() - last_rx_time < rx_grace_period
            self.status_layout.set_rx(rx_active)

            time.sleep(0.01)

    def push_to_talk_monitor(self):
        print(f"[PTT] Hold '{PTT_KEY}' to talk")
        while not self.shutdown.is_set():
            if keyboard.is_pressed(PTT_KEY):
                if not self.is_talking.is_set():
                    print("[PTT] Talking...")
                self.is_talking.set()
            else:
                if self.is_talking.is_set():
                    print("[PTT] Stopped talking")
                self.is_talking.clear()
            time.sleep(0)

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.shutdown.set()
        time.sleep(0.2)

        try:
            if self.audio_input:
                self.audio_input.close()

            if self.audio_output:
                self.audio_output.close()

            self.audio.terminate()
            self.sock.close()
        except Exception:
            pass

        if a0:
            a0.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioApp()
    window.show()
    sys.exit(app.exec_())
