# This file contains the classes that are responsible for sending the data to the server
import socket
import threading
import logging
import queue
import socket
import threading
import logging
import queue

class UDPSenderQ:
    def __init__(self, ip='127.0.0.1', port='2223'):
        self.ip = ip
        self.port = port
        self.sock = None
        self.queue = queue.Queue()
        self.thread = None
        self.running = False

    def send_data(self):
        while self.running:
            try:
                data = self.queue.get(timeout=1)
                self.sock.sendto(data, (self.ip, self.port))
                logging.info(f"Data sent: {data}")
            except queue.Empty:
                continue
            except socket.error as e:
                logging.error(f"Socket error while sending data: {e}")
                self.stop()

    def update(self, data):
        self.queue.put(data)

    def start(self):
        if not self.running:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.running = True
                self.thread = threading.Thread(target=self.send_data, daemon=True)
                self.thread.start()
                logging.info("Sender started.")
            except socket.error as e:
                logging.error(f"Socket error: {e}")
                self.close()
                raise

    def stop(self):
        if self.running:
            self.running = False
            if self.thread is not None:
                self.thread.join()
            logging.info("Sender stopped.")

    def close(self):
        self.stop()
        if self.sock:
            try:
                self.sock.close()
                logging.info("Socket closed.")
            except socket.error as e:
                logging.error(f"Error closing socket: {e}")

    def set_address(self, ip, port):
        self.ip = ip
        self.port = port

