
import socket
import threading
import time
import logging
import queue

from vive_decoder import ViveDecoder


class UDPReceiverQ:
    def __init__(self, ip='', port=2222):
        self.ip = ip
        self.port = port
        self.buffer_size = 1024
        self.data_queue = queue.Queue()
        self.running = False
        self.thread = None
        self.sock = None
        self._is_connected = False
        self.lock = threading.Lock()

    def handle_data(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(self.buffer_size)
                self.data_queue.put(data)
                print(data)
            except socket.timeout:
                continue
            except socket.error as e:
                logging.error(f"Socket error while receiving data: {e}")
                self.stop()

    def start(self):
        if self.is_running():
            logging.warning("Receiver already running.")
            return False
        if not self.is_connected():
            logging.info("Connecting...")
            self.connect()
        if not self.is_connected():
            logging.error("Connection failed.")
            return False
        with self.lock:
            self.running = True
            self.thread = threading.Thread(target=self.handle_data, daemon=True)
            self.thread.start()
            logging.info("Receiver started.")
        return True

    def is_running(self):
        with self.lock:
            return self.running

    def is_connected(self):
        with self.lock:
            return self._is_connected
    
    def stop(self):
        """Stop the receiver thread."""
        with self.lock:
            self.running = False
        if self.thread:
            self.thread.join()
        logging.info("Receiver stopped.")
        

    def connect(self):
        """bind to the socket."""
        with self.lock:
            if self.sock:
                self.close()
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.bind((self.ip, self.port))
                self.sock.settimeout(.1)
                logging.info(f"Receiver connected to {self.ip}:{self.port}.")
                self._is_connected = True
                return True
            except socket.error as e:
                logging.error(f"Socket error while connecting: {e}")
                self.close()
                return False
        
        
    def get_data_block(self):
        data = self.data_queue.get()
        return data
    
    def close(self):
        self.stop()
        if self.sock:
            self.sock.close()
            self.sock = None
        logging.info("Receiver closed.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ViveUDPReceiverQ(UDPReceiverQ):
    def __init__(self,  ip='', port=2222, ignore_list=[]):
        super().__init__(ip, port)
        self.decoder = ViveDecoder()
        self.decoder.ignored_vive_tracker_names = ignore_list

    def get_parsed_data(self):
        data = self.get_data_block()
        if data:
            return self.decoder.parse_byte_data(data)
        return None


### TEST ###

if __name__ == "__main__":
 
    receiver = ViveUDPReceiverQ('', 2223)
    receiver.start()

    i = 0
    num = 10000

    while i < num:
        print(i)
        data = receiver.get_parsed_data()
        print(data)
        i += 1

    receiver.close()

