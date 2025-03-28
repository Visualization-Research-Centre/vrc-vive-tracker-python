
from vive_decoder import ViveDecoder
from vive_encoder import ViveEncoder
from vive_blobber import ViveBlobber
from vive_augmentor import ViveAugmentor

class Processor:

    def __init__(self, callback_data, callback=None):
        self.callback_data = callback_data
        self.callback = callback
        self.augment = False
        self.decoder = ViveDecoder()
        self.encoder = ViveEncoder()
        self.blobber = ViveBlobber()
        self.augmentor = ViveAugmentor()
        self.ignored_vive_tracker_names = ['2B9219E9', 'FD0C50D1'] # TODO double check the ignored devices


        def process(self):
            bin_data = self.callback_data()
            
            self.decoder.ignored_vive_tracker_names = self.ignored_vive_tracker_names
            tracker_data = self.decoder.decode(bin_data)
                        
            if self.augment:
                tracker_data = self.augment(tracker_data)

            blobs = self.blobber.get_blobs(tracker_data)

            self.encoder.vive_trackers = tracker_data
            self.encoder.blobs = blobs
            self.data = self.encoder.encode()

            if self.callback:
                self.callback(self.data)

            return self.data

            