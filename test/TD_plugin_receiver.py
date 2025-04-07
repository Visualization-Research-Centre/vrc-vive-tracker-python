# me - this DAT
#
# dat - the DAT that received the data
# rowIndex - is the row number the data was placed into
# message - an ascii representation of the data
#           Unprintable characters and unicode characters will
#           not be preserved. Use the 'byteData' parameter to get
#           the raw bytes that were sent.
# byteData - a byte array of the data received
# peer - a Peer object describing the originating message
#   peer.close()    #close the connection
#   peer.owner  #the operator to whom the peer belongs
#   peer.address    #network address associated with the peer
#   peer.port       #network port associated with the peer
#

import math
import time
import struct
from threading import Lock 


def onReceive(dat, rowIndex, message, byteData, peer):
    # print(f"Received byteData: {byteData}")

    # Decode the byteData
    tracker_decoder = ViveDecoder()
    tracker_decoder.decode(byteData)
    # print(f"Tracker Devices: {tracker_decoder.vr_tracker_devices}")

    operator = op('trackers')
    operator.clear()
    ## operator.appendRow(['deviceid', 'x', 'y', 'z', 'rx', 'ry', 'rz', 'qx', 'qy', 'qz', 'qw'])
    operator.appendRow(['deviceid', 'x', 'y', 'z', 'qx', 'qy', 'qz', 'qw', 'tracked', 'blobID'])

    
    operator2 = op('blobs')
    operator2.clear()
    operator2.appendRow(['blobID', 'x', 'y', 'w'])

    # print the data into a table DAT: deviceid, position, rotation
    for device in tracker_decoder.vive_trackers:        
        # get position vector
        pos = device['position']

        # convert quaternion to euler angles
        q = device['rotation']
        # angles = quaternion_to_euler(q)
        
        blob_id = device.get('blob_id')
        
        is_tracked = device['is_tracked']
        
        # print the data into a table DAT
        # operator.appendRow([device['name'], pos[0], pos[1], pos[2], angles[0], angles[1], angles[2], q[0], q[1], q[2], q[3]])
        operator.appendRow([device['name'], pos[0], pos[1], pos[2], q[0], q[1], q[2], q[3], is_tracked, blob_id])

    for i, blob in enumerate(tracker_decoder.blobs):
        pos = blob['position']
        weight = blob['weight']
        
        operator2.appendRow([i, pos[0], pos[1], weight])

    return

def quaternion_to_euler(quaternion):
    x = quaternion[0]
    y = quaternion[1]
    z = quaternion[2]
    w = quaternion[3]

    # roll (x-axis rotation)
    sinr_cosp = 2 * (w * x + y * z)
    cosr_cosp = 1 - 2 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # pitch (y-axis rotation)
    sinp = 2 * (w * y - z * x)
    if math.fabs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)
    else:
        pitch = math.asin(sinp)

    # yaw (z-axis rotation)
    siny_cosp = 2 * (w * z + x * y)
    cosy_cosp = 1 - 2 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    angles = [math.degrees(roll), math.degrees(pitch), math.degrees(yaw)]

    return angles

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
        
    def set_ignored_vive_tracker_names(self, vive_tracker_names):
        self.ignored_vive_tracker_names = []
        for tracker_name in vive_tracker_names:
            name = tracker_name.lower()
            self.ignored_vive_tracker_names.append(name)
    
    def decode(self, byte_data):
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

                ## TODO device class 2 not tested
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

        # ====================================================================================
        # decode the blobs
        if index >= len(byte_data):
            return self.vive_trackers, None
        
        # change battery to blobs_id for each tracker
        for tracker in self.vive_trackers:
            tracker['blob_id'] = int(tracker['battery'] * 100)
            # remove battery
            tracker.pop('battery')

        blobs_count = byte_data[index]
        blobs = []
        index += 1

        if blobs_count > 0:
            for _ in range(blobs_count):
                position = [
                    struct.unpack('<f', byte_data[index:index + 4])[0],
                    struct.unpack('<f', byte_data[index + 4:index + 8])[0]
                ]
                weight = struct.unpack('<f', byte_data[index + 8:index + 12])[0]
                blob = {
                    'position': position,
                    'weight': weight
                }
                blobs.append(blob)
                index += 12

        self.blobs = blobs

        return self.vive_trackers, self.blobs