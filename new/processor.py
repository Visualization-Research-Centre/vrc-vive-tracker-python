
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


        def process(self):
            bin_data = self.callback_data()
            
            tracker_data = self.decoder.decode(bin_data)
                        
            if self.augment:
                tracker_data = self.augment(tracker_data)

            blobs = self.blobber.get_blobs(tracker_data)

            self.encoder.add_tracker_data(tracker_data)
            self.encoder.add_blobs(blobs)
            self.data = self.encoder.encode()

            if self.callback:
                self.callback(self.data)

            return self.data

            