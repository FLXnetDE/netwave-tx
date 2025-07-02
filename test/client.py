import socket
import struct
import threading
import pyaudio

# --- Configuration ---
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
CHANNEL_ID = 1
CHUNK_SIZE = 1024
SAMPLE_RATE = 16000
FORMAT = pyaudio.paInt16
CHANNELS = 1

# --- Set up UDP socket ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 0))  # use ephemeral port for receiving

# --- PyAudio setup ---
audio = pyaudio.PyAudio()

stream_out = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=SAMPLE_RATE,
    output=True,
    frames_per_buffer=CHUNK_SIZE
)

stream_in = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=SAMPLE_RATE,
    input=True,
    frames_per_buffer=CHUNK_SIZE
)

# --- Function to send audio ---
def send_audio():
    while True:
        audio_chunk = stream_in.read(CHUNK_SIZE, exception_on_overflow=False)
        header = struct.pack(">I", CHANNEL_ID)
        packet = header + audio_chunk
        sock.sendto(packet, (SERVER_IP, SERVER_PORT))

# --- Function to receive and play audio ---
def receive_audio():
    while True:
        data, _ = sock.recvfrom(4096)
        if len(data) < 4:
            continue
        audio_data = data[4:]
        stream_out.write(audio_data)

# --- Run threads ---
send_thread = threading.Thread(target=send_audio, daemon=True)
recv_thread = threading.Thread(target=receive_audio, daemon=True)

send_thread.start()
recv_thread.start()

print(f"Sending & receiving audio on channel {CHANNEL_ID} to {SERVER_IP}:{SERVER_PORT}. Press Ctrl+C to stop.")

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Exiting...")
    stream_in.stop_stream()
    stream_out.stop_stream()
    stream_in.close()
    stream_out.close()
    audio.terminate()
    sock.close()
