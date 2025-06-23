import os
import struct
import logging

from vive_decoder import ViveDecoder


class Debugger:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

    def is_zero_position(self, x, y):
        epsilon = 1e-6
        return abs(x) <= epsilon and abs(y) <= epsilon

    def debug_binary_file(self, binary_filepath, ignore_tracker_list):
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
        zero_position_stats = {}  # {tracker_name: [(timestamp, x, y), ...]}

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

                    if self.is_zero_position(x, y):
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


if __name__ == "__main__":
    debugger = Debugger()
    binary_filepath = "/Users/marlen/projects/hkbu-vive-tracker/recordings/ale_4ppl.bin"
    ignore_tracker_list = []
    debugger.debug_binary_file(
        binary_filepath, ignore_tracker_list)
