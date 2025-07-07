import socket
import struct
import threading
import time
import pyaudio
from config import CHANNEL_ID, CLIENT_ID, UDP_IP, UDP_PORT, CHUNK, FORMAT, CHANNELS, RATE

audio = pyaudio.PyAudio()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("", 0))

is_talking = threading.Event()

def audio_sender():
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("[Sender] Ready")
    while True:
        if is_talking.is_set():
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                packet = struct.pack("!I", CHANNEL_ID) + struct.pack("!I", CLIENT_ID) + data
                sock.sendto(packet, (UDP_IP, UDP_PORT))
            except Exception as err:
                print(f"[Sender] Error: {err}")
        else:
            time.sleep(0)

def get_socket():
    return sock

def get_audio():
    return audio

def get_talk_flag():
    return is_talking
