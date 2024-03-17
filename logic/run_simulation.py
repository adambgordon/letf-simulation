import json
import sys
import time
import numpy as np
import yaml
import os
from pathlib import Path
from helper import getAbsPath

class Data:
    """A class to represent the data for simulation."""

    def __init__(self):
        """Initialize the data from the config file."""
        # Get the absolute path
        self.PATH = getAbsPath()
        # Load the configuration file
        with open(Path(self.PATH, 'files', 'config.yml'), 'r') as file:
            self.CONFIG = yaml.safe_load(file)
        # Define constants
        self.NUM_TRADING_DAYS = 252
        self.DAILY_RETURN = (1 + self.CONFIG['index_annual_return'])**(1/self.NUM_TRADING_DAYS) - 1
        self.DAILY_STANDARD_DEVIATION = self.CONFIG['index_annual_standard_deviation'] / (self.NUM_TRADING_DAYS**0.5)
        # self.DAILY_EXPENSE_RATIO_MULTIPLIER = self.annual_fee_to_daily_fee_multiplier(fee=self.CONFIG['annual_expense_ratio'])
        self.fed_funds_annual_rate = self.CONFIG['fed_funds_annual_rate']
        self.YEARS_TO_SIMULATE = self.CONFIG['years_to_simulate']
        self.ETF_NAMES = list(self.CONFIG['etfs'].keys())
        self.ETF_INFO = self.CONFIG['etfs'].copy()

        for etf in self.ETF_NAMES:
            self.ETF_INFO[etf]['leverage'] = self.ETF_INFO[etf]['multiple'] - 1
            self.ETF_INFO[etf]['daily_expense_ratio_multiplier'] = self.annual_fee_to_daily_fee_multiplier(fee=self.ETF_INFO[etf]['annual_expense_ratio'])
            self.ETF_INFO[etf]['daily_fed_funds_rate_multiplier'] = self.daily_fed_funds_rate_multiplier(leverage=self.ETF_INFO[etf]['leverage'])
            self.ETF_INFO[etf]['daily_fee_multiplier'] = self.ETF_INFO[etf]['daily_expense_ratio_multiplier'] * self.ETF_INFO[etf]['daily_fed_funds_rate_multiplier']

        # Initialize results and annual cumulative returns
        self.results = {etf: [] for etf in self.ETF_NAMES}
        self.annual_cum_returns = {etf: [] for etf in self.ETF_NAMES}

    def annual_fee_to_daily_fee_multiplier(self, fee):
        """Convert annual fee to daily fee multiplier."""
        return (1 - fee)**(1/self.NUM_TRADING_DAYS)

    def daily_fed_funds_rate_multiplier(self, leverage):
        """Convert annual fed funds rate to daily multiplier."""
        return self.annual_fee_to_daily_fee_multiplier(self.fed_funds_annual_rate*leverage)

def simulate_year(data):
    """Simulate a year for each ETF."""
    for etf in data.ETF_NAMES:
        data.annual_cum_returns[etf] = 1

    for _ in range(data.NUM_TRADING_DAYS):
        random_generated_return = np.random.normal(loc=data.DAILY_RETURN, scale=data.DAILY_STANDARD_DEVIATION)
        for etf in data.ETF_NAMES:
            info = data.ETF_INFO[etf]
            cum = data.annual_cum_returns[etf]
            cum *= (1 + random_generated_return*info['multiple']) * info['daily_fee_multiplier']
            data.annual_cum_returns[etf] = cum

def run_simulation(data):
    """Run the simulation."""

    def print_status():
        """Print percent complete, proportional number of dots, and elapsed time"""
        pct_complete = int((y/data.YEARS_TO_SIMULATE)*100)
        dot_count = int(80*pct_complete/100) - len(str(pct_complete)) - 1

        print(f"{pct_complete}%" + "."*dot_count)
        print(f"Simulating {y+1:,} years")
        print(f"{time.time() - start_time:.2f} seconds")
        # \033[F resets 'cursor' to begging of line (x3)
        sys.stdout.write("\033[F"*3)

    start_time = time.time()
    print()

    for y in range(data.YEARS_TO_SIMULATE):
        simulate_year(data)
        for etf in data.ETF_NAMES:
            data.results[etf].append(data.annual_cum_returns[etf])

        # Print status and time every 40 years which is approximately every 0.1 second
        if y%40 == 0:
            print_status()

    # \033[K clears remainder of line
    print("100%" + "."*76 + "\033[K")
    print(f"Simulated {y+1:,} years\033[K")
    print(f"{time.time() - start_time:.2f} seconds\033[K")

def write_results_to_json(data):
    """Write the results to a JSON file."""
    if not os.path.exists(Path(data.PATH, 'results')):
        os.makedirs(Path(data.PATH, 'results'))
    with open(Path(data.PATH, 'results', 'annual_sim_data.json'), 'w') as file:
        json.dump(data.results, file)

def main():
    """Main function."""
    data = Data()
    # build_annual_cum_returns(data)
    run_simulation(data)
    write_results_to_json(data)

if __name__ == "__main__":
    main()
