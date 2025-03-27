
import logging
import time
import struct
import threading


class Recorder:
    """
    the recorder class is responsible for recording the data from the vive tracker
    the received data is timestamped and stored in a list
    after recording is done, the data is saved to a file in the specified format
    additionally, the received data can be sent to a remote host (bypass)
    the player class can then playback the data in a loop
    """

    def __init__(self, callback_data, callback=None):
        self.recording = False
        self.data = []
        self.callback = callback
        self.callback_data = callback_data
        self.start_time = None
        self.killme = False
        self.thread = threading.Thread(target=self.record_loop, daemon=True)
        self.thread.start()


    def start(self):
        logging.info("Recorder started.")
        self.recording = True
        self.start_time = time.time()
        self.data = []
        return True

    def stop(self):
        logging.info("Recorder stopped.")
        self.recording = False

    def record(self):
        data = self.callback_data()
        time_diff = time.time() - self.start_time
        self.data.append((time_diff, data))
        if self.callback:
            try:
                self.callback(data)
            except Exception as e:
                logging.error(e)
                self.stop()

    def record_loop(self):
        while not self.killme:
            if self.recording:
                self.record()
            time.sleep(0.000000001)

    def save(self, file_path, file_type="bin"):
        if file_type == "bin":
            self.save_binary(file_path)
        elif file_type == "txt":
            self.save_text(file_path)
        else:
            logging.error("Invalid file type. Use 'bin' or 'txt'.")

    def save_binary(self, file_path):
        if len(self.data) != 0:
            with open(file_path, "wb") as f:
                for timestamp, data in self.data:
                    f.write(struct.pack("<f", timestamp))
                    f.write(struct.pack("I", len(data)))
                    f.write(data)
                logging.info(f"Data saved to {file_path} with {timestamp} seconds.")
        else:
            logging.error("No data to log")
                

    def save_text(self, file_path):        
        if len(self.data) != 0:
            with open(file_path, "w") as f:
                for timestamp, data in self.data:
                    f.write(f"{timestamp}: {data}\n")
                logging.info(f"Data saved to {file_path} with {timestamp} seconds.")
        else:
            logging.error("No data to log")

    def close(self):
        self.killme = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.killme = True
        self.thread.join()


if __name__ == "__main__":
    from receivers import ViveUDPReceiverQ
    from senders import UDPSenderQ
    

    receiver = ViveUDPReceiverQ('', 2223)
    receiver.start()

    sender = UDPSenderQ('127.0.0.1', 2224)
    sender.start()

    def callback(data):
        sender.update(data)

    def callback_data():
        return receiver.get_data_block()

    recorder = Recorder(callback_data=receiver.get_data_block, callback=sender.update)

    recorder.start()

    time.sleep(4)

    recorder.stop()
    recorder.save_binary("data.bin")
    recorder.save_text("data.txt")

