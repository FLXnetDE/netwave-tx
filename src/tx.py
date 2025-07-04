import threading
import socket
import pyaudio
import keyboard
import struct
import time

# Configuration
CHANNEL_ID = 1
UDP_IP = "127.0.0.1"
UDP_PORT = 5000
PUSH_TO_TALK_KEY = "space"

# Audio configuration
CHUNK = 1024                  
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Setup PyAudio
audio = pyaudio.PyAudio()

# UDP socket (broadcast enabled)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("", 0))

# Flag to control sending
is_talking = threading.Event()

def audio_sender():
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("[Sender] Ready")
    while True:
        if is_talking.is_set():
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                packet = struct.pack("!I", CHANNEL_ID) + data
                sock.sendto(packet, (UDP_IP, UDP_PORT))
            except ConnectionResetError:
                print(f"[Sender] Could not send packet to remote host (ConnectionResetError)")
        else:
            time.sleep(0)

def audio_receiver():
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        output=True,
                        frames_per_buffer=CHUNK)

    print("[Receiver] Listening on port", UDP_PORT)
    while True:
        try:
            packet, _ = sock.recvfrom(4096)
            if len(packet) > 4:
                recv_channel, = struct.unpack("!I", packet[:4])
                if recv_channel == CHANNEL_ID:
                    stream.write(packet[4:])
        except ConnectionResetError:
            print(f"[Receiver] Could not read packet to remote host (ConnectionResetError)")

def push_to_talk_monitor():
    print(f"[PTT] Hold '{PUSH_TO_TALK_KEY}' to talk")
    while True:
        if keyboard.is_pressed(PUSH_TO_TALK_KEY):
            if not is_talking.is_set():
                print("[PTT] Talking...")
            is_talking.set()
        else:
            if is_talking.is_set():
                print("[PTT] Stopped talking")
            is_talking.clear()
        time.sleep(0.05)

# Launch threads
threads = [
    threading.Thread(target=audio_sender, daemon=True),
    threading.Thread(target=audio_receiver, daemon=True),
    threading.Thread(target=push_to_talk_monitor, daemon=True)
]

for t in threads:
    t.start()

print("[Main] Application running. Press Ctrl+C to exit.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[Main] Exiting...")
    sock.close()
    audio.terminate()
