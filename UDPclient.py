import socket
import base64
import os

class UDPClient:
    def __init__(self, host, port, file_list):
        self.server_host = host
        self.server_port = port
        self.file_list = file_list
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1.0)

    def send_and_receive(self, message, addr, max_retries=5):
        # Reliable send receive function with timeout retry.
        timeout = 1.0  # Initial timeout 1 second.
        retries = 0

        while retries < max_retries:
            try:
                self.socket.sendto(message.encode(), addr)
                self.socket.settimeout(timeout)
                response, _ = self.socket.recvfrom(65535)
                return response.decode()

            except socket.timeout:
                retries += 1
                timeout *= 2  # Exponential backoff
                print(f"Timeout and retrying, attempt {retries}.")

        raise Exception("Max retries reached, giving up.")