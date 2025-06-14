import sys
import subprocess
import time

def start_server(port):
    # Start server process
    cmd = ["python", "UDPserver.py", str(port)]
    return subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)


def run_client(host, port, file_list):
    # Run client process
    cmd = ["python", "UDPclient.py", host, str(port), file_list]
    subprocess.run(cmd, check=True)


def run_clients_concurrently(host, port, file_lists):
    # Running multiple clients concurrently
    processes = []
    for file_list in file_lists:
        cmd = ["python", "UDPclient.py", host, str(port), file_list]
        p = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr)
        processes.append(p)
    return processes


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Start server: python main.py server <port>")
        print("  Run client: python main.py client <host> <port> <file_list>")
        print("  Run concurrent clients: python main.py concurrent <host> <port> <file_list1> [file_list2 ...]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "server":
        if len(sys.argv) != 3:
            print("Usage: python main.py server <port>")
            sys.exit(1)

        port = int(sys.argv[2])
        start_server(port).wait()

    elif command == "client":
        if len(sys.argv) != 5:
            print("Usage: python main.py client <host> <port> <file_list>")
            sys.exit(1)

        host = sys.argv[2]
        port = int(sys.argv[3])
        file_list = sys.argv[4]
        run_client(host, port, file_list)

    elif command == "concurrent":
        if len(sys.argv) < 5:
            print("Usage: python main.py concurrent <host> <port> <file_list1> [file_list2 ...]")
            sys.exit(1)

        host = sys.argv[2]
        port = int(sys.argv[3])
        file_lists = sys.argv[4:]

        # Start server
        server = start_server(port)
        time.sleep(2)  # Wait for the server to start

        try:
            processes = run_clients_concurrently(host, port, file_lists)  # Start all clients
            # Wait for all clients to complete
            for p in processes:
                p.wait()

        finally:
            server.terminate()
            server.wait()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()