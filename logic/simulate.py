import yaml
import json
import numpy as np
import time
import pprint as pp
import sys

with open('../files/config.yml', 'r') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

def ANNUAL_FEE_TO_DAILY_FEE_MULTIPLIER(fee):
    return (1 - fee)**(1/NUM_TRADING_DAYS)

def DAILY_FED_FUNDS_RATE_MULTIPLIER(leverage):
    return ANNUAL_FEE_TO_DAILY_FEE_MULTIPLIER(ANNUAL_FED_FUNDS_RATE*leverage)

NUM_TRADING_DAYS = 252
DAILY_RETURN = (1 + config['annual_return'])**(1/NUM_TRADING_DAYS) - 1
DAILY_STANDARD_DEVIATION = config['annual_standard_deviation'] / (NUM_TRADING_DAYS**0.5)
DAILY_EXPENSE_RATIO_MULTIPLIER = ANNUAL_FEE_TO_DAILY_FEE_MULTIPLIER(fee=config['annual_expense_ratio'])
ANNUAL_FED_FUNDS_RATE = config['annual_fed_funds_rate']
YEARS_TO_SIMULATE = config['years_to_simulate']
ETF_INFO = config['etfs']
ETF_NAMES = [*ETF_INFO.keys()]

results = {etf: [] for etf in ETF_NAMES}

annual_cum_returns = ETF_INFO.copy()

def build_annual_cum_returns():
    for etf in ETF_NAMES:
        cum = annual_cum_returns[etf]
        cum['leverage'] = cum['multiple'] - 1
        if cum['leverage'] == 0:
            cum['daily_fee_multiplier'] = 1
        else:
            cum['daily_fee_multiplier'] = DAILY_EXPENSE_RATIO_MULTIPLIER * DAILY_FED_FUNDS_RATE_MULTIPLIER(leverage=cum['leverage'])
        annual_cum_returns[etf] = cum

# Returns multiplier (e.g. 1.08) for 1 full year of returns
def simulate_year():
    for etf in ETF_NAMES:
        annual_cum_returns[etf]['return'] = 1

    for _ in range(NUM_TRADING_DAYS):
        random_generated_return = np.random.normal(loc=DAILY_RETURN, scale=DAILY_STANDARD_DEVIATION)
        for etf in ETF_NAMES:
            cum = annual_cum_returns[etf]
            cum['return'] *= (1 + random_generated_return*cum['multiple']) * cum['daily_fee_multiplier']
            annual_cum_returns[etf] = cum

build_annual_cum_returns()

def run(years):
    dot_bucket = int(years/76)
    start_time = time.time()

    print()
    for y in range(years):
        simulate_year()
        for etf in ETF_NAMES:
            results[etf].append(annual_cum_returns[etf]['return'])
        
        dot_count = y/dot_bucket
        print("{:.0%}".format(y/years) + "."*int(dot_count))
        print("Simulating {:,} years".format(y+1))
        print("{:.2f} seconds".format(time.time() - start_time))
        sys.stdout.write("\033[F"*3)  # \033[F resets 'cursor' to begging of line (x3)

    print("100%"+"."*76+"\033[K")  # \033[K clears remainder of line
    print("Simulated {:,} years\033[K".format(y+1))
    print("{:.2f} seconds\033[K".format(time.time() - start_time))

run(YEARS_TO_SIMULATE)

with open('../results/annual_sim_data.json', 'w') as file:
    json.dump(results, file)
