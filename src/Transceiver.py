import asyncio
import pyaudio
from typing import Callable, Optional

class Transceiver:

    CHUNK: int = 1024
    FORMAT: int = pyaudio.paInt16
    CHANNELS: int = 1
    RATE: int = 16000

    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.input_active = False
        self.output_active = False
        self.on_input_callable: Optional[Callable[[bytes], None]] = None
        self.input_queue: asyncio.Queue[bytes] = asyncio.Queue()

    def open(self):
        """
        Configure and open an audio stream
        """
        self.stream = self.audio.open(format=self.FORMAT,
                                      channels=self.CHANNELS,
                                      rate=self.RATE,
                                      input=True,
                                      frames_per_buffer=self.CHUNK)

    def close(self):
        """
        Close and shutdown all handler and stream activities
        """
        self.set_input(False)
        self.set_output(False)
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()

    def on_input(self, callback: Callable[[bytes], None]):
        """
        Define a callback function for the event of receiving audio input from the stream

        :param callback: Callback function to be called in event of receiving audio input from the stream
        :type callback: Callable[[bytes], None]
        """
        self.on_input_callable = callback

    def set_input(self, active: bool):
        """
        Set the state of the input receiving loop

        :param active: True or False to activate or deactivate
        :type active: bool
        """
        self.input_active = active

    def set_output(self, active: bool):
        """
        Set the state of the output

        :param active: True or False to activate or deactivate
        :type active: bool
        """
        self.output_active = active

    async def loop(self):
        """
        Main loop for receiving audio input from stream and calling handler function
        """
        loop = asyncio.get_event_loop()

        try:
            while True:
                if self.input_active:
                    data = await loop.run_in_executor(None, self.stream.read, self.CHUNK, False)
                    await self.input_queue.put(data)
                    if self.on_input_callable:
                        self.on_input_callable(data)
                else:
                    await asyncio.sleep(0)
        except asyncio.CancelledError:
            pass  # graceful shutdown
        finally:
            self.close()
