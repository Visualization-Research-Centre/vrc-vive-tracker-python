import socket
import time
import struct
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_udp_broadcast(ip, port, message, framerate):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    delay = 1.0 / framerate  # Calculate delay between frames

    try:
        while True:
            sock.sendto(message, (ip, port))
            logging.info(f"Sent message: {message} to {ip}:{port}")
            time.sleep(delay)
    except KeyboardInterrupt:
        logging.info("Stopped sending UDP broadcast")
    except Exception as e:
        logging.error(f"Failed to send UDP message: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    BROADCAST_IP = "192.168.50.150"  # Broadcast IP address
    BROADCAST_PORT = 2223  # Broadcast port
    MESSAGE = bytes.fromhex("0050433bae0807324239323139453903640101c40a263f99a07b40ea4f6f40713057bf0fc307bf6e32c13da5a86a3d383939324246303303540000352a4dc02042053e0aba43c0c71b71bef65077bf1b481d3dde7fca3d344344464342384203320101fa2906bf426de13f5cb6b1be294b44bf16858c3d5d71c03d0b9c213f33414430374537420400010199d677403ebb6c40446a21bfe0b37b3ee61825bf1e80303e40ec333f323932423136344104000101c0e46dc0585c7340cfbec73e002980be1d4824bf1d34993e6c0929bf323644363838443604000101ef49ecbd9c027640f4e96d407bf6a3bcd5ad71bf2f6da73e395e1abd314641383045383604000101d8b352bc20477440ef0970c0e0e1b73eb2072d3d7b09eebb02ab6e3f")  # Example byte string
    FRAMERATE = 30  # Frames per second

    send_udp_broadcast(BROADCAST_IP, BROADCAST_PORT, MESSAGE, FRAMERATE)


# run on target host to check
# import socket

# UDP_IP = "192.168.50.150"
# UDP_PORT = 2223

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.bind((UDP_IP, UDP_PORT))

# print(f"Listening on {UDP_IP}:{UDP_PORT}")

# while True:
#     data, addr = sock.recvfrom(1024)
#     print(f"Received message: {data} from {addr}")