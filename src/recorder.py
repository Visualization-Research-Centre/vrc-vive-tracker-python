import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import socket
import threading
import time
import logging
import struct

from tracker_encoder import TrackerEncoder
from tracker_decoder import TrackerDecoder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Recorder:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager")

        self.record_path = tk.StringVar()
        self.load_path = tk.StringVar()
        self.play_path = tk.StringVar()
        self.recording = False
        self.recording_thread = None
        self.start_time = 0
        self.listener_running = False
        self.playing = False
        self.file_path = None
        self.default_ip_listen = ''
        self.default_port_listen = 2222
        # self.default_ip_send = '127.0.0.1'
        self.default_ip_send = '192.168.50.215'
        self.default_port_send = 2223

        # IP Address Label and Entry for listening
        self.listen_ip_label = tk.Label(root, text="IP")
        self.listen_ip_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.listen_ip_address = tk.StringVar(value=self.default_ip_listen)
        self.listen_ip_entry = tk.Entry(root, textvariable=self.listen_ip_address)
        self.listen_ip_entry.grid(row=0, column=1, padx=10, pady=10)

        # Port Label and Entry
        self.listen_port_label = tk.Label(root, text="Port")
        self.listen_port_label.grid(row=0, column=2, padx=10, pady=10, sticky='w')
        self.listen_port = tk.IntVar(value=self.default_port_listen)
        self.listen_port_entry = tk.Entry(root, textvariable=self.listen_port)
        self.listen_port_entry.grid(row=0, column=3, padx=10, pady=10)

        # Connect Button
        self.connect_button = tk.Button(root, text="Connect", command=self.connect)
        self.connect_button.grid(row=1, column=0, padx=10, pady=10)

        # Disconnect Button
        self.disconnect_button = tk.Button(root, text="Disconnected", bg="grey", relief=tk.SUNKEN, command=self.disconnect)
        self.disconnect_button.grid(row=1, column=1, padx=10, pady=10)
        
        # Record Button and Entry
        self.record_button = tk.Button(root, text="Record", command=self.record)
        self.record_button.grid(row=2, column=0, padx=10, pady=10)

        self.record_entry = tk.Entry(root, textvariable=self.record_path, state='readonly')
        self.record_entry.grid(row=2, column=1, padx=10, pady=10)

        # Load Button and Entry
        self.load_button = tk.Button(root, text="Load", command=self.load)
        self.load_button.grid(row=3, column=0, padx=10, pady=10)

        self.load_entry = tk.Entry(root, textvariable=self.load_path, state='readonly')
        self.load_entry.grid(row=3, column=1, padx=10, pady=10)

        # Play Button
        self.play_button = tk.Button(root, text="Play", command=self.start_playing)
        self.play_button.grid(row=4, column=0, padx=10, pady=10)

        # Stop Play Button
        self.stop_play_button = tk.Button(root, text="Stop Play", command=self.stop_playing)
        self.stop_play_button.grid(row=4, column=1, padx=10, pady=10)

        # IP Address Label and Entry for sending
        self.sending_ip_label = tk.Label(root, text="IP")
        self.sending_ip_label.grid(row=4, column=2, padx=10, pady=10, sticky='w')
        self.sending_ip_address = tk.StringVar(value=self.default_ip_send)
        self.sending_ip_entry = tk.Entry(root, textvariable=self.sending_ip_address)
        self.sending_ip_entry.grid(row=4, column=3, padx=10, pady=10)

        # Port Label and Entry
        self.sending_port_label = tk.Label(root, text="Port")
        self.sending_port_label.grid(row=4, column=4, padx=10, pady=10, sticky='w')
        self.sending_port = tk.IntVar(value=self.default_port_send)
        self.sending_port_entry = tk.Entry(root, textvariable=self.sending_port)
        self.sending_port_entry.grid(row=4, column=5, padx=10, pady=10)

        # add a slider in the last row for integer values between 6-12 with default value 12
        self.slider = tk.Scale(root, from_=6, to=12, orient='horizontal', length=200)
        self.slider.set(12)
        self.slider.grid(row=5, column=0, columnspan=6, padx=10, pady=10) 

        # Get the directory of the current script
        self.project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'recordings'))

    def connect(self):
        if not self.listener_running:
            try:
                self.listener_running = True
                self.recording_thread = threading.Thread(target=self.udp_broadcast_listener, daemon=True)
                self.recording_thread.start()
                self.connect_button.config(text="Connected", bg="green", relief=tk.SUNKEN)
                self.disconnect_button.config(text="Disconnect", bg="SystemButtonFace", relief=tk.RAISED)
                logging.info("UDP listener started")
            except Exception as e:
                self.listener_running = False
                messagebox.showerror("Error", f"Failed to start UDP listener: {e}")
                logging.error(f"Failed to start UDP listener: {e}")

    def disconnect(self):
        self.recording = False
        self.listener_running = False
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join()
        self.disconnect_button.config(text="Disconnected", bg="grey", relief=tk.SUNKEN)
        self.connect_button.config(text="Connect", bg="SystemButtonFace", relief=tk.RAISED)
        self.record_button.config(text="Record", bg="SystemButtonFace", relief=tk.RAISED)
        logging.info("UDP listener stopped")

    def record(self):
        self.file_path = filedialog.asksaveasfilename(initialdir=self.project_dir, defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if self.file_path:
            self.record_path.set(self.file_path)
            self.play_path.set(self.file_path)  # Set the play path to the recorded file
            # Create the file to ensure it exists
            with open(self.file_path, 'w') as file:
                file.write("")
            self.record_entry.config(width=len(self.file_path))
            # Start recording
            self.record_button.config(text="Recording", bg="yellow", relief=tk.SUNKEN)
            if not self.listener_running:
                self.connect()
            self.recording = True
            self.start_time = time.time()
            logging.info(f"Recording started at: {self.file_path}")

    def load(self):
        file_path = filedialog.askopenfilename(initialdir=self.project_dir, filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.load_path.set(file_path)
            self.play_path.set(file_path)  # Set the play path to the loaded file
            self.load_entry.config(width=len(file_path))
            logging.info(f"Loaded file: {file_path}")

    def start_playing(self):
        if self.play_path.get():
            self.playing = True
            self.play_thread = threading.Thread(target=self.play, daemon=True)
            self.play_thread.start()
            logging.info("Started playing")
            self.play_button.config(text="Playing", bg="yellow", relief=tk.SUNKEN)
        else:
            messagebox.showwarning("Warning", "No file loaded to play!")
            logging.warning("No file loaded to play!")

    def stop_playing(self):
        self.playing = False
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join()
        logging.info("Stopped playing")
        self.play_button.config(text="Play", bg="SystemButtonFace", relief=tk.RAISED)

    def play(self):
        sending_ip = self.sending_ip_address.get()
        sending_port = self.sending_port.get()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        last_timestamp = 0
        while self.playing:
            try:
                with open(self.play_path.get(), 'r') as file:
                    while True:
                        line = file.readline()
                        if not line:
                            if file.tell() == 0:  # Check if the file is empty
                                messagebox.showwarning("Warning", "The file is empty!")
                                logging.warning("The file is empty!")
                                self.playing = False
                                self.play_button.config(text="Play", bg="SystemButtonFace", relief=tk.RAISED)
                                break
                            else:
                                time.sleep(0.1)  # Timeout to prevent getting stuck
                        timestamp_str, data_str = line.strip().split(':', 1)

                        print(len(data_str))

                        if len(data_str) > 300:
                            # get the current value of the slider
                            slider_value = self.slider.get()
                            # print(f"Slider value: {slider_value}")

                            # get the timestamp and data from the line
                            timestamp = struct.unpack('<f', bytes.fromhex(timestamp_str))[0]
                            data = bytes.fromhex(data_str)

                            print('data:', data)    

                            # decode the data
                            decoder = TrackerDecoder()
                            decoder.action_process_data(data)
                            decoded_data = decoder.vr_tracker_devices
                            print(f"Decoded data: {decoded_data}")

                            # encode the data
                            encoder = TrackerEncoder()
                            encoder.vr_tracker_devices = decoded_data
                            encoded_data = encoder.action_process_data()
                            print(f"Encoded data: {encoded_data}")

                            self.send_udp_message(sending_ip, sending_port, data, sock)

                            time_diff = timestamp - last_timestamp

                            if time_diff > 0.0001:
                                time.sleep(time_diff)  # Add a small delay to simulate real-time sending

                            last_timestamp = timestamp

                        if not self.playing:
                            break

            except Exception as e:
                messagebox.showerror("Error", f"Failed to send UDP message: {e}")
                logging.error(f"Failed to send UDP message: {e}")
                break
        logging.info('Done playing')

    def send_udp_message(self, ip, port, message, socket):
        try:
            socket.sendto(message, (ip, port))
            # logging.info(f"Sent message: {message} to {ip}:{port}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send UDP message: {e}")
            logging.error(f"Failed to send UDP message: {e}")

    def udp_broadcast_listener(self):
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Allow the socket to reuse the address
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind the socket to the IP and listen_port
        ip = self.listen_ip_address.get()
        listen_port = self.listen_port.get()
        sock.bind((ip, listen_port))
        
        # Set a timeout for the socket
        sock.settimeout(5.0)  # Timeout after 5 seconds of inactivity
        
        logging.info(f"Listening for UDP broadcast on {ip}:{listen_port}...")
        
        dat = []
        while self.listener_running:
            try:
                #TODO test 
                # Receive data from the socket
                data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
                elapsed_time = time.time() - self.start_time if self.start_time else 0
                elapsed_time_bytes = struct.pack('<f', elapsed_time)  # Convert timestamp to bytes
                data = elapsed_time_bytes + data  # Prepend timestamp to data
                dat.append(data)
                # print(f"Received data: {data}")
            except socket.timeout:
                logging.warning("UDP listener timed out")
                continue

        if self.file_path:
            with open(self.file_path, 'w') as file:
                for item in dat:
                    timestamp_bytes = item[:4]
                    data_bytes = item[4:]
                    timestamp_str = timestamp_bytes.hex()
                    data_str = data_bytes.hex()
                    file.write(f"{timestamp_str}:{data_str}\n")
            logging.info(f"Data saved to {self.file_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = Recorder(root)
    root.mainloop()