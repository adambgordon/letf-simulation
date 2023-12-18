import json
import yaml
import numpy as np
import time
import pprint as pp
import csv

F_YR = ','
F_PCT = ',.4%'

YEAR_BUCKETS = [1, 3, 5, 10, 15, 20, 30]
PERCENTILES = [i for i in range(0, 101)]
ETF_NAMES = []
ALL_NAMES = []
BLENDS_INFO = {}

returns = {}
return_percentiles = {}

with open('files/config.yml', 'r') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    BLENDS_INFO = config['blends']

with open('files/annual_sim_data.json', 'r') as file:
    sim_data = json.load(file)
    ETF_NAMES = [*sim_data.keys()]
    ALL_NAMES = ETF_NAMES + [*BLENDS_INFO.keys()]

    returns = {etf: {bucket: [] for bucket in YEAR_BUCKETS} for etf in ETF_NAMES}
    return_percentiles = {name: {bucket: {} for bucket in YEAR_BUCKETS} for name in ALL_NAMES}

    for etf, returns_data in sim_data.items():
        returns[etf][1] = returns_data

def build_time_frame_results(bucket):
    index = bucket - 1
    slices = {}
    for etf in ETF_NAMES:
        slices[etf] = [0] + returns[etf][1][:index]
        validate_slice(slice=slices[etf], bucket=bucket)

    while (index < len(returns[ETF_NAMES[0]][1])):
        for etf in ETF_NAMES:
            slices[etf].pop(0)
            slices[etf].append(returns[etf][1][index])
            returns[etf][bucket].append(compound(slices[etf]))
        index += 1

def validate_slice(slice, bucket):
    if len(slice) != bucket:
        raise Exception('Slice is of length', len(slice), 'bucket is', bucket)

def compound(returns_list):
    compounded = 1
    for x in returns_list:
        compounded *= x
    return compounded

def build_percentiles():
    for etf in ETF_NAMES:
        for bucket in YEAR_BUCKETS:
            for pct in PERCENTILES:
                return_percentiles[etf][bucket][pct] = np.percentile(returns[etf][bucket], pct) - 1

def build_blends():
    for blend_name, blend in BLENDS_INFO.items():
        for bucket in YEAR_BUCKETS:
            for pct in PERCENTILES:
                composite = 0
                for etf, prop in blend.items():
                    composite += return_percentiles[etf][bucket][pct] * prop
                return_percentiles[blend_name][bucket][pct] = composite

def build_final_results():
    for bucket in YEAR_BUCKETS[1:]:
        build_time_frame_results(bucket)
    build_percentiles()
    build_blends()

start_time = time.time()
build_final_results()
end_time = time.time()
duration_compute = round(end_time - start_time, 2)

fields = ['etf', 'year_value', 'year_name', 'percentile', 'return']
with open('return_percentiles.csv', 'w') as f:
    w = csv.writer(f)
    w.writerow(fields)
    for name in return_percentiles:
        for year in YEAR_BUCKETS:
            for pct in PERCENTILES:
                ret = return_percentiles[name][year][pct]
                w.writerow([name, year, str(year)+'yr', pct, ret])

print(format(len(returns[ETF_NAMES[0]][1]), F_YR), 'years')
print(duration_compute, 's to compute')
