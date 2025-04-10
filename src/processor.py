import threading
import logging
from src.vive_decoder import ViveDecoder
from src.vive_encoder import ViveEncoder
from src.vive_blobber import ViveBlobber
from src.vive_augmentor import ViveAugmentor
from src.vive_visualizer import ViveVisualizer


class Processor:

    def __init__(
        self,
        callback_data,
        callback=None,
        bypass=False,
        debug=False,
        canvas=None,
    ):
        self.callback_data = callback_data
        self.callback = callback
        self.radius = 1
        self.num_augmentations = 1
        self.decoder = ViveDecoder()
        self.encoder = ViveEncoder()
        self.blobber = ViveBlobber(self.radius)
        self.augmentor = ViveAugmentor()
        self.visualizer = ViveVisualizer(canvas)
        self.thread = None
        self.running = False
        self.data = None
        self.bypass = bypass
        self.detect_blobs = True
        self.debug = debug
        self.augment_data = True
        self.visualize = True

    def set_radius(self, radius):
        self.blobber.radius = radius
        self.radius = radius

    def set_num_augmentations(self, num_augmentations):
        self.num_augmentations = num_augmentations

    def set_augment_data(self, augment_data):
        self.augment_data = augment_data

    def set_detect_blobs(self, detect_blobs):
        self.detect_blobs = detect_blobs

    def set_ignore_vive_tracker_names(self, ignored_vive_tracker_names):
        self.decoder.set_ignored_vive_tracker_names(ignored_vive_tracker_names)

    def set_debug(self, debug):
        self.debug = debug
        
    def set_visualize(self, vis):
        self.visualize = vis
        

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
        # if self.thread:
        #     self.thread.join()
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
            tracker_data = self.decoder.vive_trackers

            # augment the data
            if self.augment_data:
                tracker_data = self.augmentor.augment(
                    tracker_data, self.num_augmentations
                )

            if tracker_data is None:
                logging.warning("No devices found in the decoded data.")
                return None

            # detect the blobs
            if self.detect_blobs:
                blobs, tracker_data = self.blobber.process_data(tracker_data)
                self.encoder.blobs = blobs
                if self.debug:
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
            self.encoder.vive_trackers = tracker_data
            data = self.encoder.encode()

            if self.visualize:
                self.visualizer.update_canvas(blobs, tracker_data, radius=self.radius)

        if self.debug:
            logging.info(f"Sent: {len(data)} bytes\n")

        # send the data out
        if self.callback:
            self.callback(data)

    def run(self):
        while self.running:
            self.process()
