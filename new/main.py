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
        self.recorder = None
        self.player = None
        self.sender = None
        self.receiver = None
        self.file_path = None
        self.file_type = None
        self.save_file_path = None
        self.save_file_type = None

        self.receiver_ip = '127.0.0.1'
        self.receiver_port = 2223
        self.sender_ip = '127.0.0.1'
        self.sender_port = 2224

        self.states = [
            "Idle",
            "Recording",
            "Playing"
        ]
        self.state = self.states[0]
        self.init_ui()

        self.player = Player()


    def init_ui(self):

        self.style = ttk.Style()
        self.style.theme_use('clam') # clam, alt, default, classic

        self.minsize(500, 150)
        self.configure(bg="#dfdfdf")
        self.protocol("WM_DELETE_WINDOW", self.exit_gracefully)
        

        # Use frames to group related widgets
        input_frame = ttk.LabelFrame(self, text="Network Settings")
        input_frame.grid(row=0, column=0, padx=10, sticky="ew")

        # Receiver IP and Port
        self.receiver_ip_label = ttk.Label(input_frame, text="Receiver IP:")
        self.receiver_ip_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.receiver_ip_entry = ttk.Entry(input_frame)
        self.receiver_ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.receiver_ip_entry.insert(0, self.receiver_ip)
        # self.receiver_ip_entry.config(state='disabled')

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
        button_frame.grid(row=1, column=0, padx=10, sticky="ew")

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

        self.update_state("Idle")


    def exit_gracefully(self):
        logging.info("Exiting...")
        if self.receiver:
            self.receiver.close()
        if self.sender:
            self.sender.close()
        if self.recorder:
            self.recorder.close()
        if self.player:
            self.player.stop()
        self.destroy()


    def update_state(self, new_state):

        self.state = new_state

        # signals
        is_save_file_path_valid = self.save_file_path is not None
        is_load_file_path_valid = self.file_path is not None
    
        if self.state == self.states[0]: # idle
            # save
            self.btn_save.config(state=tk.NORMAL)
            if is_save_file_path_valid:
                self.btn_start.config(state=tk.NORMAL)
            else:
                self.btn_start.config(state=tk.DISABLED)
                self.save_data_label.config(text="Please select a save location.")
            
            # load 
            self.btn_load.config(state=tk.NORMAL)
            if is_load_file_path_valid:
                self.btn_play.config(state=tk.NORMAL)
            else:
                self.btn_play.config(state=tk.DISABLED)
                self.load_data_label.config(text="Please select a load location.")
            
            # stop buttons: play and record
            self.btn_stop.config(state=tk.DISABLED)
            self.btn_stop_play.config(state=tk.DISABLED)
        
        elif self.state == self.states[1]: # recording
            self.btn_load.config(state=tk.DISABLED)
            self.btn_play.config(state=tk.DISABLED)
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.btn_stop_play.config(state=tk.DISABLED)
        
        elif self.state == self.states[2]: # playing
            self.btn_load.config(state=tk.DISABLED)
            self.btn_play.config(state=tk.DISABLED)
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.DISABLED)
            self.btn_stop_play.config(state=tk.NORMAL)

    def update_variables(self):
        self.receiver_ip = self.receiver_ip_entry.get()
        self.receiver_port = int(self.receiver_port_entry.get())
        self.sender_ip = self.sender_ip_entry.get()
        self.sender_port = int(self.sender_port_entry.get())

    def start_recording(self):
        self.update_variables()
        if self.receiver:
            self.receiver.close()
        if self.sender:
            self.sender.close()
        if self.recorder:
            self.recorder.close()        
        if self.receiver_ip == '127.0.0.1':
            self.receiver_ip = ''
        logging.info(f"Starting recording with receiver: {self.receiver_ip}:{self.receiver_port} and sender: {self.sender_ip}:{self.sender_port}")
        self.receiver = ViveUDPReceiverQ(ip=self.receiver_ip, port=self.receiver_port)
        self.sender = UDPSenderQ(ip=self.sender_ip, port=self.sender_port)
        self.recorder = Recorder(callback_data=self.receiver.get_data_block, callback=self.sender.update)
        if not self.receiver.start():
            messagebox.showerror("Error", "Failed to start receiver. Check the IP and Port.")
            return
        if not self.recorder.start():
            messagebox.showerror("Error", "Failed to start recorder.")
            self.receiver.close()
            return
        if not self.sender.start():
            messagebox.showerror("Error", "Failed to start sender. Check the IP and Port.")
            self.receiver.close()
            self.recorder.close()
            return
        self.update_state("Recording")
            

    def stop_recording(self):
        self.recorder.stop()
        self.receiver.close()
        self.sender.stop()
        self.recorder.save(self.save_file_path)
        self.update_state("Idle")
        

    def play_data(self):
        self.update_variables()
        if self.sender:
            self.sender.close()
        self.sender = UDPSenderQ(ip=self.sender_ip, port=self.sender_port)
        if not self.sender.start():
            messagebox.showerror("Error", "Failed to start sender. Check the IP and Port.")
            return
        self.player.load(self.file_path)
        self.player.set_callback(self.sender.update)
        if not self.player.start():
            messagebox.showerror("Error", "Failed to start player.")
            self.sender.close()
            return
        self.update_state("Playing")

    def stop_playback(self):
        self.player.stop()
        self.sender.stop()
        self.update_state("Idle")

    def load_data(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            if not self.file_path.endswith(".bin") and not self.file_path.endswith(".txt"):
                messagebox.showerror("Error", "Invalid file type. Please select a .bin or .txt file.")
                self.file_path = None
            self.load_data_label.config(text=self.trim_path(self.file_path))
        else:
            messagebox.showwarning("Warning", "No file selected.")
            self.file_path = None
        self.update_state("Idle")    

    def save_data_location(self):
        self.save_file_path = filedialog.asksaveasfilename()
        if self.save_file_path:
            if not self.save_file_path.endswith(".bin") and not self.save_file_path.endswith(".txt"):
                    self.save_file_path += ".bin"
            self.save_data_label.config(text=self.trim_path(self.save_file_path))
        else:
            messagebox.showwarning("Warning", "No save location selected.")
            self.save_file_path = None
        self.update_state("Idle")

    def trim_path(self, path):
        if len(path) > 50:
            return "..." + path[-50:]
        return path



if __name__ == "__main__":
    app = App()
    app.mainloop()