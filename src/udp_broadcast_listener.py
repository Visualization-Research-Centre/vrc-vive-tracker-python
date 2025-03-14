import socket

def udp_broadcast_listener(port):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Allow the socket to reuse the address
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind the socket to the port
    sock.bind(('', port))
    
    print(f"Listening for UDP broadcast on port {port}...")
    
    while True:
        # Receive data from the socket
        data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
        print(f"Received raw data: {data} from {addr}")

if __name__ == "__main__":
    udp_broadcast_listener(2222)