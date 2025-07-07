import struct
import pyaudio
from config import CHANNEL_ID, CHUNK, FORMAT, CHANNELS, RATE

def audio_receiver(sock):
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

    print("[Receiver] Listening...")
    while True:
        try:
            packet, _ = sock.recvfrom(4096)
            if len(packet) > 8:
                recv_channel, = struct.unpack("!I", packet[:4])
                if recv_channel == CHANNEL_ID:
                    stream.write(packet[8:])
        except Exception as err:
            print(f"[Receiver] Error: {err}")
