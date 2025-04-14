import logging
import os
import struct

from src.vive_decoder import ViveDecoder
import csv


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
            

if __name__ == "__main__":

    # number of ppl
    no_ppl = 7
    recordings = ['circle', 'line', 'random', 'square', 'triangle', 'cross']
    rec_path = "recordings"
    
    with open("recordings/formations.csv", "w", newline="") as csvfile:
        # Add a first row with the header 'form_type', 'x{i}, 'y{i}' for each tracker
        header = ["form_type"]
        for i in range(0, no_ppl):
            header.append(f"x{i}")
            header.append(f"y{i}")
        writer = csv.writer(csvfile)
        writer.writerow(header)
        print(f"Header: {header}")

        for recording in recordings:
            recording_path = os.path.join(rec_path, f"{recording}.bin")
            if not os.path.exists(recording_path):
                logging.error(f"Recording file not found: {recording_path}")
                continue

            decoder = ViveDecoder()
            
            data = load_from_bin(recording_path)
            
            table = []
            for d in data:
                if d is None:
                    continue
                # timestamp = d[0]
                # label is the index of the recording
                label = recordings.index(recording)
                print(f"Processing recording: {recording}, label: {label}")
                decoder.decode(d[1])
                trackers = decoder.vive_trackers
                if trackers is None or len(trackers) == 0:
                    logging.warning("No trackers found in the decoded data.")
                    continue
                
                # augment the data
                
                # row = [timestamp]
                row = [label]
                for tracker in trackers:
                    if tracker["is_tracked"]:
                        x = tracker["position"][0]
                        y = tracker["position"][2]
                        row.append(x)
                        row.append(y)
                table.append(row)
                
                # write the data to csv
                writer = csv.writer(csvfile)
                for row in table:
                    writer.writerow(row)