import pyaudio
import numpy as np
import time

# Morse code map
MORSE_CODE = {
    'A': '.-',     'B': '-...',   'C': '-.-.',
    'D': '-..',    'E': '.',      'F': '..-.',
    'G': '--.',    'H': '....',   'I': '..',
    'J': '.---',   'K': '-.-',    'L': '.-..',
    'M': '--',     'N': '-.',     'O': '---',
    'P': '.--.',   'Q': '--.-',   'R': '.-.',
    'S': '...',    'T': '-',      'U': '..-',
    'V': '...-',   'W': '.--',    'X': '-..-',
    'Y': '-.--',   'Z': '--..',
    '0': '-----',  '1': '.----',  '2': '..---',
    '3': '...--',  '4': '....-',  '5': '.....',
    '6': '-....',  '7': '--...',  '8': '---..',
    '9': '----.',
    ' ': '/'  # Treat space as a word separator
}

# Audio configuration
FREQ = 700        # Tone frequency in Hz
SAMPLE_RATE = 44100
VOLUME = 0.5

# Morse timing (in seconds)
DOT_DURATION = 0.1
DASH_DURATION = 3 * DOT_DURATION
INTRA_CHAR_SPACE = DOT_DURATION
INTER_CHAR_SPACE = 3 * DOT_DURATION
WORD_SPACE = 7 * DOT_DURATION

def generate_tone(duration):
    """Generate a sine wave for the given duration."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    tone = np.sin(FREQ * 2 * np.pi * t)
    return (VOLUME * tone).astype(np.float32).tobytes()

def play_morse(message):
    """Play the given message as Morse code over audio."""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=SAMPLE_RATE,
                    output=True)

    for char in message.upper():
        if char not in MORSE_CODE:
            continue  # Skip unsupported characters

        code = MORSE_CODE[char]
        for symbol in code:
            if symbol == '.':
                stream.write(generate_tone(DOT_DURATION))
            elif symbol == '-':
                stream.write(generate_tone(DASH_DURATION))
            else:
                continue

            time.sleep(INTRA_CHAR_SPACE)

        time.sleep(INTER_CHAR_SPACE)

        if char == ' ':
            time.sleep(WORD_SPACE - INTER_CHAR_SPACE)

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    message = input("Enter a message to transmit in Morse code: ")
    while True:
        print("Transmitting...")
        play_morse(message)
        time.sleep(5)
        print("Done.")
