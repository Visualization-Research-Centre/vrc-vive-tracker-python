import threading
import logging
from src.decoder import Decoder
from src.encoder import Encoder
from src.blobber import Blobber
from src.augmentor import Augmentor
from src.classifier import Classifier

class Processor:

    def __init__(
        self,
        callback_data,
        callback=None,
        callback_vis=None,
        config=None,
    ):
        self.callback_data = callback_data
        self.callback = callback
        self.callback_vis = callback_vis
        self.num_augmentations = 1
        self.decoder = Decoder()
        self.encoder = Encoder()
        self.blobber = Blobber()
        self.augmentor = Augmentor()
        self.classifier = None # Classifier(config)
        self.thread = None
        self.running = False
        self.data = None
        self.bypass = False
        self.detect_blobs = True
        self.debug = False
        self.augment_data = True
    
    def set_radius(self, radius):
        self.blobber.radius = radius
    
    def set_num_augmentations(self, num_augmentations):
        self.num_augmentations = num_augmentations

    def set_augment_data(self, augment_data):
        self.augment_data = augment_data
        
    def set_ignore_tracker_names(self, ignored_tracker_names):
        self.decoder.set_ignored_tracker_names(ignored_tracker_names)

    def set_debug(self, debug):
        self.debug = debug
        
    def set_bypass(self, bypass):
        self.bypass = bypass
    
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
        logging.info("Processor stopped.")

    def close(self):
        self.stop()
        logging.info("Processor closed.")

    def process(self):
        # get data

        data = self.callback_data()

        if data is None:
            return

        if self.debug:
            logging.info(f"Got: {len(data)} bytes")

        if not self.bypass:
            # to avoid freezing the UI we use a timeout on the queue get which can lead to None data

            # decode the data (find the trackers)
            self.decoder.decode(data)
            tracker_data = self.decoder.trackers
            
            if tracker_data is None or len(tracker_data) == 0:
                logging.warning("No trackers found in the decoded data.")
                return None
            
            # augment the data
            if self.augment_data:
                tracker_data = self.augmentor.augment(
                    tracker_data, self.num_augmentations
                )

            if tracker_data is None:
                logging.warning("No devices found in the decoded data.")
                return None

            # detect the blobs
            blobs, tracker_data = self.blobber.process_data(tracker_data)
            self.encoder.blobs = blobs
            if self.debug and len(blobs) > 0:
                dbg_str = "Blobs:\n"
                for i, blob in enumerate(blobs):
                    dbg_str += f"\tID {i}:({blob[0]:.2f} "
                    dbg_str += f",{blob[1]:.2f} "
                    dbg_str += f",{blob[2]:.2f})\n"
                logging.info(dbg_str)

            if self.debug:
                dbg_str = "Trackers:\n"
                for tracker in tracker_data:
                    dbg_str += f"\t{tracker['name']} #{tracker['device_class']}: "
                    if tracker["is_tracked"]:
                        dbg_str += " o "
                    else:
                        dbg_str += " x "
                    if tracker["blob_id"] is not None:
                        dbg_str += f"blob: {tracker['blob_id']} "
                    dbg_str += f"\t({tracker['position'][0]:.2f} "
                    dbg_str += f",{tracker['position'][1]:.2f} "
                    dbg_str += f",{tracker['position'][2]:.2f})\n"
                logging.info(dbg_str)

            # encode the data
            self.encoder.trackers = tracker_data
            data = self.encoder.encode()
            
            # classify the data
            if self.classifier:
                    # preprocess the data
                    trackers = []
                    for tracker in tracker_data:
                        if tracker["is_tracked"]:
                            x = tracker["position"][0]
                            y = tracker["position"][2]
                            trackers.extend([x,y])
                    probs, label = self.classifier.predict(trackers)
                    logging.info(f"Class: {label} ({probs})")

            if self.callback_vis:
                self.callback_vis(blobs, tracker_data)
                
        if self.debug:
            logging.info(f"Sent: {len(data)} bytes\n")

        # send the data out
        if self.callback:
            self.callback(data)

    def run(self):
        while self.running:
            self.process()
