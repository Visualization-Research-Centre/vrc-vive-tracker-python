import logging
import os
import struct
import csv
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from src.vive_decoder import ViveDecoder
from src.sources import Player

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

class Analyser:
    """Base class for data analysis"""
    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        self.decoder = ViveDecoder()
        self.player = Player()
        

    def process_tracking_data(self):
        """Convert binary data to CSV and return device stats"""
        os.makedirs(self.output_dir, exist_ok=True)

        self.player.load(self.input_file)
    
        records = self.player.data
        
        if not records:
            logging.error("No data processed. Exiting.")
            return None

        self.device_stats = {}
        self.all_data = {}

        # Process each data chunk
        for timestamp, binary_chunk in records:
            self.decoder.decode(binary_chunk)
            for tracker in self.decoder.vive_trackers:
                name = tracker["name"]
                
                # Initialize tracker storage
                if name not in self.all_data:
                    self.all_data[name] = []
                    self.device_stats[name] = {
                        'total': 0,
                        'errors': 0,
                        'positions': []
                    }
                
                # Record tracking status
                self.device_stats[name]['total'] += 1
                if tracker["tracking_result"] != 2:  # 2 = good tracking
                    self.device_stats[name]['errors'] += 1

                # Store position and tracking result for visualization
                self.device_stats[name]['positions'].append((
                    timestamp,
                    tracker["position"][0],
                    tracker["position"][2],  # Using X and Z for 2D plot
                    tracker["tracking_result"]
                ))
                
                # Prepare CSV data
                self.all_data[name].append([
                    timestamp,
                    *tracker["position"],  # x, y, z
                    *tracker["rotation"],  # qx, qy, qz, qw
                    tracker["status"],
                    tracker["is_tracked"],
                    tracker["tracking_result"]
                ])

        # Write CSV files
        for name, records in self.all_data.items():
            csv_path = os.path.join(self.output_dir, f"{name}.csv")
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "x", "y", "z", 
                    "qx", "qy", "qz", "qw",
                    "status", "tracked", "tracking_result"
                ])
                writer.writerows(records)
            logging.info(f"Created tracker data: {csv_path}")
        logging.info("Data processing complete.")

    def visualize_results(self):
        """Generate visualizations from processed data"""
        if not self.device_stats:
            logging.error("No data available for visualization")
            return
            
        plt.figure(figsize=(15, 10))
        plt.suptitle("Vive Tracker Data Visualization", fontsize=16)

        # Create subplot grid
        ax1 = plt.subplot(2, 1, 1)  # Trajectory plot
        ax2 = plt.subplot(2, 1, 2)  # Error analysis
        
        # Plot device trajectories
        logging.info("Generating trajectory plot...")
        for device, data in self.device_stats.items():
            if not data['positions']:
                continue
                
            # Extract positions and tracking status
            positions = np.array(data['positions'])
            timestamps = positions[:, 0]
            xs = positions[:, 1]
            zs = positions[:, 2]
            status = positions[:, 3]
            
            # Plot trajectory
            ax1.scatter(xs, zs, s=2, label=device)
            ax1.plot(xs, zs, alpha=0.3)
            
            # Mark positions with tracking issues
            error_mask = status != 2
            if np.any(error_mask):
                ax1.scatter(
                    xs[error_mask], 
                    zs[error_mask], 
                    s=20, 
                    c='red', 
                    marker='x',
                    alpha=0.7
                )
            
        ax1.set_title("Device Trajectories (X-Z Plane)")
        ax1.set_xlabel("X Position")
        ax1.set_ylabel("Z Position")
        ax1.legend()
        ax1.grid(True)
        
        # Calculate and plot error rates over time
        logging.info("Analyzing error rates over time...")
        min_time = float('inf')
        max_time = float('-inf')
        
        # Find global time range
        for data in self.device_stats.values():
            if data['positions']:
                positions = np.array(data['positions'])
                min_time = min(min_time, np.min(positions[:, 0]))
                max_time = max(max_time, np.max(positions[:, 0]))
        
        # Set time window to a tenth of the full time range
        if max_time > min_time:
            time_window = (max_time - min_time) / 10
        else:
            time_window = 1  # fallback to 1s if time range is zero
        
        # Create time bins
        bins = np.arange(min_time, max_time + time_window, time_window)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        # Plot error rates for each device
        for device, data in self.device_stats.items():
            if not data['positions']:
                continue
                
            positions = np.array(data['positions'])
            timestamps = positions[:, 0]
            status = positions[:, 3]
            
            # Calculate error rate per time window
            bin_errors = []
            for i in range(len(bins) - 1):
                in_bin = (timestamps >= bins[i]) & (timestamps < bins[i+1])
                if np.any(in_bin):
                    bin_status = status[in_bin]
                    error_rate = np.sum(bin_status != 2) / len(bin_status)
                    bin_errors.append(error_rate)
                else:
                    bin_errors.append(0)
            
            ax2.plot(bin_centers, bin_errors, label=device, marker='o', markersize=3)
        
        ax2.set_title(f"Error Rates Over Time ({time_window}s Windows)")
        ax2.set_xlabel("Time (s)")
        ax2.set_ylabel("Error Rate")
        ax2.grid(True)
        ax2.legend()
        
        # Finalize and save
        plt.tight_layout()
        plot_path = os.path.join(self.output_dir, "tracking_analysis.png")
        plt.savefig(plot_path)
        plt.show()
        logging.info(f"Visualization saved: {plot_path}")
        
        # Print device rankings
        print("\n=== Device Error Rankings ===")
        rankings = []
        for device, data in self.device_stats.items():
            if data['total'] > 0:
                error_rate = data['errors'] / data['total']
                rankings.append((device, error_rate))
        
        for device, rate in sorted(rankings, key=lambda x: x[1], reverse=True):
            print(f"{device}: {rate:.2%} error rate")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vive Tracker Analysis & Visualization")
    parser.add_argument("--input", required=True, help="Input binary file path")
    parser.add_argument("--output", default="analysis_results", help="Output directory")
    parser.add_argument("--ignore", nargs="*", default=[], help="Trackers to exclude")
    parser.add_argument("--window", type=int, default=10, help="Time window for analysis (seconds)")
    
    args = parser.parse_args()
    
    analyser = Analyser(args.input, args.output)
    analyser.process_tracking_data()
    analyser.visualize_results(time_window=args.window)