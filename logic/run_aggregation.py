import csv
import json
import numpy as np
import yaml
from pathlib import Path
from helper import getAbsPath
from thread_timer import ElapsedTimeThread

class Data:
    """A class to represent the data for simulation."""

    def __init__(self):
        """Initialize the data from the config file."""
        # Get the absolute path
        self.PATH = getAbsPath()
        # Define constants
        self.YEAR_BUCKETS = [1, 3, 5, 10, 15, 20, 30]
        self.PERCENTILES = [i for i in range(0, 101)]
        self.ETF_NAMES = []
        self.ALL_NAMES = []
        self.BLENDS_INFO = {}
        self.returns = {}
        self.return_percentiles = {}

        # Load the configuration file
        with open(Path(self.PATH, 'files', 'config.yml'), 'r') as file:
            data = yaml.safe_load(file)
            self.BLENDS_INFO = data['blends']

        # Load the simulation data
        with open(Path(self.PATH, 'results', 'annual_sim_data.json'), 'r') as file:
            sim_data = json.load(file)
            self.ETF_NAMES = list(sim_data.keys())
            self.ALL_NAMES = self.ETF_NAMES + list(self.BLENDS_INFO.keys())

            # Initialize returns and return percentiles
            self.returns = {etf: {bucket: [] for bucket in self.YEAR_BUCKETS} for etf in self.ETF_NAMES}
            self.return_percentiles = {name: {bucket: {} for bucket in self.YEAR_BUCKETS} for name in self.ALL_NAMES}

            # Load the returns data
            for etf, returns_data in sim_data.items():
                self.returns[etf][1] = returns_data

def build_time_frame_results(data, bucket):
    """Build time frame results for each ETF."""
    index = bucket - 1
    slices = {}
    for etf in data.ETF_NAMES:
        slices[etf] = [0] + data.returns[etf][1][:index]
        validate_slice(slice=slices[etf], bucket=bucket)

    # Calculate returns for each time frame
    while index < len(data.returns[data.ETF_NAMES[0]][1]):
        for etf in data.ETF_NAMES:
            slices[etf].pop(0)
            slices[etf].append(data.returns[etf][1][index])
            data.returns[etf][bucket].append(compound(slices[etf]))
        index += 1

def validate_slice(slice, bucket):
    """Validate the length of the slice."""
    if len(slice) != bucket:
        raise Exception('Slice is of length', len(slice), 'bucket is', bucket)

def compound(returns_list):
    """Calculate the product of the returns."""
    return np.prod([x for x in returns_list])

def build_percentiles(data):
    """Build percentiles for each ETF."""
    for etf in data.ETF_NAMES:
        for bucket in data.YEAR_BUCKETS:
            for pct in data.PERCENTILES:
                data.return_percentiles[etf][bucket][pct] = np.percentile(data.returns[etf][bucket], pct) - 1

def build_blends(data):
    """Build blends for each ETF."""
    for blend_name, blend in data.BLENDS_INFO.items():
        for bucket in data.YEAR_BUCKETS:
            for pct in data.PERCENTILES:
                composite = 0
                for etf, prop in blend.items():
                    composite += data.return_percentiles[etf][bucket][pct] * prop
                data.return_percentiles[blend_name][bucket][pct] = composite

def build_final_results(data):
    """Build final results for each ETF."""
    for bucket in data.YEAR_BUCKETS[1:]:
        build_time_frame_results(data, bucket)
    build_percentiles(data)
    build_blends(data)

def write_results_to_csv(data):
    """
    Write the results to a CSV file.
    """
    fields = ['etf', 'year_value', 'year_name', 'percentile', 'return']
    with open(Path(data.PATH, 'results', 'return_percentiles.csv'), 'w') as f:
        w = csv.writer(f)
        w.writerow(fields)
        for name in data.return_percentiles:
            for year in data.YEAR_BUCKETS:
                for pct in data.PERCENTILES:
                    ret = data.return_percentiles[name][year][pct]
                    w.writerow([name, year, str(year)+'yr', pct, ret])

def main():
    """Main function."""
    data = Data()
    build_final_results(data)
    write_results_to_csv(data)

if __name__ == "__main__":
    # Start the elapsed time thread
    elapsed_thread = ElapsedTimeThread()
    elapsed_thread.start()

    main()

    # Stop the elapsed time thread
    elapsed_thread.stop()
    elapsed_thread.join()
