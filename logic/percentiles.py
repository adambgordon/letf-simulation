import csv
import json
import numpy as np
import yaml
from pathlib import Path
from helper import getAbsPath
from thread_timer import ElapsedTimeThread

class Builder:
    def __init__(self):
        self.PATH = getAbsPath()
        self.YEAR_BUCKETS = [1, 3, 5, 10, 15, 20, 30]
        self.PERCENTILES = [i for i in range(0, 101)]
        self.ETF_NAMES = []
        self.ALL_NAMES = []
        self.BLENDS_INFO = {}
        self.returns = {}
        self.return_percentiles = {}

        with open(Path(self.PATH, 'files', 'config.yml'), 'r') as file:
            config = yaml.safe_load(file)
            self.BLENDS_INFO = config['blends']

        with open(Path(self.PATH, 'results', 'annual_sim_data.json'), 'r') as file:
            sim_data = json.load(file)
            self.ETF_NAMES = list(sim_data.keys())
            self.ALL_NAMES = self.ETF_NAMES + list(self.BLENDS_INFO.keys())

            self.returns = {etf: {bucket: [] for bucket in self.YEAR_BUCKETS} for etf in self.ETF_NAMES}
            self.return_percentiles = {name: {bucket: {} for bucket in self.YEAR_BUCKETS} for name in self.ALL_NAMES}

            for etf, returns_data in sim_data.items():
                self.returns[etf][1] = returns_data

    def build_time_frame_results(self, bucket):
        index = bucket - 1
        slices = {}
        for etf in self.ETF_NAMES:
            slices[etf] = [0] + self.returns[etf][1][:index]
            self.validate_slice(slice=slices[etf], bucket=bucket)

        while index < len(self.returns[self.ETF_NAMES[0]][1]):
            for etf in self.ETF_NAMES:
                slices[etf].pop(0)
                slices[etf].append(self.returns[etf][1][index])
                self.returns[etf][bucket].append(self.compound(slices[etf]))
            index += 1

    @staticmethod
    def validate_slice(slice, bucket):
        if len(slice) != bucket:
            raise Exception('Slice is of length', len(slice), 'bucket is', bucket)

    @staticmethod
    def compound(returns_list):
        return np.prod([x for x in returns_list])

    def build_percentiles(self):
        for etf in self.ETF_NAMES:
            for bucket in self.YEAR_BUCKETS:
                for pct in self.PERCENTILES:
                    self.return_percentiles[etf][bucket][pct] = np.percentile(self.returns[etf][bucket], pct) - 1

    def build_blends(self):
        for blend_name, blend in self.BLENDS_INFO.items():
            for bucket in self.YEAR_BUCKETS:
                for pct in self.PERCENTILES:
                    composite = 0
                    for etf, prop in blend.items():
                        composite += self.return_percentiles[etf][bucket][pct] * prop
                    self.return_percentiles[blend_name][bucket][pct] = composite

    def build_final_results(self):
        for bucket in self.YEAR_BUCKETS[1:]:
            self.build_time_frame_results(bucket)
        self.build_percentiles()
        self.build_blends()

    def write_to_csv(self):
        fields = ['etf', 'year_value', 'year_name', 'percentile', 'return']
        with open(Path(self.PATH, 'results', 'return_percentiles.csv'), 'w') as f:
            w = csv.writer(f)
            w.writerow(fields)
            for name in self.return_percentiles:
                for year in self.YEAR_BUCKETS:
                    for pct in self.PERCENTILES:
                        ret = self.return_percentiles[name][year][pct]
                        w.writerow([name, year, str(year)+'yr', pct, ret])

def main():
    builder = Builder()
    builder.build_final_results()
    builder.write_to_csv()

if __name__ == "__main__":
    elapsed_thread = ElapsedTimeThread()
    elapsed_thread.start()

    main()

    elapsed_thread.stop()
    elapsed_thread.join()
