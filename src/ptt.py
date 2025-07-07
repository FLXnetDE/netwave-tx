import time
import keyboard
from config import PUSH_TO_TALK_KEY

def push_to_talk_monitor(is_talking):
    print(f"[PTT] Hold '{PUSH_TO_TALK_KEY}' to talk")
    while True:
        if PUSH_TO_TALK_KEY is None: return
        if keyboard.is_pressed(PUSH_TO_TALK_KEY):
            if not is_talking.is_set():
                print("[PTT] Talking...")
            is_talking.set()
        else:
            if is_talking.is_set():
                print("[PTT] Stopped talking")
            is_talking.clear()
        time.sleep(0.05)
