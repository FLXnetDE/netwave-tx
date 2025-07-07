import threading
import time
from sender import audio_sender, get_socket, get_audio, get_talk_flag
from receiver import audio_receiver
from ptt import push_to_talk_monitor

sock = get_socket()
audio = get_audio()
is_talking = get_talk_flag()

threads = [
    threading.Thread(target=audio_sender, daemon=True),
    threading.Thread(target=audio_receiver, args=(sock,), daemon=True),
    threading.Thread(target=push_to_talk_monitor, args=(is_talking,), daemon=True)
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
