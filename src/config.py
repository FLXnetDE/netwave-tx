import pyaudio
from AppConfig import AppConfig

config = AppConfig("config.yaml")

# Network
CLIENT_ID = config.get("ClientId", 1)
CHANNEL_ID = config.get("ChannelId", 1)
UDP_IP = config.get("SocketServerAddress", "127.0.0.1")
UDP_PORT = config.get("SocketServerPort", 5000)

# Audio
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# PTT
PUSH_TO_TALK_KEY = config.get("PushToTalkKey", "space")