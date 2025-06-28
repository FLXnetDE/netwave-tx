import socket

class SimpleBackendTransporter:

    def __init__(self, udp_ip: str, udp_port: int) -> None:
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data: bytes):
        self.socket.sendto(data, (self.udp_ip, self.udp_port))