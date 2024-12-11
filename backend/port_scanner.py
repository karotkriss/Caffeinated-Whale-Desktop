# port_scanner.py
import socket
import sys

def find_available_port(start_port):
    """Find the first available port starting from the given port."""
    port = int(start_port)
    while port < 65535:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        if result != 0:
            print(port)
            return
        port += 1
        
if __name__ == "__main__":
    if len(sys.argv) == 2:
        start_port = sys.argv[1]
        find_available_port(start_port)
    else:
        print("Usage: python port_scanner.py <start_port>")