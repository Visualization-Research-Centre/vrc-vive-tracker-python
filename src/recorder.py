import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
import socket
import threading
import time

class Recorder:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager")

        self.record_path = tk.StringVar()
        self.load_path = tk.StringVar()
        self.play_path = tk.StringVar()
        self.recording = False
        self.recording_thread = None
        self.start_time = None
        self.listener_running = False
        self.playing = False
        self.file_path = None
        self.default_ip_listen = ''
        self.default_port_listen = 2222
        self.default_ip_send = ''
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

        # Get the directory of the current script
        self.project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'recordings'))

    def connect(self):
        if not self.listener_running:
            self.listener_running = True
            self.recording_thread = threading.Thread(target=self.udp_broadcast_listener, daemon=True)
            self.recording_thread.start()
            self.connect_button.config(text="Connected", bg="green", relief=tk.SUNKEN)
            self.disconnect_button.config(text="Disconnect", bg="SystemButtonFace", relief=tk.RAISED)
            # messagebox.showinfo("Info", "UDP listener started")

    def disconnect(self):
        self.recording = False
        self.listener_running = False
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join()
        self.disconnect_button.config(text="Disconnected", bg="grey", relief=tk.SUNKEN)
        self.connect_button.config(text="Connect", bg="SystemButtonFace", relief=tk.RAISED)
        self.record_button.config(text="Record", bg="SystemButtonFace", relief=tk.RAISED)
        # messagebox.showinfo("Info", "UDP listener stopped")

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
            # messagebox.showinfo("Info", f"Recording started at: {self.file_path}")

    def load(self):
        file_path = filedialog.askopenfilename(initialdir=self.project_dir, filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.load_path.set(file_path)
            self.play_path.set(file_path)  # Set the play path to the loaded file
            self.load_entry.config(width=len(file_path))
            # messagebox.showinfo("Info", f"Loaded file: {file_path}")

    def start_playing(self):
        if self.play_path.get():
            self.playing = True
            self.play_thread = threading.Thread(target=self.play, daemon=True)
            self.play_thread.start()
        else:
            messagebox.showwarning("Warning", "No file loaded to play!")

    def stop_playing(self):
        self.playing = False
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join()

    def play(self):
        sending_ip = self.sending_ip_address.get()
        sending_port = self.sending_port.get()
        while self.playing:
            with open(self.play_path.get(), 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if not self.playing:
                        break
                    timestamp, data = line.strip().split(': ', 1)
                    self.send_udp_message(sending_ip, sending_port, data)
                    time.sleep(0.1)  # Add a small delay to simulate real-time sending
            # messagebox.showinfo("Info", f"Playing: {self.play_path.get()}")

    def send_udp_message(self, ip, port, message):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), (ip, port))
        print(f"Sent message: {message} to {ip}:{port}")

    def udp_broadcast_listener(self):
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Allow the socket to reuse the address
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind the socket to the IP and listen_port
        ip = self.listen_ip_address.get()
        listen_port = self.listen_port.get()
        sock.bind((ip, listen_port))
        
        print(f"Listening for UDP broadcast on {ip}:{listen_port}...")
        
        while self.listener_running:
            # Receive data from the socket
            data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            print(f"elapsed_time: {elapsed_time:.4f}, received data: {data} from {addr}")
            if self.recording and self.file_path:
                with open(self.file_path, 'a') as file:
                    file.write(f"{elapsed_time:.4f}: {data}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = Recorder(root)
    root.mainloop()