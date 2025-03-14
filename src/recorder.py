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

        # Record Button and Entry
        self.record_button = tk.Button(root, text="Record", command=self.record)
        self.record_button.grid(row=0, column=0, padx=10, pady=10)

        self.record_entry = tk.Entry(root, textvariable=self.record_path, state='readonly')
        self.record_entry.grid(row=0, column=1, padx=10, pady=10)

        # Stop Button
        self.stop_button = tk.Button(root, text="Stop", command=self.stop)
        self.stop_button.grid(row=1, column=0, padx=10, pady=10)

        # Load Button and Entry
        self.load_button = tk.Button(root, text="Load", command=self.load)
        self.load_button.grid(row=2, column=0, padx=10, pady=10)

        self.load_entry = tk.Entry(root, textvariable=self.load_path, state='readonly')
        self.load_entry.grid(row=2, column=1, padx=10, pady=10)

        # Play Button
        self.play_button = tk.Button(root, text="Play", command=self.play)
        self.play_button.grid(row=3, column=0, padx=10, pady=10)

        # Get the directory of the current script
        self.project_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'recordings'))

    def record(self):
        file_path = filedialog.asksaveasfilename(initialdir=self.project_dir, defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.record_path.set(file_path)
            self.play_path.set(file_path)  # Set the play path to the recorded file
            # Create the file to ensure it exists
            with open(file_path, 'w') as file:
                file.write("")
            # Start the UDP listener in a separate thread
            self.recording = True
            self.start_time = time.time()
            self.recording_thread = threading.Thread(target=self.udp_broadcast_listener, args=(file_path, 2222), daemon=True)
            self.recording_thread.start()
            messagebox.showinfo("Info", f"Recording started at: {file_path}")

    def load(self):
        file_path = filedialog.askopenfilename(initialdir=self.project_dir, filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.load_path.set(file_path)
            self.play_path.set(file_path)  # Set the play path to the loaded file
            messagebox.showinfo("Info", f"Loaded file: {file_path}")

    def play(self):
        if self.play_path.get():
            messagebox.showinfo("Info", f"Playing: {self.play_path.get()}")
        else:
            messagebox.showwarning("Warning", "No file loaded to play!")

    def stop(self):
        self.recording = False
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join()
        messagebox.showinfo("Info", f"Recording saved at: {self.record_path.get()}")

    def udp_broadcast_listener(self, file_path, port):
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Allow the socket to reuse the address
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind the socket to the port
        sock.bind(('', port))
        
        print(f"Listening for UDP broadcast on port {port}...")
        
        with open(file_path, 'a') as file:
            while self.recording:
                # Receive data from the socket
                data, addr = sock.recvfrom(1024)  # Buffer size is 1024 bytes
                elapsed_time = time.time() - self.start_time
                print(f"Received data: {data} from {addr}")
                file.write(f"{elapsed_time:.4f}: {data}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = Recorder(root)
    root.mainloop()