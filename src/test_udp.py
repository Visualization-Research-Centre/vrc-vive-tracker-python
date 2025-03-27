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

def receive_udp_data(ip, port, output_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))

    logging.info(f"Listening on {ip}:{port}")

    with open(output_file, 'wb') as file:
        try:
            while True:
                data, addr = sock.recvfrom(1024)
                logging.info(f"Received message: {data} from {addr}")
                file.write(data)
        except KeyboardInterrupt:
            logging.info("Stopped receiving UDP data")
        except Exception as e:
            logging.error(f"Failed to receive UDP message: {e}")
        finally:
            sock.close()

if __name__ == "__main__":
    import os
    BROADCAST_IP = ""  # Broadcast IP address
    BROADCAST_PORT = 2222  # Broadcast port
    RECEIVE_PORT = 2223  # Port to receive UDP data
    timestamp = struct.pack('f', time.time())  # Convert current time to byte data
    MESSAGE = timestamp + b'\x00P\xC3;\xAE\x08\x072B9219E9\x03d\x01\x01\xC4\n&?\x99\xA0{@\xEAOo@q0W\xBF\x0F\xC3\x07\xBFn2\xC1=\xA5\xA8j=8992BF03\x03T\x00\x005*M\xC0 B\x05>\n\xBA\xC3\xC0\xC7\x1Bq\xBE\xF6Pw\xBF\x1B\x48\x1D=\xDE\x7F\xCA=4CDFCB8B\x032\x01\x01\xFA)\x06\xBFBm\xE1?\\\xB6\xB1\xBE)KD\xBF\x16\x85\x8C=]q\xC0=\x0B\x9C!?\x33AD07E7B\x04\x00\x01\x01\x99\xD6w@>\xBBl@Dj!\xBF\xE0\xB3{>\xE6\x18%\xBF\x1E\x80\x03\x03\xE4\x0E\xC33\xF2\x29B\xB1dA\x04\x00\x01\x01\xC0\xE4m\xC0X\\s@\xCF\xBE\xC7>\x00)\x80\xBE\x1DHBK\xBF\x1D4\x99>l\t)\xBF2d688D6\x04\x00\x01\x01\xEFI\xEC\xBD\x9C\x02v@\xF4\xE9m@{\xF6\xA3\xBC\xD5\xADq\xBF/o\xDA\x73\xE3\x95\xE1\xAB\xD3\x14FA80E86\x04\x00\x01\x01\xD8\xB3R\xBC Gt@\xEF\tp\xC0\xE0\xE1\xB7>\xB2\x07-=\x7B\t\xEE\xBB\x02\xABn?'
    FRAMERATE = 30  # Frames per second
    project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'recordings'))
    OUTPUT_FILE = os.path.join(project_dir, "test_file.txt")

    # write MESSAGE to file
    with open(OUTPUT_FILE, 'wb') as file:
        for i in range(100):
            file.write(MESSAGE)

    # Start sending UDP broadcast in a separate thread
    # import threading
    # sender_thread = threading.Thread(target=send_udp_broadcast, args=(BROADCAST_IP, BROADCAST_PORT, MESSAGE, FRAMERATE))
    # sender_thread.start()

    # # Start receiving UDP data and saving to file
    # receive_udp_data("", RECEIVE_PORT, OUTPUT_FILE)


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