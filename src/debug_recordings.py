import os
import struct
import logging

from src.decoder import Decoder


class Debugger:
    def __init__(self, binary_filepath, ignore_tracker_list, epsilon=1e-6, detect_jittering=True, detect_zero_position=True):
        self.binary_filepath = binary_filepath
        self.ignore_tracker_list = ignore_tracker_list
        self.epsilon = epsilon
        self.detect_jittering = detect_jittering
        self.detect_zero_position = detect_zero_position

        logging.basicConfig(level=logging.INFO)

        if not os.path.exists(self.binary_filepath):
            logging.error(
                f"Recording file not found: {self.binary_filepath}")

    def is_jittering(self, x0, y0, x1, y1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        # Check if the change in position is significant
        if self.is_zero_position(dx, dy):
            return False
        # if dx and dy are zero (with a small epsilon), we consider it as no jitter
        if dx <= self.epsilon and dy <= self.epsilon:
            return False

        return True

    def is_zero_position(self, x, y):
        return abs(x) <= self.epsilon and abs(y) <= self.epsilon

    def debug_binary_file(self):
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

        decoder = Decoder()
        decoder.set_ignored_tracker_names(self.ignore_tracker_list)

        data = load_from_bin(self.binary_filepath)

        table = []
        zero_position_stats = {}  # {tracker_name: [(timestamp, x, y), ...]}
        freezer_stats = {}  # {tracker_name: [(timestamp, x, y), ...]}

        for d in data:
            if d is None:
                return
            timestamp = d[0]
            decoder.decode(d[1])
            trackers = decoder.trackers
            if trackers is None or len(trackers) == 0:
                logging.warning(
                    "No trackers found in the decoded data.")
                return

            row = [timestamp]
            old_x = old_y = None
            for tracker in trackers:
                x = tracker["position"][0]
                y = tracker["position"][2]

                if self.detect_jittering and old_x is not None and old_y is not None:
                    if not self.is_jittering(old_x, old_y, x, y):
                        logging.warning(
                            f"Frozen tracker {tracker['name']} at timestamp {timestamp}: "
                            f"old position ({old_x}, {old_y}), new position ({x}, {y})"
                        )
                        if tracker["name"] not in freezer_stats:
                            freezer_stats[tracker["name"]] = []
                        freezer_stats[tracker["name"]].append(
                            (timestamp, old_x, old_y, x, y))
                old_x = x
                old_y = y

                if self.detect_zero_position and self.is_zero_position(x, y):
                    logging.warning(
                        f"\nAt timestamp {timestamp}, tracker {tracker['name']} has zero position: x={x}, y={y}."
                    )
                    if tracker["name"] not in zero_position_stats:
                        zero_position_stats[tracker["name"]] = []
                    zero_position_stats[tracker["name"]].append(
                        (timestamp, x, y))

                row.append(x)
                row.append(y)
            table.append(row)

        # Print statistics at the end
        if zero_position_stats:
            logging.info("\n=== Zero Position Statistics ===")
            for tracker_name, events in zero_position_stats.items():
                logging.info(f"Tracker {tracker_name}:")
                logging.info(f"  Total number of errors: {len(events)}")
                for timestamp, x, y in events:
                    logging.info(
                        f"  Zero position at timestamp {timestamp}: x={x}, y={y}")
                logging.info()
        if freezer_stats:
            logging.info("\n=== Freeze Statistics ===")
            for tracker_name, events in freezer_stats.items():
                logging.info(f"Tracker {tracker_name}:")
                logging.info(f"  Total number of errors: {len(events)}")
                for timestamp, old_x, old_y, x, y in events:
                    logging.info(
                        f"  Frozen at timestamp {timestamp}: old position ({old_x}, {old_y}), new position ({x}, {y})")
                logging.info()


if __name__ == "__main__":
    debugger = Debugger(
        binary_filepath="/Users/marlen/projects/hkbu-vive-tracker/recordings/ale_4ppl.bin",
        ignore_tracker_list=[]
    )
    debugger.debug_binary_file()
