import socket
import threading
import time
import logging
import queue
import os
import struct
from abc import ABC, abstractmethod

from src.vive_decoder import ViveDecoder
from src.vive_encoder import ViveEncoder


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
    def __init__(self, ip="", port=2222, callback=None):
        self.ip = ip
        self.port = port
        self.buffer_size = 1460
        self.data_queue = queue.Queue()
        self.running = False
        self.thread = None
        self.sock = None
        self._is_connected = False
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
        self.running = True
        self.thread = threading.Thread(target=self.handle_data, daemon=True)
        self.thread.start()
        logging.info("Receiver started.")
        return True

    def stop(self):
        """Stop the receiver thread."""
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
        return self.running

    def is_connected(self):
        return self._is_connected

    def connect(self):
        """bind to the socket."""
        if self.sock:
            self.close()
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.ip, self.port))
            self.sock.settimeout(0.1)
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

    def get_data_block(self, timeout=0.1):
        try:
            return self.data_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_data_block_nowait(self):
        try:
            return self.data_queue.get_nowait()
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
        self.queue = queue.Queue()
        self.paused = False

    def start(self):
        self.playing = True
        self.thread = threading.Thread(target=self.play_loop)
        self.thread.start()
        logging.info("Player started.")
        return True

    def stop(self):
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
            # Read the header
            first = f.read(4)
            if not first:
                logging.error("File is empty or corrupted.")
                return
            start_time = struct.unpack("<f", first)[0]
            length = struct.unpack("I", f.read(4))[0]
            if length != 0:
                logging.warning(
                    "File might be old and recording time is wrong. Interpreting header as data...."
                )
                data = f.read(length)
            logging.info(f"Recording time: {start_time}")

            while True:
                first = f.read(4)
                if not first:
                    logging.info("End of file reached.")
                    break
                if first == b"\x00":
                    logging.info("End of file reached.")
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
        return self.playing

    def play(self):
        start_time = time.time()
        for timestamp, data in self.data:
            if not self.playing:
                return
            if self.paused:
                pause_time = time.time()
                while self.paused:
                    time.sleep(0.1)
                time_diff = time.time() - pause_time
                start_time += time_diff
            time_diff = time.time() - start_time
            if time_diff < timestamp:
                time.sleep(timestamp - time_diff)
            if self.callback:
                self.callback(data)
            else:
                self.queue.put(data)
        logging.info("Player looped.")
        
    def pause(self):
        """Pause or resume the playback."""
        self.paused = not self.paused
        if self.paused:
            logging.info("Player paused.")
            return True
        else:
            logging.info("Player resumed.")
            return False

    def play_loop(self):
        while self.is_playing():
            self.play()
        logging.info("Loop stopped.")

    def set_callback(self, callback):
        self.callback = callback

    def get_data_block(self, timeout=0.1):
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_data_block_nowait(self):
        try:
            return self.queue.get_nowait()
        except queue.Empty:
            return None


class Synchronizer(DataSource):
    def __init__(self, callbacks=[]):
        self.running = False
        self.thread = None
        self.callbacks = callbacks
        self.queue = queue.Queue()
        self.decoder = ViveDecoder()
        self.encoder = ViveEncoder()

    def start(self):
        if self.running:
            logging.warning("Synchronizer already running.")
            return False
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        logging.info("Synchronizer started.")
        return True

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logging.info("Synchronizer stopped.")

    def close(self):
        self.stop()
        logging.info("Synchronizer closed.")

    def run(self):
        while self.running:
            self.sync()
            
    def add_callback(self, callback: dict):
        """Add a callback function to the synchronizer."""
        for cb in self.callbacks:
            if cb["name"] == callback["name"]:
                logging.warning(
                    f"Callback with name {callback['name']} already exists. Overwriting."
                )
                self.callbacks.remove(cb)
        self.callbacks.append(callback)
        
    def remove_callback(self, name):
        """Remove a callback function from the synchronizer."""
        for cb in self.callbacks:
            if cb["name"] == name:
                logging.info(f"Removing callback: {cb}")
                self.callbacks.remove(cb)
                break
        else:
            logging.warning(f"Callback with name {callback['name']} not found.")
    
    def clear_callbacks(self):
        """Clear all callback functions from the synchronizer."""
        logging.info(f"Callbacks: {self.callbacks}")
        for cb in self.callbacks:
            self.remove_callback(cb["name"])
            
    def sync(self):
        # Get data from all sources
        data = [cb["callback"](cb["timeout"]) for cb in self.callbacks]
        
        tracker_names = []
        all_trackers = []
        
        for d in data:
            # if d is None:
            #     return
            if d is not None:
                self.decoder.decode(d)
                tracker_data = self.decoder.vive_trackers
                # combine all trackers
                # overwrite trackers with the same name
                for tracker in tracker_data:
                    name = tracker["name"]
                    if name in tracker_names:
                        # overwrite the tracker
                        index = tracker_names.index(name)
                        all_trackers[index] = tracker
                    else:
                        tracker_names.append(name)
                        all_trackers.append(tracker)
        # Encode the data
        if all_trackers is not None and len(all_trackers) > 0:
            self.encoder.vive_trackers = all_trackers
            encoded_data = self.encoder.encode()
            self.queue.put(encoded_data)
        
    def get_data_block(self, timeout=0.1):
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_data_block_nowait(self):
        try:
            return self.queue.get_nowait()
        except queue.Empty:
            return None


### TEST ###

if __name__ == "__main__":

    receiver = UDPReceiverQ("", 2223)
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
