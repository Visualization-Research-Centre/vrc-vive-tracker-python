import threading
import logging
from src.vive_decoder import ViveDecoder
from src.vive_encoder import ViveEncoder
from src.vive_blobber import ViveBlobber
from src.vive_augmentor import ViveAugmentor

class Processor:

    def __init__(self, callback_data, callback=None, bypass=False):
        self.callback_data = callback_data
        self.callback = callback
        self.radius = 1
        self.num_augmentations = 1
        self.decoder = ViveDecoder()
        self.encoder = ViveEncoder()
        self.blobber = ViveBlobber(self.radius)
        self.augmentor = ViveAugmentor()
        self.thread = None
        self.running = False
        self.data = None
        self.bypass = bypass
        self.detect_blobs = True
    
    def set_radius(self, radius):
        self.blobber.radius = radius

    def set_num_augmentations(self, num_augmentations):
        self.num_augmentations = num_augmentations

    def set_detect_blobs(self, detect_blobs):
        self.detect_blobs = detect_blobs

    def set_ignore_vive_tracker_names(self, ignored_vive_tracker_names):
        self.decoder.add_ignored_vive_tracker_names(ignored_vive_tracker_names)

    def start(self):
        if self.running:
            logging.warning("Processor already running.")
            return False
        self.running = True
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        logging.info("Processor started.")
        return True
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        logging.info("Processor stopped.")


    def close(self):
        self.stop()
        logging.info("Processor closed.")

    
    def process(self):
        # get data
        data = self.callback_data()
        
        if data is None:
            return
        
        if not self.bypass:
            # to avoid freezing the UI we use a timeout on the queue get which can lead to None data
            
            # decode the data (find the trackers)
            self.decoder.decode(data)
            tracker_data = self.decoder.vive_trackers

            # augment the data
            tracker_data = self.augmentor.augment(tracker_data, self.num_augmentations)

            # detect the blobs
            if self.detect_blobs:
                blobs, tracker_data = self.blobber.process_data(tracker_data)
                self.encoder.blobs = blobs
                print("Blobs: ", blobs)

            # encode the data
            self.encoder.vive_trackers = tracker_data
            data = self.encoder.encode()

        # send the data out
        if self.callback:
            self.callback(data)


    def run(self):
        while self.running:
            self.process()
