import socket

def udp_broadcast_listener(file_path=None, port=2222):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Allow the socket to reuse the address
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind the socket to the port
    sock.bind(('', port))
    
    print(f"Listening for UDP broadcast on port {port}...")

    if file_path:
        with open(file_path, 'a') as file:
            while True:
                # Receive data from the socket
                data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
                print(f"Received message: {data} from {addr}")
                file.write(f"{data}\n")
    else:
        while True:
            # Receive data from the socket
            data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            print(f"Received message: {data} from {addr}")


def udp_broadcast_sender(port=2222):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Set the socket to broadcast
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    message = b"Hello, World!"
    while True:
        # Send data to the socket
        sock.sendto(message, ('', port))
        print(f"Sent message: {message}")

if __name__ == "__main__":
    # udp_broadcast_listener()
    udp_broadcast_sender(2222)