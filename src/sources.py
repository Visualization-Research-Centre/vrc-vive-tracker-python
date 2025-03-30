
import socket
import threading
import time
import logging
import queue
import os
import struct
from abc import ABC, abstractmethod

class DataSource(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def close(self):
        pass

class UDPReceiverQ(DataSource):
    def __init__(self, ip='', port=2222, callback=None):
        self.ip = ip
        self.port = port
        self.buffer_size = 1460
        self.data_queue = queue.Queue()
        self.running = False
        self.thread = None
        self.sock = None
        self._is_connected = False
        self.lock = threading.Lock()
        self.callback = callback

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

    def stop(self):
        """Stop the receiver thread."""
        with self.lock:
            self.running = False
        if self.thread:
            self.thread.join()
        logging.info("Receiver stopped.")
        
    def close(self):
        self.stop()
        if self.sock:
            self.sock.close()
            self.sock = None
        logging.info("Receiver closed.")
    

    def is_running(self):
        with self.lock:
            return self.running

    def is_connected(self):
        with self.lock:
            return self._is_connected
    
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
                return False

    def handle_data(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(self.buffer_size)
                if self.callback:
                    self.callback(data)
                else:
                    self.data_queue.put(data)
            except socket.timeout:
                continue
            except socket.error as e:
                logging.error(f"Socket error while receiving data: {e}")
                self.stop()
    
    def get_data_block(self):
        try:
            return self.data_queue.get(timeout=.1)
        except queue.Empty:
            return None
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class Player(DataSource):
    """Plays back a recording of timestamped data."""

    def __init__(self, callback=None):
        self.data = []
        self.callback = callback
        self.playing = False
        self.thread = None
        self.lock = threading.Lock()
        self.queue = queue.Queue()


    def start(self):
        with self.lock:
            self.playing = True
        self.thread = threading.Thread(target=self.play_loop)
        self.thread.start()
        logging.info("Player started.")
        return True

    def stop(self):
        with self.lock:
            self.playing = False
        if self.thread is not None:
            self.thread.join()
        logging.info("Player thread stopped.")


    def close(self):
        self.stop()
        logging.info("Player closed.")


    def load(self, file_path):
        file_type = file_path.split(".")[-1]
        if file_type == "bin":
            self.load_from_bin(file_path)
        elif file_type == "txt":
            self.load_from_text(file_path)
        else:
            logging.error(f"Unsupported file type: {file_type}")

    def load_from_bin(self, file_path):
        self.data = []
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return
        with open(file_path, "rb") as f:
            while True:
                first = f.read(4)
                if not first:
                    break
                if first == b'\x00':
                    break
                timestamp = struct.unpack("<f", first)[0]
                length = struct.unpack("I", f.read(4))[0]
                data = f.read(length)
                self.data.append((timestamp, data))
                
    def load_from_text(self, file_path):
        self.data = []
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return
        with open(file_path, "r") as f:
            for line in f:
                timestamp = line.strip().split(": ")[0]
                data = line.strip().split(": ")[1:]
                data = "".join(data).encode()
                self.data.append((float(timestamp), data))

    def is_playing(self):
        with self.lock:
            return self.playing

    def play(self):
        start_time = time.time()
        for timestamp, data in self.data:
            if not self.playing:
                return
            time_diff = time.time() - start_time
            if time_diff < timestamp:
                time.sleep(timestamp - time_diff)
            if self.callback:
                self.callback(data)
            else:
                self.queue.put(data)
        logging.info("Player looped.")

    def play_loop(self):
        while self.is_playing():
            self.play()
        logging.info("Loop stopped.")

    def set_callback(self, callback):
        self.callback = callback

    def get_data_block(self):
        try:
            return self.queue.get(timeout=.1)
        except queue.Empty:
            return None

    def __exit__(self):
        self.stop()


### TEST ###

if __name__ == "__main__":
 
    receiver = UDPReceiverQ('', 2223)
    receiver.start()

    i = 0
    num = 10000

    while i < num:
        print(i)
        data = receiver.get_data_block()
        print(data)
        i += 1

    receiver.close()


    def callback(data):
        print(data)

    player = Player(callback)
    player.load_from_bin("data.bin")
    player.start()

    # Example to stop the player after some time
    time.sleep(5)
    player.stop()
