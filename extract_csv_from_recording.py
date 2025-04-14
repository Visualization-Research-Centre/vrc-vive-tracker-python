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

    rec_path = "recordings/circle.bin"
    
    decoder = ViveDecoder()
    
    data = load_from_bin(rec_path)
    
    table = []
    for d in data:
        if d is None:
            continue
        timestamp = d[0]
        decoder.decode(d[1])
        trackers = decoder.vive_trackers
        if trackers is None or len(trackers) == 0:
            logging.warning("No trackers found in the decoded data.")
            continue
        
        # augment the data
        
        row = [timestamp]
        for tracker in trackers:
            if tracker["is_tracked"]:
                x = tracker["position"][0]
                y = tracker["position"][2]
                row.append(x)
                row.append(y)
        table.append(row)
        
        # write the data to csv
with open("recordings/circle.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    for row in table:
        writer.writerow(row)