# This file contains the classes that are responsible for sending the data to the server
import socket
import threading
import logging
import queue


class UDPSenderQ:
    def __init__(self, ip="127.0.0.1", port=2223, debug=False):
        self.port = port
        self.running = False
        self.sock = None
        self.queue = queue.Queue()
        self.thread = None
        self.debug = debug
        if type(ip) is str:
            if ip == "broadcast" or ip.endswith(".255"):
                self.ip = ["<broadcast>"]
            else:
                self.ip = [ip]
        elif type(ip) is list:
            self.ip = ip
        else:
            raise ValueError("Invalid IP address format.")

    def is_running(self):
        return self.running

    def set_debug(self, debug):
        self.debug = debug

    def send_data(self):
        while self.is_running():
            try:
                data = self.queue.get(timeout=0.1)
                if self.debug:
                    logging.info(f"Sending data: {data}")
                for ip in self.ip:
                    self.sock.sendto(data, (ip, self.port))
            except queue.Empty:
                continue
            except socket.error as e:
                logging.error(f"Socket error while sending data: {e}")
                self.stop()

    def update(self, data):
        self.queue.put(data)

    def start(self):
        if self.is_running():
            logging.warning("Sender already running.")
            return False
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.running = True
            self.thread = threading.Thread(target=self.send_data, daemon=True)
            self.thread.start()
            logging.info("Sender started on {}:{}".format(self.ip, self.port))
            return True
        except socket.error as e:
            logging.error(f"Socket error: {e}")
            self.close()
            raise

    def stop(self):
        if self.is_running():
            self.running = False
            if self.thread is not None:
                self.thread.join()
            logging.info("Sender stopped.")

    def close(self):
        self.stop()
        if self.sock:
            self.sock.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __enter__(self):
        return self
