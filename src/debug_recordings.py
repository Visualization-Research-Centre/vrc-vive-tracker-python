import os
import struct
import logging

from vive_decoder import ViveDecoder


class Debugger:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

    def check_zero_x_y(self, x, y):
        epsilon = 1e-6
        if abs(x) <= epsilon and abs(y) <= epsilon:
            return True
        return False

    def generate_from_binary_directory(self, binary_filepath, ignore_tracker_list):
        def load_from_bin(file_path):
            rec = []
            if not os.path.exists(file_path):
                logging.error(f"File not found: {file_path}")
                return
            with open(file_path, "rb") as f:
                # Read the header
                first = f.read(4)
                if not first:
                    logging.error("File is empty or corrupted.")
                    return
                start_time = struct.unpack("<f", first)[0]
                length = struct.unpack("I", f.read(4))[0]
                if length != 0:
                    logging.warning(
                        "File might be old and recording time is wrong. Interpreting header as data...."
                    )
                    data = f.read(length)
                logging.info(f"Recording time: {start_time}")

                while True:
                    first = f.read(4)
                    if not first:
                        logging.info("End of file reached.")
                        break
                    if first == b"\x00":
                        logging.info("End of file reached.")
                        break
                    timestamp = struct.unpack("<f", first)[0]
                    length = struct.unpack("I", f.read(4))[0]
                    data = f.read(length)
                    rec.append((timestamp, data))
            return rec

        if not os.path.exists(binary_filepath):
            logging.error(
                f"Recording file not found: {binary_filepath}")
            return

        decoder = ViveDecoder()
        decoder.set_ignored_vive_tracker_names(ignore_tracker_list)

        data = load_from_bin(binary_filepath)

        table = []
        for d in data:
            if d is None:
                return
            timestamp = d[0]
            decoder.decode(d[1])
            trackers = decoder.vive_trackers
            if trackers is None or len(trackers) == 0:
                logging.warning(
                    "No trackers found in the decoded data.")
                return

            row = [timestamp]
            for tracker in trackers:
                if tracker["is_tracked"]:
                    x = tracker["position"][0]
                    y = tracker["position"][2]

                    x = 0.000001
                    y = 0.000001
                    if self.check_zero_x_y(x, y):
                        logging.error(
                            f"\nAt timestamp {timestamp}, tracker {tracker['name']} has zero position: x={x}, y={y}. Ignoring this tracker."
                        )
                        return

                    row.append(x)
                    row.append(y)
            table.append(row)
            print(f"\nDecoded data for timestamp {timestamp}: {row}")


if __name__ == "__main__":
    debugger = Debugger()
    binary_filepath = "/Users/marlen/projects/hkbu-vive-tracker/recordings/train/random.bin"
    ignore_tracker_list = []
    debugger.generate_from_binary_directory(
        binary_filepath, ignore_tracker_list)
