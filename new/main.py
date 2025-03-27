import os
import struct
import time
import logging
from receivers import ViveUDPReceiverQ
from senders import UDPSenderQ
from player import Player
from vive_recorder import Recorder

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

logging.basicConfig(level=logging.INFO, format='%(filename)s - %(levelname)s - %(message)s')

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vive Tracker Recorder")
        self.geometry("400x400")
        self.recorder = None
        self.player = None
        self.sender = None
        self.receiver = None
        self.file_path = None
        self.file_type = None
        self.save_file_path = None
        self.save_file_type = None

        self.receiver_ip = '127.0.0.1'
        self.receiver_port = 2222
        self.sender_ip = '127.0.0.1'
        self.sender_port = 2223

        self.init_ui()

    def init_ui(self):

        self.style = ttk.Style()
        self.style.theme_use('clam') # clam, alt, default, classic

        # Use frames to group related widgets
        input_frame = ttk.LabelFrame(self, text="Network Settings")
        input_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

        # Receiver IP and Port
        self.receiver_ip_label = ttk.Label(input_frame, text="Receiver IP:")
        self.receiver_ip_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.receiver_ip_entry = ttk.Entry(input_frame)
        self.receiver_ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.receiver_ip_entry.insert(0, self.receiver_ip)
        self.receiver_ip_entry.config(state='disabled')

        self.receiver_port_label = ttk.Label(input_frame, text="Receiver Port:")
        self.receiver_port_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.receiver_port_entry = ttk.Entry(input_frame)
        self.receiver_port_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.receiver_port_entry.insert(0, self.receiver_port)

        # Sender IP and Port
        self.sender_ip_label = ttk.Label(input_frame, text="Sender IP:")
        self.sender_ip_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.sender_ip_entry = ttk.Entry(input_frame)
        self.sender_ip_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.sender_ip_entry.insert(0, self.sender_ip)

        self.sender_port_label = ttk.Label(input_frame, text="Sender Port:")
        self.sender_port_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.sender_port_entry = ttk.Entry(input_frame)
        self.sender_port_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.sender_port_entry.insert(0, self.sender_port)


        # Use ttk buttons and labels
        button_frame = ttk.LabelFrame(self, text="Controls")
        button_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew")

        self.btn_save = ttk.Button(button_frame, text="Save Data Location", command=self.save_data_location)
        self.btn_save.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.save_data_label = ttk.Label(button_frame, text="No data loaded.")
        self.save_data_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.btn_start = ttk.Button(button_frame, text="Start Recording", command=self.start_recording)
        self.btn_start.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.btn_stop = ttk.Button(button_frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.btn_stop.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.btn_load = ttk.Button(button_frame, text="Load Data", command=self.load_data)
        self.btn_load.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.load_data_label = ttk.Label(button_frame, text="No data loaded.")
        self.load_data_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.btn_play = ttk.Button(button_frame, text="Play Data", command=self.play_data, state=tk.DISABLED)
        self.btn_play.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.btn_stop_play = ttk.Button(button_frame, text="Stop Playback", command=self.stop_playback, state=tk.DISABLED)
        self.btn_stop_play.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # fill the empty space
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # set background color in rgb
        self.configure(bg="#dfdfdf")

        # set window size 
        self.minsize(500, 150)

    def start_recording(self):
        if self.receiver:
            self.receiver.close()
        if self.sender:
            self.sender.close()
        if self.recorder:
            self.recorder.close()        
        if self.receiver_ip == '127.0.0.1':
            self.receiver_ip = ''
        self.receiver = ViveUDPReceiverQ(ip=self.receiver_ip, port=self.receiver_port)
        self.sender = UDPSenderQ(ip=self.sender_ip, port=self.sender_port)
        self.recorder = Recorder(callback_data=self.receiver.get_data_block, callback=self.sender.update)
        if self.save_file_path:
            self.receiver.start()
            self.recorder.start()
            self.sender.start()
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.btn_play.config(state=tk.DISABLED)
        else:
            self.save_data_label.config(text="Please select a save location.")

    def stop_recording(self):
        self.recorder.stop()
        self.receiver.stop()
        self.sender.stop()
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_play.config(state=tk.NORMAL)
        if self.save_file_type == "bin":
            self.recorder.save_binary(self.save_file_path)
        elif self.save_file_type == "txt":
            self.recorder.save_text(self.save_file_path)
        else:
            logging.error("Invalid file type.")
        

    def play_data(self):
        if self.sender:
            self.sender.close()
        self.sender = UDPSenderQ(ip=self.sender_ip, port=self.sender_port)
        self.sender.start()
        self.player.set_callback(self.sender.update)
        self.player.play_in_thread()
        self.btn_play.config(state=tk.DISABLED)
        self.btn_stop_play.config(state=tk.NORMAL)

    def stop_playback(self):
        self.player.stop()
        self.sender.stop()
        self.btn_play.config(state=tk.NORMAL)
        self.btn_stop_play.config(state=tk.DISABLED)

    def load_data(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path.endswith(".bin"):
            self.file_type = "bin"
        elif self.file_path.endswith(".txt"):
            self.file_type = "txt"
        else:
            messagebox.showerror("Error", "Invalid file type. Please select a .bin or .txt file.")
            return
        self.player = Player()
        if self.file_type == "bin":
            self.player.load_from_bin(self.file_path)
        elif self.file_type == "txt":
            self.player.load_from_text(self.file_path)

        self.btn_play.config(state=tk.NORMAL)
        self.load_data_label.config(text=self.trim_path(self.file_path))


    def save_data_location(self):
        # open a file dialog to select the save location
        self.save_file_path = filedialog.asksaveasfilename()
        # check if bin or txt is already in the file path and add it if not
        self.save_file_type = "bin"
        if not self.save_file_path.endswith(".bin"):
            if self.save_file_path.endswith(".txt"):
                self.save_file_type = "txt"
            else: 
                self.save_file_type = "bin"
                self.save_file_path += ".bin"
        # update the label 
        self.save_data_label.config(text=self.trim_path(self.save_file_path))

    def trim_path(self, path):
        if len(path) > 50:
            return "..." + path[-50:]
        return path



if __name__ == "__main__":
    app = App()
    app.mainloop()