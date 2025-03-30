import struct

class ViveEncoder:
    def __init__(self):
        self.vive_trackers = []
        self.blobs = []
        self.label = 2222

    def encode(self):
        # Create byte data
        byte_data = bytearray()

        # Add label (2 bytes, little-endian)
        byte_data.extend(struct.pack('<H', self.label))

        # Add number of devices (1 byte)
        byte_data.extend(struct.pack('<B', len(self.vive_trackers)))

        # Add device data
        for device in self.vive_trackers:
            # Encode name (as bytes, followed by a null terminator for safety)
            byte_data.extend(device['name'].encode('utf-8'))

            # Encode device class (1 byte)
            byte_data.extend(struct.pack('<B', device['device_class']))

            if self.blobs:
                # Encode blob_id (1 byte, integer ranging from 0 to 10)
                byte_data.extend(struct.pack('<B', int(device['blob_id'])))
            else:
                # Encode battery percentage (1 byte, scaled to 0-100)
                byte_data.extend(struct.pack('<B', int(device['battery'] * 100)))

            # Encode status and tracking flags (1 byte each)
            byte_data.extend(struct.pack('<B', 1 if device['status'] else 0))
            byte_data.extend(struct.pack('<B', 1 if device['is_tracked'] else 0))

            # Encode position (3 floats, 4 bytes each)
            for pos in device['position']:
                byte_data.extend(struct.pack('<f', pos))

            # Encode rotation (4 floats, 4 bytes each)
            for rot in device['rotation']:
                byte_data.extend(struct.pack('<f', rot))

            ## TODO device class 2 not tested
            # # Encode additional data for device class 2
            # if device['device_class'] == 2:
            #     # Encode button pressed (8 bytes)
            #     byte_data.extend(struct.pack('<Q', device['ul_button_pressed']))

            #     # Encode axes data (5 axes, each with 2 floats)
            #     for axis in range(5):
            #         byte_data.extend(struct.pack('<ff', *device[f'r_axis{axis}']))

        # check if blobs are present
        if self.blobs:
            # Add number of blobs (1 byte)
            byte_data.extend(struct.pack('<B', len(self.blobs)))

            # Add blob data
            for blob in self.blobs:
                # Encode position (2 floats, 4 bytes each)
                for pos in blob[0]:
                    byte_data.extend(struct.pack('<f', pos))

                # Encode weight (1 float, 4 bytes)
                byte_data.extend(struct.pack('<f', blob[1]))

        return bytes(byte_data)