import os
import time
import struct
import logging
import threading

class Player:
    """Plays back a recording of timestamped data."""

    def __init__(self, callback=None):
        self.data = []
        self.callback = callback
        self.playing = False
        self.thread = None
        self.lock = threading.Lock()

    def load_from_bin(self, file_path):
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
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return

        with open(file_path, "r") as f:
            for line in f:
                timestamp = line.strip().split(": ")[0]
                data = line.strip().split(": ")[1:]
                data = "".join(data).encode()
                self.data.append((float(timestamp), data))

    def play(self):
        logging.info("Player started.")
        start_time = time.time()
        for timestamp, data in self.data:
            if not self.playing:
                return
            time_diff = time.time() - start_time
            if time_diff < timestamp:
                time.sleep(timestamp - time_diff)
            if self.callback:
                logging.info(f"Playing data: {data}")
                self.callback(data)
        logging.info("Player looped.")

    def play_loop(self):
        while self.is_playing():
            self.play()
        logging.info("Loop stopped.")

    def play_in_thread(self):
        with self.lock:
            self.playing = True
        self.thread = threading.Thread(target=self.play_loop)
        self.thread.start()

    def is_playing(self):
        with self.lock:
            return self.playing

    def stop(self):
        with self.lock:
            self.playing = False
        if self.thread is not None:
            self.thread.join()
        logging.info("Player thread stopped.")

    def set_callback(self, callback):
        self.callback = callback

if __name__ == "__main__":

    def callback(data):
        print(data)

    player = Player(callback)
    player.load_from_bin("data.bin")
    player.play_in_thread()

    # Example to stop the player after some time
    time.sleep(5)
    player.stop()
