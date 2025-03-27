
import socket
import threading
import time
import logging
import queue

from vive_decoder import ViveDecoder


logging.basicConfig(level=logging.INFO, format='%(filename)s - %(levelname)s - %(message)s')

class UDPReceiverQ:
    def __init__(self, ip='', port=2222):
        self.ip = ip
        self.port = port
        self.buffer_size = 1024
        self.data_queue = queue.Queue()
        self.running = False
        self.thread = None
        self.sock = None

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.ip, self.port))
        except socket.error as e:
            logging.error(f"Socket error: {e}")
            self.close()
            raise

    def handle_data(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(self.buffer_size)
                self.data_queue.put(data)
            except socket.error as e:
                logging.error(f"Socket error while receiving data: {e}")
                self.stop()

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.handle_data, daemon=True)
            self.thread.start()
            logging.info("Receiver started.")

    def stop(self):
        if self.running:
            self.running = False
            if self.thread is not None:
                self.thread.join()
            logging.info("Receiver stopped.")

    def get_data_block(self):
        data = self.data_queue.get()
        return data
    
    def close(self):
        self.stop()
        if self.sock:
            try:
                self.sock.close()
                logging.info("Socket closed.")
            except socket.error as e:
                logging.error(f"Error closing socket: {e}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

                
    def update_address(self, ip, port):
        self.ip = ip
        self.port = port
        self.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
            

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

