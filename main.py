import os
import struct
import time
import logging
from src.sources import UDPReceiverQ, Player
from src.senders import UDPSenderQ
from src.recorder import Recorder
from src.processor import Processor

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

logging.basicConfig(level=logging.INFO, format='%(filename)s - %(levelname)s - %(message)s')

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vive Tracker Recorder")

        # default network settings
        self.receiver_ip = '127.0.0.1'
        self.receiver_port = 2221
        self.sender_ip = '127.0.0.1'
        self.sender_ip_list = [
            '192.168.50.200',
            '192.168.50.201',
            '192.168.50.202',
            '192.168.50.203',
            '192.168.50.204',
            '192.168.50.205',
            '192.168.50.206',
            '192.168.50.195'
        ]
        self.sender_port = 2223
        self.ignore_vive_tracker_names = ['2B9219E9']
        

        # app variables
        self.file_path = None
        self.save_file_path = None
        self.compute_blobs = 0
        self.augment_slider_value = 0
        self.compute_blobs_slider_value = 0
        
        # actors
        self.recorder = None
        self.player = None
        self.sender = None
        self.receiver = None
        self.processor = None
        self.src = None

        # states
        self.states = [
            "Idle",
            "Recording",
            "Playing",
            "Testing"
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
        

        # Network frame
        input_frame = ttk.LabelFrame(self, text="Network Settings")
        input_frame.grid(row=0, column=0, padx=10, sticky="ew")

        # Receiver IP and Port
        self.receiver_ip_label = ttk.Label(input_frame, text="Receiver IP:")
        self.receiver_ip_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.receiver_ip_entry = ttk.Entry(input_frame)
        self.receiver_ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.receiver_ip_entry.insert(0, self.receiver_ip)

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
        
        self.sender_use_list_var = tk.IntVar()
        self.sender_use_list_checkbox = ttk.Checkbutton(input_frame, text="Use Sender list?", variable=self.sender_use_list_var, command=self.handle_sender_use_list)
        self.sender_use_list_checkbox.grid(row=3, column=2, padx=5, pady=5, sticky="w")
        
        # Test Connection
        self.connect_label = ttk.Label(input_frame, text="Test Connection")
        self.connect_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        
        self.connect_var = tk.IntVar()
        self.connect_checkbox = ttk.Checkbutton(input_frame, variable=self.connect_var, command=self.handle_connect_checkbox)
        self.connect_checkbox.grid(row=4, column=1, padx=5, pady=5, sticky="w")


        # Controls frame
        button_frame = ttk.LabelFrame(self, text="Controls")
        button_frame.grid(row=1, column=0, padx=10, sticky="ew")

        self.btn_save = ttk.Button(button_frame, text="Save Data Location", command=self.save_data_location)
        self.btn_save.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.save_data_label = ttk.Label(button_frame, text="No data loaded.")
        self.save_data_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.btn_record = ttk.Button(button_frame, text="Record", command=self.handle_recording)
        self.btn_record.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.btn_load = ttk.Button(button_frame, text="Load Data", command=self.load_data)
        self.btn_load.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.load_data_label = ttk.Label(button_frame, text="No data loaded.")
        self.load_data_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.btn_play = ttk.Button(button_frame, text="Play Data", command=self.handle_process_button)
        self.btn_play.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        
        
        # Process frame
        process_frame = ttk.LabelFrame(self, text="Process")
        process_frame.grid(row=2, column=0, padx=10, sticky="ew")
        
        self.augemnt_label = ttk.Label(process_frame, text="Augment Data:")
        self.augemnt_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.augment_var = tk.IntVar()
        self.augment_checkbox = ttk.Checkbutton(process_frame, variable=self.augment_var, command=self.handle_augment_checkbox)
        self.augment_checkbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.augment_var.set(0)
        
        self.augment_slider = ttk.Scale(process_frame, from_=1, to=20, orient=tk.HORIZONTAL)
        self.augment_slider.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.augment_slider_label = ttk.Label(process_frame)
        self.augment_slider_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.augment_slider.set(1)
        self.augment_slider.bind("<ButtonRelease-1>", self.update_augment_slider)
        self.augment_slider.bind("<Motion>", self.update_augment_slider)
        
        self.compute_blobs_label = ttk.Label(process_frame, text="Compute Blobs:")
        self.compute_blobs_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
                
        self.compute_blobs_slider = ttk.Scale(process_frame, from_=1, to=40, orient=tk.HORIZONTAL)
        self.compute_blobs_slider.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        self.compute_blobs_slider_label = ttk.Label(process_frame)
        self.compute_blobs_slider_label.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.compute_blobs_slider.set(10)
        self.compute_blobs_slider.bind("<ButtonRelease-1>", self.update_compute_blobs_slider)
        self.compute_blobs_slider.bind("<Motion>", self.update_compute_blobs_slider)
        
        
        self.ignore_vive_tracker_names_var = tk.IntVar()
        self.ignore_vive_tracker_names_checkbox = ttk.Checkbutton(process_frame, text="Ignore Vive Tracker Names?", variable=self.ignore_vive_tracker_names_var, command=self.handle_ignore_vive_trackers)
        self.ignore_vive_tracker_names_checkbox.grid(row=7, column=0, padx=5, pady=5, sticky="w")
        self.ignore_vive_tracker_names_var.set(1)
        
        self.ignore_vive_tracker_names_entry = ttk.Entry(process_frame)
        self.ignore_vive_tracker_names_entry.grid(row=8, column=0, padx=5, pady=5, sticky="ew")
        self.ignore_vive_tracker_names_entry.insert(0, ', '.join(self.ignore_vive_tracker_names))
        self.ignore_vive_tracker_names_entry.bind("<Return>", self.update_ignore_vive_tracker_names)
        self.ignore_vive_tracker_names_entry.bind("<FocusOut>", self.update_ignore_vive_tracker_names)

        self.debug_var = tk.IntVar()
        self.debug_checkbox = ttk.Checkbutton(process_frame, text="Debug Mode", variable=self.debug_var, command=self.handle_debug_checkbox)
        self.debug_checkbox.grid(row=9, column=0, padx=5, pady=5, sticky="w")
        
        self.bypass_processor_var = tk.IntVar()
        self.bypass_processor_checkbox = ttk.Checkbutton(process_frame, text="Bypass processing?", variable=self.bypass_processor_var)
        self.bypass_processor_checkbox.grid(row=9, column=1, padx=5, pady=5, sticky="w")


        # Visualisation
        self.visualisation_frame = ttk.LabelFrame(self, text="Visualisation")
        self.visualisation_frame.grid(row=3, column=0, padx=10, sticky="ew")
        
        self.canvas = tk.Canvas(self.visualisation_frame, width=280, height=280, bg="white")
        self.canvas.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        

        # fill the empty space
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.update_state("Idle")
        self.update_augment_slider(None)
        self.update_compute_blobs_slider(None)


    def update_canvas(self, blobs, trackers):
        """blobs and tracker are in the range of [-4, 4]"""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.delete("all")
        # draw the blobs
        for blob in blobs:
            x, y = blob[0], blob[1]
            r = blob[2] * width / 16 * self.compute_blobs_slider_value
            x = (x + 4) / 8 * width
            y = height - (y + 4) / 8 * height
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill="red", outline="")
        # draw the trackers
        for tracker in trackers:
            x, y = tracker['position'][0], tracker['position'][2]
            x = (x + 4) / 8 * width
            y = height - (y + 4) / 8 * height
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="blue", outline="")
            self.canvas.create_text(x, y-10, text=tracker['name'], fill="black", font=("Arial", 8))
        # draw the coordinate system
        self.canvas.create_line(0, height/2, width, height/2, fill="black", dash=(2, 2))
        self.canvas.create_line(width/2, 0, width/2, height, fill="black", dash=(2, 2))
        # draw the center
        self.canvas.create_oval(width/2-5, height/2-5, width/2+5, height/2+5, fill="green", outline="")

    def update_variables(self):
        self.receiver_ip = self.receiver_ip_entry.get()
        self.receiver_port = int(self.receiver_port_entry.get())
        self.handle_sender_use_list()
        self.sender_port = int(self.sender_port_entry.get())
        self.bypass_processor = self.bypass_processor_var.get()      
        self.ignore_vive_trackers = self.ignore_vive_tracker_names_var.get()  
        self.debug = self.debug_var.get()
        if self.receiver_ip == '127.0.0.1':
            self.receiver_ip = ''

        
    def update_augment_slider(self, event):
        self.augment_slider_value = int(self.augment_slider.get())
        self.augment_slider_label.config(text=str(self.augment_slider_value))
        if self.processor:
            self.processor.set_num_augmentations(self.augment_slider_value)

    def update_compute_blobs_slider(self, event):
        self.compute_blobs_slider_value = self.compute_blobs_slider.get() / 10
        self.compute_blobs_slider_label.config(text=str(self.compute_blobs_slider_value)[:4]+" m")
        if self.processor:
            self.processor.set_radius(self.compute_blobs_slider_value)

    def exit_gracefully(self):
        logging.info("Exiting...")
        try:
            self.close_all_actors()
        except Exception as e:
            logging.error(f"Error while closing actors: {e}")
        self.destroy()


    def close_all_actors(self):
        if self.processor:
            self.processor.stop()
        if self.recorder:
            self.recorder.close()
        if self.player:
            self.player.close()
        if self.receiver:
            self.receiver.close()
        if self.sender:
            self.sender.close()
        if self.src:
            self.src.close()


    def handle_debug_checkbox(self):
        if self.debug_var.get():
            if self.processor:
                logging.info("Debug mode enabled.")
                self.processor.set_debug(True)
        else:
            if self.processor:
                logging.info("Debug mode disabled.")
                self.processor.set_debug(False)

    def handle_ignore_vive_trackers(self):
        if self.ignore_vive_tracker_names_var.get():
            logging.info("Ignore Vive Tracker Names enabled.")
            if self.processor:
                self.processor.set_ignore_vive_tracker_names(self.ignore_vive_tracker_names)
        else:
            logging.info("Ignore Vive Tracker Names disabled.")
            if self.processor:
                self.processor.set_ignore_vive_tracker_names([])

    def update_state(self, new_state):

        self.state = new_state

        # signals
        is_save_file_path_valid = self.save_file_path is not None
        is_load_file_path_valid = self.file_path is not None
        is_testing = self.connect_var.get()
    
        if self.state == self.states[0]: # idle
                
            self.connect_checkbox.config(state=tk.NORMAL)
            # record
            self.btn_save.config(state=tk.NORMAL)
            if is_save_file_path_valid:
                self.btn_record.config(state=tk.NORMAL)
            else:
                self.btn_record.config(state=tk.DISABLED)
                self.save_data_label.config(text="Please select a save location.")
            self.btn_record.config(text="Record")
            
            # load 
            self.btn_load.config(state=tk.NORMAL)
            self.btn_play.config(text="Run")
            self.btn_play.config(state=tk.NORMAL)
            if is_load_file_path_valid:
                self.load_data_label.config(text=self.trim_path(self.file_path))
            else:
                self.load_data_label.config(text="No data loaded. Using receiver.")
        
        elif self.state == self.states[1]: # recording
            self.btn_play.config(state=tk.DISABLED)
            self.btn_save.config(state=tk.DISABLED)
            self.btn_record.config(text="Stop")
            self.connect_checkbox.config(state=tk.DISABLED)
        
        elif self.state == self.states[2]: # playing
            self.btn_load.config(state=tk.DISABLED)
            self.btn_play.config(text="Stop")
            self.btn_record.config(state=tk.DISABLED)
            self.connect_checkbox.config(state=tk.DISABLED)
            
        if self.state == self.states[3]: # testing            
            pass
        
        logging.info(f"State: {self.state}")
            

    def update_ignore_vive_tracker_names(self, event):
        if self.ignore_vive_tracker_names_entry.get():
            self.ignore_vive_tracker_names = [name.strip() for name in self.ignore_vive_tracker_names_entry.get().split(',')]
            logging.info(f"Ignoring Vive Tracker Names: {self.ignore_vive_tracker_names}")
            if self.processor:
                self.processor.set_ignore_vive_tracker_names(self.ignore_vive_tracker_names)
        else:
            logging.info("No Vive Tracker Names to ignore.")
            if self.processor:
                self.processor.set_ignore_vive_tracker_names([])

    def handle_augment_checkbox(self):
        if self.augment_var.get():
            if self.processor:
                logging.info("Augmentation enabled.")
                self.processor.set_augment_data(True)
        else:
            if self.processor:
                logging.info("Augmentation disabled.")
                self.processor.set_augment_data(False)

    def handle_process_button(self):
        if self.state == self.states[2]:
            self.stop_processing()
        else:
            self.process_data()
            
    def handle_sender_use_list(self):
        if self.sender_use_list_var.get():
            self.sender_ip = self.sender_ip_list
            logging.info(f"Using sender list: {self.sender_ip}")
        else:
            self.sender_ip = self.sender_ip_entry.get()
            logging.info(f"Using sender IP: {self.sender_ip}")

    def process_data(self):
        self.update_variables()
        self.close_all_actors()
        self.disconnect_when_testing()

        # start the sender
        self.sender = UDPSenderQ(ip=self.sender_ip, port=self.sender_port)
        if not self.sender.start():
            messagebox.showerror("Error", "Failed to start sender. Check the IP and Port.")
            return
        
        # select source
        self.src = None
        if self.file_path:
            self.src = self.player
            self.src.load(self.file_path)
        else:
            self.src = UDPReceiverQ(ip=self.receiver_ip, port=self.receiver_port)
        if not self.src.start():
            messagebox.showerror("Error", "Failed to start source. Check the IP and Port.")
            return

        # start the processor
        self.processor = Processor(callback_data=self.src.get_data_block, callback=self.sender.update, bypass=self.bypass_processor, debug=self.debug, callback_visualize=self.update_canvas)
        self.processor.set_num_augmentations(self.augment_slider_value)
        self.processor.set_radius(self.compute_blobs_slider_value)
        if self.bypass_processor:
            logging.info("Bypassing processor.")
        else:
            logging.info("Processing data with {} augmentations and {}m radius".format(self.augment_slider_value, self.compute_blobs_slider_value))
            if self.ignore_vive_trackers:
                logging.info("Ignoring certain vive tracker names.")
                self.processor.set_ignore_vive_tracker_names(self.ignore_vive_tracker_names)
            if self.augment_var.get():
                logging.info("Augmenting data.")
                self.processor.set_augment_data(True)
            else:
                logging.info("Not augmenting data.")
                self.processor.set_augment_data(False)
        self.processor.start()

        # update the state
        self.update_state("Playing")


    def stop_processing(self):
        self.close_all_actors()
        self.update_state("Idle")


    def handle_connect_checkbox(self):
        if self.connect_var.get():
            self.connect_test()
        else:
            self.disconnect_test()
        
    def connect_test(self):
        logging.info("Enable bypass mode.")
        self.update_variables()
        self.sender = UDPSenderQ(ip=self.sender_ip, port=self.sender_port, debug=True)
        self.receiver = UDPReceiverQ(ip=self.receiver_ip, port=self.receiver_port, callback=self.sender.update)
        if not self.receiver.start():
            messagebox.showerror("Error", "Failed to start receiver. Check the IP and Port.")
            return
        if not self.sender.start():
            messagebox.showerror("Error", "Failed to start sender. Check the IP and Port.")
            self.receiver.close()
            return
        self.update_state("Testing")
        
        
    def disconnect_test(self):
        logging.info("Disable bypass mode.")
        if self.receiver:
            self.receiver.close()
        if self.sender:
            self.sender.close()
        self.update_state("Idle")
        
    def disconnect_when_testing(self):
        self.disconnect_test()
        self.connect_var.set(0)
        
        
    def handle_recording(self):
        if self.state == self.states[1]:
            self.stop_recording()
        else:
            self.start_recording()
        
    def start_recording(self):
        self.disconnect_when_testing()
        self.update_variables()
        if self.receiver:
            self.receiver.close()
        if self.sender:
            self.sender.close()
        if self.recorder:
            self.recorder.close()
        logging.info(f"Starting recording with receiver: {self.receiver_ip}:{self.receiver_port} and sender: {self.sender_ip}:{self.sender_port}")
        self.receiver = UDPReceiverQ(ip=self.receiver_ip, port=self.receiver_port)
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
        self.close_all_actors()
        self.recorder.save(self.save_file_path)
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

    def save_data_location(self):
        self.save_file_path = filedialog.asksaveasfilename()
        if self.save_file_path:
            if not self.save_file_path.endswith(".bin") and not self.save_file_path.endswith(".txt"):
                    self.save_file_path += ".bin"
            self.save_data_label.config(text=self.trim_path(self.save_file_path))
        else:
            self.save_file_path = None

    def trim_path(self, path):
        if len(path) > 50:
            return "..." + path[-50:]
        return path


    # def play_data(self):
    #     self.update_variables()
    #     if self.sender:
    #         self.sender.close()
    #     self.sender = UDPSenderQ(ip=self.sender_ip, port=self.sender_port)
    #     if not self.sender.start():
    #         messagebox.showerror("Error", "Failed to start sender. Check the IP and Port.")
    #         return
    #     self.player.load(self.file_path)
    #     self.player.set_callback(self.sender.update)
    #     if not self.player.start():
    #         messagebox.showerror("Error", "Failed to start player.")
    #         self.sender.close()
    #         return
    #     self.update_state("Playing")

    # def stop_playback(self):
    #     self.player.stop()
    #     self.sender.stop()
    #     self.update_state("Idle")


if __name__ == "__main__":
    app = App()
    app.mainloop()