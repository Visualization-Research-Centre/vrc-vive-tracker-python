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
    
    decoder = ViveDecoder()
    decoder.set_ignored_vive_tracker_names(ignore_list)
    
    data = load_from_bin(rec_path)
    
    table = {}
    for d in data:
        if d is None:
            continue
        timestamp = d[0]
        # label is the index of the recording
        decoder.decode(d[1])
        trackers = decoder.vive_trackers
        if trackers is None or len(trackers) == 0:
            logging.warning("No trackers found in the decoded data.")
            continue
        
        for tracker in trackers:
            # if tracker["status"] != 3:
            #     logging.warning(f"Tracker {tracker['name']}: Status: {tracker['status']}")
            #     logging.warning(f"Tracker timestamp: {timestamp}")
            if tracker["is_tracked"] == False:
                logging.warning(f"Tracker {tracker['name']} is not tracked.")
                
            if tracker["name"] not in table:
                # Initialize the tracker in the table if not already present
                table[tracker["name"]] = []
            else:
                table[tracker["name"]].append([
                    timestamp,
                    tracker["position"][0],
                    tracker["position"][2],
                    tracker["position"][1],
                    tracker["rotation"][0],
                    tracker["rotation"][1],
                    tracker["rotation"][2],
                    tracker["rotation"][3],
                    tracker["status"],
                    tracker["is_tracked"],
                    tracker["tracking_result"]
                ])
            
                
            # print(f"Tracker {tracker}")
        
        # row = []
        # for tracker in trackers:
        #     x = tracker["position"][0]
        #     y = tracker["position"][2]
        #     row.append(x)
        #     row.append(y)
        # table.append(row)
        
        # write the data to csv
        # writer = csv.writer(csvfile)
        # for row in table:
        #     writer.writerow(row)
            
            

    # Add a first row with the header 'form_type', 'x{i}, 'y{i}' for each tracker
    # header = ["form_type"]
    for tracker_name in table.keys():
        header = []
        csv_file = os.path.join(f"{tracker_name}.csv")
        with open(csv_file, "w", newline="") as csvfile:
            header.append("timestamp")
            header.append(f"x")
            header.append(f"y")
            header.append(f"z")
            header.append(f"qx")
            header.append(f"qy")
            header.append(f"qz")
            header.append(f"qw")
            header.append(f"status")
            header.append(f"tracked")
            header.append(f"tracking_result")
            writer = csv.writer(csvfile)
            writer.writerow(header)
            for row in table[tracker_name]:
                writer.writerow(row)
        logging.info(f"CSV file created: {csv_file}")

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Extract CSV from Vive recording.")
    parser.add_argument(
        "--path",
        type=str,
        default="recordings",
        help="Path to the recordings directory.",
    )
    
    args = parser.parse_args()

    # change here
    # ============================================
    no_ppl = 1
    rec_path = "recordings"
    ignore_list = ['']
    # ============================================

    # set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )
    logging.info("Starting to extract csv from recording...")
    main(no_ppl, args.path, ignore_list)
    logging.info("Finished extracting csv from recording.")