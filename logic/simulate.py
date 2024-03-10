import yaml
import json
import numpy as np
import time
import sys
from helper import *

PATH = getAbsPath()

class Config:
    def __init__(self, path):
        with open(path, 'r') as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)
        self.num_trading_days = 252
        self.daily_return = (1 + self.config['annual_return'])**(1/self.num_trading_days) - 1
        self.daily_standard_deviation = self.config['annual_standard_deviation'] / (self.num_trading_days**0.5)
        self.daily_expense_ratio_multiplier = self.annual_fee_to_daily_fee_multiplier(fee=self.config['annual_expense_ratio'])
        self.annual_fed_funds_rate = self.config['annual_fed_funds_rate']
        self.years_to_simulate = self.config['years_to_simulate']
        self.etf_info = self.config['etfs']
        self.etf_names = [*self.etf_info.keys()]

    def annual_fee_to_daily_fee_multiplier(self, fee):
        return (1 - fee)**(1/self.num_trading_days)

    def daily_fed_funds_rate_multiplier(self, leverage):
        return self.annual_fee_to_daily_fee_multiplier(self.annual_fed_funds_rate*leverage)
    
config = Config(getAbsPath()+'/files/config.yml')

results = {etf: [] for etf in config.etf_names}

annual_cum_returns = config.etf_info.copy()

def build_annual_cum_returns():
    for etf in config.etf_names:
        cum = annual_cum_returns[etf]
        cum['leverage'] = cum['multiple'] - 1
        if cum['leverage'] == 0:
            cum['daily_fee_multiplier'] = 1
        else:
            cum['daily_fee_multiplier'] = config.daily_expense_ratio_multiplier * config.daily_fed_funds_rate_multiplier(leverage=cum['leverage'])
        annual_cum_returns[etf] = cum

# Returns multiplier (e.g. 1.08) for 1 full year of returns
def simulate_year():
    for etf in config.etf_names:
        annual_cum_returns[etf]['return'] = 1

    for _ in range(config.num_trading_days):
        random_generated_return = np.random.normal(loc=config.daily_return, scale=config.daily_standard_deviation)
        for etf in config.etf_names:
            cum = annual_cum_returns[etf]
            cum['return'] *= (1 + random_generated_return*cum['multiple']) * cum['daily_fee_multiplier']
            annual_cum_returns[etf] = cum

build_annual_cum_returns()

def run(years):

    start_time = time.time()
    print()

    for y in range(years):
        simulate_year()
        for etf in config.etf_names:
            results[etf].append(annual_cum_returns[etf]['return'])
        
        pct_complete = int((y/years)*100)
        dot_count = int(80*pct_complete/100) - len(str(pct_complete)) - 1
        
        print(f"{pct_complete}%" + "."*dot_count)
        print(f"Simulating {y+1:,} years")
        print(f"{time.time() - start_time:.2f} seconds")
        sys.stdout.write("\033[F"*3)  # \033[F resets 'cursor' to begging of line (x3)

    print("100%" + "."*76 + "\033[K")  # \033[K clears remainder of line
    print(f"Simulated {y+1:,} years\033[K")
    print(f"{time.time() - start_time:.2f} seconds\033[K")

run(config.years_to_simulate)

with open(PATH+'/results/annual_sim_data.json', 'w') as file:
    json.dump(results, file)
