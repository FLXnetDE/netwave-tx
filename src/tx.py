import socket
import threading
import struct
import pyaudio
import keyboard
import time

# Configuration
SERVER_IP = "127.0.0.1"
SERVER_PORT = 5000
CLIENT_ID = 0  # Will be set by server
CHANNEL_ID = 10
PUSH_TO_TALK_KEY = "space"

# Audio config
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Packet types
PACKET_TYPE_LOGIN = 0x01
PACKET_TYPE_LOGIN_ACK = 0x02
PACKET_TYPE_AUDIO = 0x03

# Globals
is_talking = threading.Event()
audio = pyaudio.PyAudio()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 0))  # Bind to random available port


def send_login_packet():
    packet = struct.pack("!BI", PACKET_TYPE_LOGIN, CHANNEL_ID)
    sock.sendto(packet, (SERVER_IP, SERVER_PORT))


def receive_login_ack():
    global CLIENT_ID
    sock.settimeout(5)
    try:
        data, _ = sock.recvfrom(1024)
        if data[0] == PACKET_TYPE_LOGIN_ACK and len(data) >= 5:
            CLIENT_ID = struct.unpack("!I", data[1:5])[0]
            print(f"[Login] Received client ID: {CLIENT_ID}")
        else:
            print("[Login] Invalid ACK")
            exit(1)
    except socket.timeout:
        print("[Login] Timed out waiting for ACK")
        exit(1)
    finally:
        sock.settimeout(None)


def build_audio_packet(client_id, channel_id, audio_data):
    header = struct.pack("!B I I", PACKET_TYPE_AUDIO, client_id, channel_id)
    return header + audio_data


def audio_sender():
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("[Sender] Ready to transmit audio")
    while True:
        if is_talking.is_set():
            try:
                audio_data = stream.read(CHUNK, exception_on_overflow=False)
                packet = build_audio_packet(CLIENT_ID, CHANNEL_ID, audio_data)
                sock.sendto(packet, (SERVER_IP, SERVER_PORT))
            except Exception as e:
                print(f"[Sender] Error: {e}")
        else:
            time.sleep(0)


def audio_receiver():
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
    print("[Receiver] Listening for audio...")
    while True:
        try:
            packet, _ = sock.recvfrom(4096)
            if len(packet) > 9 and packet[0] == PACKET_TYPE_AUDIO:
                recv_client_id = struct.unpack("!I", packet[1:5])[0]
                recv_channel_id = struct.unpack("!I", packet[5:9])[0]
                if recv_channel_id == CHANNEL_ID:
                    stream.write(packet[9:])
        except Exception as e:
            print(f"[Receiver] Error: {e}")


def push_to_talk_monitor():
    print(f"[PTT] Hold '{PUSH_TO_TALK_KEY}' to speak")
    while True:
        if keyboard.is_pressed(PUSH_TO_TALK_KEY):
            if not is_talking.is_set():
                print("[PTT] Talking...")
            is_talking.set()
        else:
            if is_talking.is_set():
                print("[PTT] Stopped")
            is_talking.clear()
        time.sleep(0)


def main():
    print("[Main] Logging in...")
    send_login_packet()
    receive_login_ack()

    threads = [
        threading.Thread(target=audio_sender, daemon=True),
        threading.Thread(target=audio_receiver, daemon=True),
        threading.Thread(target=push_to_talk_monitor, daemon=True)
    ]

    for t in threads:
        t.start()

    print("[Main] Client running. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Main] Exiting...")
        sock.close()
        audio.terminate()


if __name__ == "__main__":
    main()
