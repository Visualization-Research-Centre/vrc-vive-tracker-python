import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

def analyze_device_data(folder_path, time_window=300):
    """
    Analyzes CSV files in a folder to identify device tracking issues.

    Args:
        folder_path (str): The path to the folder containing the CSV files.
    """

    all_device_data = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            filepath = os.path.join(folder_path, filename)
            try:
                df = pd.read_csv(filepath)
                device_name = filename[:-4]  # Extract device name from filename
                all_device_data[device_name] = df
            except Exception as e:
                print(f"Error reading or processing {filename}: {e}")

    if not all_device_data:
        print("No CSV files found or processed successfully.")
        return
    
    
    device_error_rates = {}  # Store overall error rates for each device

    # Analyze and visualize data for each device
    for device_name, df in all_device_data.items():
        if not all(col in df.columns for col in ['timestamp', 'tracking_result']):
            print(f"Skipping {device_name} due to missing required columns.")
            continue

        
        # Calculate overall error rate for the device
        overall_error_rate = (df['tracking_result'][df['tracking_result'] != 2].count() / df['tracking_result'].count()) if df['tracking_result'].count() > 0 else 0
        device_error_rates[device_name] = overall_error_rate


        # Calculate time spent in each tracking state
        total_time = df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]
        time_in_states = df['tracking_result'].value_counts(normalize=True) * total_time

        df['time_group'] = pd.cut(df['timestamp'], bins=np.arange(df['timestamp'].min(), df['timestamp'].max() + time_window, time_window), right=False)

        # Suppress the warning by explicitly setting observed=False
        error_rates = df.groupby('time_group', observed=False)['tracking_result'].apply(lambda x: (x[x != 2].count() / x.count()) if x.count() > 0 else 0)

        # Plotting (now plotting on the same figure)
        plt.plot(error_rates.index.astype(str), error_rates.values, label=device_name)

        

    plt.xlabel("Time Window")
    plt.ylabel("Error Rate")
    plt.title(f"Error Rates over Time (Window = {time_window}s)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.legend()  # Add a legend to distinguish devices
    plt.savefig("combined_error_rate_plot.png")
    plt.show()

    # Sort devices by error rate (highest first)
    sorted_devices = sorted(device_error_rates.items(), key=lambda item: item[1], reverse=True)

    # Textual output (ranked by overall error rate)
    print("\n--- Overall Error Rates (Ranked) ---")
    for device_name, error_rate in sorted_devices:
        print(f"- {device_name}: {error_rate:.2%}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Analyze device tracking data from CSV files.")
    parser.add_argument("--folder_path", type=str, help="Path to the folder containing CSV files.", default="analysis")
    parser.add_argument("--time_window", type=int, default=10, help="Time window in seconds for resampling data (default: 300s).")
    args = parser.parse_args()
    analyze_device_data(args.folder_path, args.time_window)