import socket
import threading
import random
import os
import base64

class UDPServer:
    def __init__(self, port):
        self.port = port
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.main_socket.bind(('0.0.0.0', port))
        print(f"Server started on port {port}")

    def handle_file_transfer(self, filename, client_addr):
        # Threaded functions that handle single file transfers.
        try:
            # Create a new UDP socket for this file transfer.
            transfer_port = random.randint(50000, 51000)
            transfer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            transfer_socket.bind(('0.0.0.0', transfer_port))

            # Check whether the file exists.
            if not os.path.exists(filename):
                self.main_socket.sendto(
                    f"ERR {filename} NOT_FOUND".encode(),
                    client_addr
                )
                return

            # Send OK response.
            file_size = os.path.getsize(filename)
            response = f"OK {filename} SIZE {file_size} PORT {transfer_port}"
            self.main_socket.sendto(response.encode(), client_addr)

            # Open file for transfer.
            with open(filename, 'rb') as f:
                while True:
                    # Waiting for client requests.
                    data, addr = transfer_socket.recvfrom(1024)
                    request = data.decode().strip()
                    parts = request.split()

                    if parts[0] == "FILE" and parts[2] == "CLOSE":
                        # Process close request.
                        transfer_socket.sendto(
                            f"FILE {filename} CLOSE_OK".encode(),
                            addr
                        )
                        break

                    elif parts[0] == "FILE" and parts[2] == "GET":
                        # Processing data requests.
                        start = int(parts[4])
                        end = int(parts[6])

                        # Read file block.
                        f.seek(start)
                        chunk = f.read(end - start + 1)

                        # Encode and send.
                        encoded = base64.b64encode(chunk).decode()
                        response = (
                            f"FILE {filename} OK START {start} END {end} "
                            f"DATA {encoded}"
                        )

                        transfer_socket.sendto(response.encode(), addr)

            transfer_socket.close()

        except Exception as e:
            print(f"Error in file transfer: {e}")

    def run(self):
        # Master server loop.
        while True:
            try:
                # Receive download request.
                data, addr = self.main_socket.recvfrom(1024)
                request = data.decode().strip()

                if request.startswith("DOWNLOAD"):
                    # Resolve file name.
                    filename = request.split()[1]

                    # Create a new thread to handle file transfers.
                    threading.Thread(
                        target=self.handle_file_transfer,
                        args=(filename, addr),
                        daemon=True
                    ).start()

            except Exception as e:
                print(f"Server error: {e}")