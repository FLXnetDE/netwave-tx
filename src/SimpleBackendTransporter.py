import socket

class SimpleBackendTransporter:

    def __init__(self, udp_ip: str, udp_port: int, channelId: int) -> None:
        if not (0 <= channelId <= 255):
            raise ValueError("channelId must be in range 0–255 (uint8)")

        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.channelId = channelId
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data: bytes):
        # Prepend channelId as uint8
        packet = bytes([self.channelId]) + data
        self.socket.sendto(packet, (self.udp_ip, self.udp_port))