import time
import struct

class ViveDecoder:
    def __init__(self):
        self.ignore_tracking_reference = True
        self.vive_trackers = []
        self.ignored_vive_tracker_names = []
        self.blobs = []
        self.label = 2222
        self.current_timestamp = 0
        
    def add_ignored_vive_tracker_name(self, vive_tracker_name):
        name = vive_tracker_name.lower()
        if name not in self._ignored_vive_tracker_names:
            self._ignored_vive_tracker_names.append(name)
    
    def decode_data(self, byte_data):
        if len(byte_data) <= 2:
            return

        label = int.from_bytes(byte_data[:2], 'little')
        if label != self.label:
            return

        # decode the trackers
        vr_tracker_devices_count = byte_data[2]
        vive_trackers = []
        index = 3

        if vr_tracker_devices_count > 0:
            self.current_timestamp = time.time()
            for _ in range(vr_tracker_devices_count):
                tracker_name = byte_data[index:index+8].decode('utf-8')
                device_class = byte_data[index + 8]
                battery = byte_data[index + 9] / 100.0
                status = byte_data[index + 10] == 1
                is_tracked = byte_data[index + 11] == 1

                position = [
                    struct.unpack('<f', byte_data[index + 12:index + 16])[0],
                    struct.unpack('<f', byte_data[index + 16:index + 20])[0],
                    struct.unpack('<f', byte_data[index + 20:index + 24])[0]
                ]
                rotation = [
                    struct.unpack('<f', byte_data[index + 24:index + 28])[0],
                    struct.unpack('<f', byte_data[index + 28:index + 32])[0],
                    struct.unpack('<f', byte_data[index + 32:index + 36])[0],
                    struct.unpack('<f', byte_data[index + 36:index + 40])[0]
                ]
                vr_tracker_device = {
                    'name': tracker_name,
                    'device_class': device_class,
                    'battery': battery,
                    'status': status,
                    'is_tracked': is_tracked,
                    'position': position,
                    'rotation': rotation
                }

                if device_class == 2:
                    vr_tracker_device['ul_button_pressed'] = int.from_bytes(byte_data[index + 40:index + 48], 'little')
                    vr_tracker_device['r_axis0'] = [
                        struct.unpack('<f', byte_data[index + 48:index + 52])[0],
                        struct.unpack('<f', byte_data[index + 52:index + 56])[0]
                    ]
                    vr_tracker_device['r_axis1'] = [
                        struct.unpack('<f', byte_data[index + 56:index + 60])[0],
                        struct.unpack('<f', byte_data[index + 60:index + 64])[0]
                    ]
                    vr_tracker_device['r_axis2'] = [
                        struct.unpack('<f', byte_data[index + 64:index + 68])[0],
                        struct.unpack('<f', byte_data[index + 68:index + 72])[0]
                    ]
                    vr_tracker_device['r_axis3'] = [
                        struct.unpack('<f', byte_data[index + 72:index + 76])[0],
                        struct.unpack('<f', byte_data[index + 76:index + 80])[0]
                    ]
                    vr_tracker_device['r_axis4'] = [
                        struct.unpack('<f', byte_data[index + 80:index + 84])[0],
                        struct.unpack('<f', byte_data[index + 84:index + 88])[0]
                    ]
                    index += 88
                else:
                    index += 40

                can_add_tracker_device = True
                if self.ignore_tracking_reference:
                    if (vr_tracker_device['name'].lower() in self.ignored_vive_tracker_names 
                        or vr_tracker_device['name'].upper() in self.ignored_vive_tracker_names 
                        or vr_tracker_device['device_class'] == 4):
                        can_add_tracker_device = False

                if can_add_tracker_device:
                    vive_trackers.append(vr_tracker_device)

        self.vive_trackers = vive_trackers

        # decode the blobs
        if index >= len(byte_data):
            return  # Prevent index out of range error
        blobs_count = byte_data[index]
        blobs = []
        index += 1

        if blobs_count > 0:
            for _ in range(blobs_count):
                blob_name = byte_data[index:index+8].decode('utf-8')
                position = [
                    struct.unpack('<f', byte_data[index + 8:index + 12])[0],
                    struct.unpack('<f', byte_data[index + 12:index + 16])[0]
                ]
                weight = struct.unpack('<f', byte_data[index + 16:index + 20])[0]
                blob = {
                    'name': blob_name,
                    'position': position,
                    'weight': weight
                }
                blobs.append(blob)
                index += 20

        self.blobs = blobs

        return self.vive_trackers, self.blobs