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

    def download_file(self, filename, transfer_port):
        # Download a single file.
        try:
            # Create a new socket for file transfer.
            transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            transfer_socket.settimeout(1.0)

            # Open local file
            with open(filename, 'wb') as f:
                print(f"Downloading {filename}", end='', flush=True)

                start = 0
                block_size = 1000

                while True:
                    end = start + block_size - 1

                    # Send data request
                    request = (
                        f"FILE {filename} GET START {start} END {end}"
                    )

                    try:
                        response = self.send_and_receive(
                            request,
                            (self.server_host, transfer_port)
                        )

                        parts = response.split()

                        if parts[0] == "FILE" and parts[2] == "OK":
                            # Processing data blocks
                            data_start = int(parts[4])
                            data_end = int(parts[6])
                            encoded = response.split('DATA ')[1]
                            chunk = base64.b64decode(encoded)

                            # Write file
                            f.seek(data_start)
                            f.write(chunk)
                            print('*', end='', flush=True)

                            if data_end >= int(parts[4]) - 1:
                                # File transfer complete.
                                break

                            start = data_end + 1

                    except Exception as e:
                        print(f"Error during transfer: {e}")
                        raise

                # Send close request
                close_msg = f"FILE {filename} CLOSE"
                self.send_and_receive(close_msg, (self.server_host, transfer_port))

                print(f"{filename} downloaded successfully")

            transfer_socket.close()

        except Exception as e:
            print(f"Failed to download {filename}: {e}")
            if os.path.exists(filename):
                os.remove(filename)