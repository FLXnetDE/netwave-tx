import asyncio
from SimpleBackendTransporter import SimpleBackendTransporter
from Transceiver import Transceiver

UDP_IP: str = "127.0.0.1"
UDP_PORT: int = 5005

transceiver = Transceiver()
transporter = SimpleBackendTransporter(UDP_IP, UDP_PORT, 3)

async def main():
    transceiver.open()
    transceiver.set_input(True)

    transceiver.on_input(transporter.send)

    try:
        await transceiver.loop()
    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        transceiver.close()

asyncio.run(main())