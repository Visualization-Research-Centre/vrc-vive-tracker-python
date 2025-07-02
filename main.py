import logging
import json

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from src.sources import UDPReceiverQ, Player, Synchronizer
from src.senders import UDPSenderQ
from src.recorder import Recorder
from src.processor import Processor
from src.visualizer import Visualizer
from src.analyser import Analyser

logging.basicConfig(
    level=logging.INFO, format="%(filename)s - %(levelname)s - %(message)s"
)


class App(tk.Tk):
    def __init__(self, config=None):
        super().__init__()
        self.title("FCS Tracker Recorder")

        # default network settings
        self.receiver_ip = "127.0.0.1"
        self.receiver_port = 2221
        self.sender_ip = "127.0.0.1"
        self.sender_ip_list = ["192.168.50.255"]
        self.sender_port = 2223
        self.ignore_tracker_names = ["2B9219E9"]

        # app variables
        self.file_path = None
        self.save_file_path = None
        self.compute_blobs = 0
        self.augment_slider_value = 0
        self.compute_blobs_slider_value = 0
        self.config_data = None

        # actors
        self.recorder = None
        self.player = None
        self.sender = None
        self.receiver = None
        self.processor = None
        self.src = None
        self.synchronizer = None
        self.analyser = None

        if config:
            # Load configuration from file
            logging.info(f"Loading configuration from {config}")
            with open(config, "r", encoding="utf-8") as f:
                self.config_data = json.load(f)
                sender_list = self.config_data.get("sender_list", None)
                if sender_list:
                    self.sender_ip_list = sender_list
                self.receiver_ip = self.config_data.get("receiver_ip", self.receiver_ip)
                self.receiver_port = self.config_data.get(
                    "receiver_port", self.receiver_port
                )
                self.sender_ip = self.config_data.get("sender_ip", self.sender_ip)
                self.sender_port = self.config_data.get("sender_port", self.sender_port)
                self.ignore_tracker_names = self.config_data.get(
                    "ignore_tracker_names", self.ignore_tracker_names
                )
                
        

        # states
        self.states = ["Idle", "Recording", "Playing", "Testing"]
        self.state = self.states[0]
        self.init_ui()
        
        self.player = Player()
        self.visualizer = Visualizer(self.canvas, self)
        self.visualizer.start()
        
        # set UI
        self.dropdown.current(0)
        self.enable_visualisation_var.set(1)
        self.ignore_tracker_names_var.set(1)
        self.compute_blobs_slider.set(10)
        self.augment_var.set(0)
        self.sync_with_receiver_var.set(0)
        self.visualize_blobs_var.set(0)
        
        
        self.network_visible = True  # Track visibility state
        
        
        self.update_state("Idle")
        self.update_augment_slider(None)
        self.update_compute_blobs_slider(None)
        self.handle_visualisation_selection(None)
        self.dropdown_var.set("None")
        
        
            # Add this method to your class
    def toggle_network_settings(self, event=None):
        """Toggle visibility of network settings"""
        if self.network_visible:
            self.input_frame.grid_remove()
            self.network_toggle.config(text="► Network Settings")
            self.network_visible = False
        else:
            self.input_frame.grid()
            self.network_toggle.config(text="▼ Network Settings")
            self.network_visible = True

    def init_ui(self):

        self.style = ttk.Style()
        self.style.theme_use("clam")  # clam, alt, default, classic
        self.configure(bg="#dfdfdf")
        self.protocol("WM_DELETE_WINDOW", self.exit_gracefully)
        
        # Network container frame
        network_container = ttk.Frame(self)
        network_container.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # Toggle button for network settings
        self.network_toggle = ttk.Label(
            network_container, 
            text="▼ Network Settings",
            cursor="hand2"
        )
        self.network_toggle.grid(row=0, column=0,  padx=0, pady=0 , sticky="w")
        self.network_toggle.bind("<Button-1>", self.toggle_network_settings)
        
        # Network frame (initially visible)
        self.input_frame = ttk.LabelFrame(network_container, text="")
        self.input_frame.grid(row=1, column=0, padx=0, pady=0, sticky="ew")

        # Receiver IP and Port
        self.receiver_ip_label = ttk.Label(self.input_frame, text="Receiver IP:")
        self.receiver_ip_label.grid(row=0, column=0, padx=5, pady=0, sticky="w")

        self.receiver_ip_entry = ttk.Entry(self.input_frame)
        self.receiver_ip_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.receiver_ip_entry.insert(0, self.receiver_ip)

        self.receiver_port_label = ttk.Label(self.input_frame, text="Receiver Port:")
        self.receiver_port_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.receiver_port_entry = ttk.Entry(self.input_frame)
        self.receiver_port_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.receiver_port_entry.insert(0, self.receiver_port)

        # Sender IP and Port
        self.sender_ip_label = ttk.Label(self.input_frame, text="Sender IP:")
        self.sender_ip_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.sender_ip_entry = ttk.Entry(self.input_frame)
        self.sender_ip_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.sender_ip_entry.insert(0, self.sender_ip)

        self.sender_port_label = ttk.Label(self.input_frame, text="Sender Port:")
        self.sender_port_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.sender_port_entry = ttk.Entry(self.input_frame)
        self.sender_port_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.sender_port_entry.insert(0, self.sender_port)

        # Test Connection
        self.connect_var = tk.IntVar()
        self.connect_checkbox = ttk.Checkbutton(
            self.input_frame,
            text="Test",
            variable=self.connect_var,
            command=self.handle_connect_checkbox,
        )
        self.connect_checkbox.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self.sender_use_list_var = tk.IntVar()
        self.sender_use_list_checkbox = ttk.Checkbutton(
            self.input_frame,
            text="Use Sender list",
            variable=self.sender_use_list_var,
            command=self.handle_sender_use_list,
        )
        self.sender_use_list_checkbox.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Controls frame
        button_frame = ttk.LabelFrame(self, text="Controls")
        button_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.btn_save = ttk.Button(
            button_frame, text="Save Data", command=self.save_data_location
        )
        self.btn_save.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.save_data_label = ttk.Label(button_frame, text="No data loaded.")
        self.save_data_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.btn_load = ttk.Button(
            button_frame, text="Load Data", command=self.load_data
        )
        self.btn_load.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.btn_record = ttk.Button(
            button_frame, text="Record", command=self.handle_recording
        )
        self.btn_record.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.btn_analyze = ttk.Button(
            button_frame, text="Analyze Data", command=self.analyze_data
        )
        self.btn_analyze.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.load_data_label = ttk.Label(button_frame, text="No data loaded.")
        self.load_data_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        play_frame = ttk.Frame(button_frame)
        play_frame.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.btn_play = ttk.Button(
            button_frame, text="Run", command=self.handle_process_button
        )
        self.btn_play.grid(row=3, column=0, padx=5, pady=5, sticky="w")

        self.btn_pause = ttk.Button(
            play_frame, text="Pause", command=self.handle_pause_button
        )
        self.btn_pause.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.sync_with_receiver_var = tk.IntVar()
        self.sync_with_receiver_checkbox = ttk.Checkbutton(
            play_frame,
            text="Sync",
            variable=self.sync_with_receiver_var,
            command=self.handle_sync_with_receiver_checkbox,
        )
        self.sync_with_receiver_checkbox.grid(
            row=3, column=2, padx=5, pady=5, sticky="w"
        )

        # Process frame
        process_frame = ttk.LabelFrame(self, text="Process")
        process_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        slider_frame = ttk.Frame(process_frame)
        slider_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew")

        # AUGMENT
        self.augment_data_label = ttk.Label(slider_frame, text="Augment Data")
        self.augment_data_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.augment_var = tk.IntVar()
        self.augment_checkbox = ttk.Checkbutton(
            slider_frame,
            variable=self.augment_var,
            command=self.handle_augment_checkbox,
        )
        self.augment_checkbox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.augment_slider = ttk.Scale(
            slider_frame,
            from_=1,
            to=20,
            orient=tk.HORIZONTAL,
        )
        self.augment_slider.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.augment_slider.set(1)
        self.augment_slider.bind("<ButtonRelease-1>", self.update_augment_slider)
        self.augment_slider.bind("<Motion>", self.update_augment_slider)

        self.augment_slider_label = ttk.Label(slider_frame)
        self.augment_slider_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # BLOBS
        self.compute_blobs_label = ttk.Label(slider_frame, text="Blobs")
        self.compute_blobs_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.compute_blobs_slider = ttk.Scale(
            slider_frame, from_=1, to=40, orient=tk.HORIZONTAL
        )
        self.compute_blobs_slider.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        self.compute_blobs_slider_label = ttk.Label(slider_frame)
        self.compute_blobs_slider_label.grid(
            row=1, column=3, padx=5, pady=5, sticky="w"
        )
        self.compute_blobs_slider.bind(
            "<ButtonRelease-1>", self.update_compute_blobs_slider
        )
        self.compute_blobs_slider.bind("<Motion>", self.update_compute_blobs_slider)

        # OTHER
        self.ignore_tracker_names_var = tk.IntVar()
        self.ignore_tracker_names_checkbox = ttk.Checkbutton(
            process_frame,
            text="Ignore FCS Tracker Names",
            variable=self.ignore_tracker_names_var,
            command=self.handle_ignore_trackers,
        )
        self.ignore_tracker_names_checkbox.grid(
            row=7, column=0, padx=5, pady=5, sticky="w"
        )

        self.ignore_tracker_names_entry = ttk.Entry(process_frame, width=35)
        self.ignore_tracker_names_entry.grid(
            row=8, column=0, padx=5, pady=5, sticky="ew"
        )
        self.ignore_tracker_names_entry.insert(
            0, ", ".join(self.ignore_tracker_names)
        )
        self.ignore_tracker_names_entry.bind(
            "<Return>", self.update_ignore_tracker_names
        )
        self.ignore_tracker_names_entry.bind(
            "<FocusOut>", self.update_ignore_tracker_names
        )

        self.other_ctrl_frame = ttk.Frame(process_frame)
        self.other_ctrl_frame.grid(row=9, column=0, padx=0, pady=0, sticky="ew")
        self.debug_var = tk.IntVar()
        self.debug_checkbox = ttk.Checkbutton(
            self.other_ctrl_frame,
            text="Debug Mode",
            variable=self.debug_var,
            command=self.handle_debug_checkbox,
        )
        self.debug_checkbox.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.bypass_processor_var = tk.IntVar()
        self.bypass_processor_checkbox = ttk.Checkbutton(
            self.other_ctrl_frame, text="Bypass", variable=self.bypass_processor_var,
            command= lambda: ( self.processor.set_bypass(self.bypass_processor_var.get()) if self.processor else None ) 
        )
        self.bypass_processor_checkbox.grid(
            row=0, column=1, padx=5, pady=5, sticky="w"
        )

        # Visualisation
        self.visualisation_frame = ttk.LabelFrame(self, text="Visualisation")
        self.visualisation_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.visualisation_ctrl_frame = ttk.Frame(self.visualisation_frame)
        self.visualisation_ctrl_frame.grid(row=0, column=0, padx=0, pady=0, sticky="ew")

        self.enable_visualisation_var = tk.IntVar()
        self.enable_visualisation_checkbox = ttk.Checkbutton(
            self.visualisation_ctrl_frame,
            text="Enable",
            variable=self.enable_visualisation_var,
            command=self.handle_visualisation_checkbox,
        )
        self.enable_visualisation_checkbox.grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )

        # dropdown
        self.dropdown_label = ttk.Label(
            self.visualisation_ctrl_frame, text="Visualisation:"
        )
        self.dropdown_label.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.dropdown_var = tk.StringVar()
        self.dropdown = ttk.Combobox(
            self.visualisation_ctrl_frame,
            textvariable=self.dropdown_var,
            values=["None", "all_in_radius", "unique", "unique_w_tracing", "nearest"],
            state="readonly", width=12,
        )
        self.dropdown.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.dropdown.bind("<<ComboboxSelected>>", self.handle_visualisation_selection)

        # draw blobs
        self.visualize_blobs_var = tk.IntVar()
        self.visualize_blobs_checkbox = ttk.Checkbutton(
            self.visualisation_ctrl_frame,
            text="Draw Blobs",
            variable=self.visualize_blobs_var,
            command=lambda: (
                self.visualizer.set_draw_blobs(self.visualize_blobs_var.get())
            ),
        )
        self.visualize_blobs_checkbox.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.canvas = tk.Canvas(
            self.visualisation_frame, width=250, height=250, bg="white"
        )
        self.canvas.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        # fill the empty space
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


    def update_state(self, new_state):

        self.state = new_state

        # signals
        is_save_file_path_valid = self.save_file_path is not None
        is_load_file_path_valid = self.file_path is not None
        is_testing = self.connect_var.get()

        if self.state == self.states[0]:  # idle

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
            self.btn_pause.config(state=tk.DISABLED)
            if is_load_file_path_valid:
                self.load_data_label.config(text=self.trim_path(self.file_path))
                self.btn_analyze.config(state=tk.NORMAL)
            else:
                self.load_data_label.config(text="No data loaded. Using receiver.")
                self.btn_analyze.config(state=tk.DISABLED)

        elif self.state == self.states[1]:  # recording
            self.btn_play.config(state=tk.DISABLED)
            self.btn_save.config(state=tk.DISABLED)
            self.btn_record.config(text="Stop")
            self.connect_checkbox.config(state=tk.DISABLED)
            self.btn_pause.config(state=tk.DISABLED)

        elif self.state == self.states[2]:  # playing
            self.btn_load.config(state=tk.DISABLED)
            self.btn_play.config(text="Stop")
            self.btn_record.config(state=tk.DISABLED)
            self.connect_checkbox.config(state=tk.DISABLED)
            self.btn_pause.config(state=tk.NORMAL)

        if self.state == self.states[3]:  # testing
            pass

        logging.info(f"State: {self.state}")

    def update_variables(self):
        self.receiver_ip = self.receiver_ip_entry.get()
        self.receiver_port = int(self.receiver_port_entry.get())
        self.handle_sender_use_list()
        self.sender_port = int(self.sender_port_entry.get())
        self.bypass_processor = self.bypass_processor_var.get()
        self.ignore_trackers = self.ignore_tracker_names_var.get()
        self.debug = self.debug_var.get()
        if self.receiver_ip == "127.0.0.1":
            self.receiver_ip = ""

    def close_all_actors(self):
        if self.processor:
            self.processor.close()
        if self.recorder:
            self.recorder.close()
        if self.player:
            self.player.close()
        if self.receiver:
            self.receiver.close()
        if self.sender:
            self.sender.close()
        if self.synchronizer:
            self.synchronizer.clear_callbacks()
            self.synchronizer.close()

    ### CONNECTION

    def handle_sender_use_list(self):
        if self.sender_use_list_var.get():
            self.sender_ip = self.sender_ip_list
            logging.info(f"Using sender list: {self.sender_ip}")
        else:
            self.sender_ip = self.sender_ip_entry.get()
            logging.info(f"Using sender IP: {self.sender_ip}")

    def handle_connect_checkbox(self):
        if self.connect_var.get():
            self.connect_test()
        else:
            self.disconnect_test()

    def connect_test(self):
        logging.info("Enable bypass mode.")
        self.update_variables()
        self.sender = UDPSenderQ(ip=self.sender_ip, port=self.sender_port, debug=True)
        self.receiver = UDPReceiverQ(
            ip=self.receiver_ip, port=self.receiver_port, callback=self.sender.update
        )
        if not self.receiver.start():
            messagebox.showerror(
                "Error", "Failed to start receiver. Check the IP and Port."
            )
            return
        if not self.sender.start():
            messagebox.showerror(
                "Error", "Failed to start sender. Check the IP and Port."
            )
            self.receiver.close()
            return
        # self.update_state("Testing")

    def disconnect_test(self):
        logging.info("Disable bypass mode.")
        if self.receiver:
            self.receiver.close()
        if self.sender:
            self.sender.close()
        self.update_state("Idle")
        self.connect_var.set(0)

    ### RECORDING

    def handle_recording(self):
        if self.state == self.states[1]:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.disconnect_test()
        self.update_variables()
        if self.receiver:
            self.receiver.close()
        if self.sender:
            self.sender.close()
        if self.recorder:
            self.recorder.close()
        logging.info(
            f"Starting recording with receiver: {self.receiver_ip}:{self.receiver_port} and sender: {self.sender_ip}:{self.sender_port}"
        )
        self.receiver = UDPReceiverQ(ip=self.receiver_ip, port=self.receiver_port)
        self.sender = UDPSenderQ(ip=self.sender_ip, port=self.sender_port)
        self.recorder = Recorder(
            callback_data=self.receiver.get_data_block, callback=self.sender.update
        )
        if not self.receiver.start():
            messagebox.showerror(
                "Error", "Failed to start receiver. Check the IP and Port."
            )
            return
        if not self.recorder.start():
            messagebox.showerror("Error", "Failed to start recorder.")
            self.receiver.close()
            return
        if not self.sender.start():
            messagebox.showerror(
                "Error", "Failed to start sender. Check the IP and Port."
            )
            self.receiver.close()
            self.recorder.close()
            return
        self.update_state("Recording")

    def stop_recording(self):
        self.close_all_actors()
        self.recorder.save(self.save_file_path)
        self.update_state("Idle")

        ### FILE HANDLING

    def load_data(self):
        self.file_path = filedialog.askopenfilename()
        if self.file_path:
            if not self.file_path.endswith(".bin") and not self.file_path.endswith(
                ".txt"
            ):
                messagebox.showerror(
                    "Error", "Invalid file type. Please select a .bin or .txt file."
                )
                self.file_path = None
            self.load_data_label.config(text=self.trim_path(self.file_path))
        else:
            messagebox.showwarning("Warning", "No file selected.")
            self.file_path = None
        self.update_state(self.state)

    def save_data_location(self):
        self.save_file_path = filedialog.asksaveasfilename()
        if self.save_file_path:
            if not self.save_file_path.endswith(
                ".bin"
            ) and not self.save_file_path.endswith(".txt"):
                self.save_file_path += ".bin"
            self.save_data_label.config(text=self.trim_path(self.save_file_path))
        else:
            self.save_file_path = None
        self.update_state(self.state)

    def handle_sync_with_receiver_checkbox(self):
        if self.sync_with_receiver_var.get():
            if self.processor:
                if self.receiver:
                    self.receiver.close()
                self.receiver = UDPReceiverQ(
                    ip=self.receiver_ip, port=self.receiver_port
                )
                if not self.receiver.start():
                    messagebox.showerror(
                        "Error", "Failed to start receiver. Check the IP and Port."
                    )
                    return
                if self.synchronizer:
                    self.synchronizer.add_callback(
                        {
                            "name": "receiver",
                            "callback": self.receiver.get_data_block,
                            "timeout": 0.1,
                        }
                    )
                    logging.info("Sync with Receiver enabled.")
        else:
            if self.processor:
                if self.receiver:
                    if self.synchronizer:
                        self.synchronizer.remove_callback("receiver")
                        logging.info("Sync with Receiver disabled.")
                        
    def analyze_data(self):
        if not self.file_path:
            messagebox.showwarning("Warning", "No data loaded. Please load data first.")
            return

        # Create an Analyser instance
        self.analyser = Analyser(
            input_file=self.file_path, output_dir="output"
        )
        
        # Process the tracking data
        try:
            self.analyser.process_tracking_data()
            self.analyser.visualize_results()
        except Exception as e:
            logging.error(f"Error during analysis: {e}")
            messagebox.showerror("Error", f"Failed to analyze data: {e}")

    #### PROCESSING

    def handle_process_button(self):
        if self.state == self.states[2]:
            self.stop_processing()
        else:
            self.process_data()

    def process_data(self):
        self.update_variables()
        self.close_all_actors()
        self.disconnect_test()

        # start the sender
        self.sender = UDPSenderQ(ip=self.sender_ip, port=self.sender_port)
        if not self.sender.start():
            messagebox.showerror(
                "Error", "Failed to start sender. Check the IP and Port."
            )
            return

        self.synchronizer = Synchronizer()

        if self.file_path:
            self.player.load(self.file_path)
            if not self.player.start():
                messagebox.showerror("Error", "Failed to start Player.")
                return
            self.synchronizer.add_callback(
                {
                    "name": "player",
                    "callback": self.player.get_data_block,
                    "timeout": 0.1,
                }
            )

        if self.sync_with_receiver_var.get() or self.file_path is None:
            self.receiver = UDPReceiverQ(ip=self.receiver_ip, port=self.receiver_port)
            if not self.receiver.start():
                messagebox.showerror(
                    "Error", "Failed to start receiver. Check the IP and Port."
                )
                return
            self.synchronizer.add_callback(
                {
                    "name": "receiver",
                    "callback": self.receiver.get_data_block,
                    "timeout": 0.1,
                }
            )

        if not self.synchronizer.start():
            messagebox.showerror("Error", "Failed to start Synchronizer.")
            return
    
        # start the processor
        self.processor = Processor(
            callback_data=self.synchronizer.get_data_block,
            callback=self.sender.update,
            callback_vis=self.visualizer.update,
            config=self.config_data,
        )
        self.processor.set_num_augmentations(self.augment_slider_value)
        self.processor.set_radius(self.compute_blobs_slider_value)
        self.processor.set_debug(self.debug)
        
        if self.bypass_processor:
            self.processor.set_bypass(True)
            logging.info("Bypassing processor.")
        else:
            logging.info(
                f"Processing data with {self.augment_slider_value} augmentations and {self.compute_blobs_slider_value}m radius"
            )
            if self.ignore_trackers:
                logging.info("Ignoring certain FCS tracker names.")
                self.processor.set_ignore_tracker_names(
                    self.ignore_tracker_names
                )
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

    def handle_pause_button(self):
        if self.player:
            if self.player.pause():
                self.btn_pause.config(text="Play")
            else:
                self.btn_pause.config(text="Pause")

    def update_augment_slider(self, event):
        self.augment_slider_value = int(self.augment_slider.get())
        self.augment_slider_label.config(text=str(self.augment_slider_value))
        if self.processor:
            self.processor.set_num_augmentations(self.augment_slider_value)

    def handle_augment_checkbox(self):
        if self.augment_var.get():
            if self.processor:
                logging.info("Augmentation enabled.")
                self.processor.set_augment_data(True)
        else:
            if self.processor:
                logging.info("Augmentation disabled.")
                self.processor.set_augment_data(False)

    def update_compute_blobs_slider(self, event):
        self.compute_blobs_slider_value = self.compute_blobs_slider.get() / 10
        self.compute_blobs_slider_label.config(
            text=str(self.compute_blobs_slider_value)[:4] + " m"
        )
        if self.processor:
            self.processor.set_radius(self.compute_blobs_slider_value)
            self.visualizer.set_radius(self.compute_blobs_slider_value)

    def handle_ignore_trackers(self):
        if self.ignore_tracker_names_var.get():
            logging.info("Ignore FCS Tracker Names enabled.")
            if self.processor:
                self.processor.set_ignore_tracker_names(
                    self.ignore_tracker_names
                )
        else:
            logging.info("Ignore FCS Tracker Names disabled.")
            if self.processor:
                self.processor.set_ignore_tracker_names([])

    def update_ignore_tracker_names(self, event):
        if self.ignore_tracker_names_entry.get():
            self.ignore_tracker_names = [
                name.strip()
                for name in self.ignore_tracker_names_entry.get().split(",")
            ]
            logging.info(
                f"Ignoring FCS Tracker Names: {self.ignore_tracker_names}"
            )
            if self.processor:
                self.processor.set_ignore_tracker_names(
                    self.ignore_tracker_names
                )
        else:
            logging.info("No FCS Tracker Names to ignore.")
            if self.processor:
                self.processor.set_ignore_tracker_names([])

    def handle_debug_checkbox(self):
        if self.debug_var.get():
            if self.processor:
                logging.info("Debug mode enabled.")
                self.processor.set_debug(True)
        else:
            if self.processor:
                logging.info("Debug mode disabled.")
                self.processor.set_debug(False)

    def handle_visualisation_checkbox(self):
        if self.enable_visualisation_var.get():
            logging.info("Visualisation enabled.")
            self.visualizer.set_visualize(True)
        else:
            logging.info("Visualisation disabled.")
            self.visualizer.set_visualize(False)

    def handle_visualisation_selection(self, event):
        logging.info(f"Visualisation mode: {self.dropdown_var.get()}")
        self.visualizer.set_connection_visualisation(self.dropdown_var.get())

    ### UTILS

    def trim_path(self, path):
        if len(path) > 50:
            return "..." + path[-50:]
        return path

    def exit_gracefully(self):
        logging.info("Exiting...")
        try:
            self.close_all_actors()
        except Exception as e:
            logging.error(f"Error while closing actors: {e}")
        self.destroy()
        logging.info("Exited gracefully.")
        self.quit()
        exit(0)
        

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="FCS Tracker Recorder")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        help="Path to the configuration file",
        default="config.json",
    )
    args = parser.parse_args()

    app = App(config=args.config)
    app.mainloop()
