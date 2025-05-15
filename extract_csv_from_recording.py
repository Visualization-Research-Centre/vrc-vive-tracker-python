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
            
def main(no_ppl, rec_path, ignore_list):
    # check if the path exists
    if not os.path.exists(rec_path):
        logging.error(f"Path does not exist: {rec_path}")
        return
    
    # path to the recordings for training
    train_path = os.path.join(rec_path, "train")

    # list of recordings
    train_recordings = [
        os.path.splitext(file)[0]
        for file in os.listdir(train_path)
        if file.endswith(".bin")
    ]

    # write train_recordings to a config file of form labels: train_recordings
    config_file = os.path.join(train_path, "train_set.txt")
    with open(config_file, "w") as f:
        f.write("labels:\n")
        for recording in train_recordings:
            f.write(f"{recording}\n")
    logging.info(f"Train recordings config file: {config_file}")
    
    # file to save the csv
    csv_file = os.path.join(train_path, "train_set.csv")

    with open(csv_file, "w", newline="") as csvfile:
        # Add a first row with the header 'form_type', 'x{i}, 'y{i}' for each tracker
        header = ["form_type"]
        for i in range(0, no_ppl):
            header.append(f"x{i}")
            header.append(f"y{i}")
        writer = csv.writer(csvfile)
        writer.writerow(header)

        for recording in train_recordings:
            recording_path = os.path.join(train_path, f"{recording}.bin")
            if not os.path.exists(recording_path):
                logging.error(f"Recording file not found: {recording_path}")
                continue

            decoder = ViveDecoder()
            decoder.set_ignored_vive_tracker_names(ignore_list)
            
            data = load_from_bin(recording_path)
            
            table = []
            for d in data:
                if d is None:
                    continue
                # timestamp = d[0]
                # label is the index of the recording
                label = train_recordings.index(recording)
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

if __name__ == "__main__":

    # change here
    # ============================================
    no_ppl = 20
    rec_path = "recordings"
    ignore_list = ['2B9219E9']
    # ============================================

    # set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("extract_csv_from_recording.log"),
            logging.StreamHandler()
        ]
    )
    
    main(no_ppl, rec_path, ignore_list)
