import json
import sys
import time
import numpy as np
import yaml
from pathlib import Path
from helper import getAbsPath

class Config:
    def __init__(self):
        self.PATH = getAbsPath()
        with open(Path(self.PATH, 'files', 'config.yml'), 'r') as file:
            self.CONFIG = yaml.safe_load(file)
        self.NUM_TRADING_DAYS = 252
        self.DAILY_RETURN = (1 + self.CONFIG['annual_return'])**(1/self.NUM_TRADING_DAYS) - 1
        self.DAILY_STANDARD_DEVIATION = self.CONFIG['annual_standard_deviation'] / (self.NUM_TRADING_DAYS**0.5)
        self.DAILY_EXPENSE_RATIO_MULTIPLIER = self.annual_fee_to_daily_fee_multiplier(fee=self.CONFIG['annual_expense_ratio'])
        self.ANNUAL_FED_FUNDS_RATE = self.CONFIG['annual_fed_funds_rate']
        self.YEARS_TO_SIMULATE = self.CONFIG['years_to_simulate']
        self.ETF_INFO = self.CONFIG['etfs']
        self.ETF_NAMES = list(self.ETF_INFO.keys())

    def annual_fee_to_daily_fee_multiplier(self, fee):
        return (1 - fee)**(1/self.NUM_TRADING_DAYS)

    def daily_fed_funds_rate_multiplier(self, leverage):
        return self.annual_fee_to_daily_fee_multiplier(self.ANNUAL_FED_FUNDS_RATE*leverage)

def build_annual_cum_returns(config, annual_cum_returns):
    for etf in config.ETF_NAMES:
        cum = annual_cum_returns[etf]
        cum['leverage'] = cum['multiple'] - 1
        if cum['leverage'] == 0:
            cum['daily_fee_multiplier'] = 1
        else:
            cum['daily_fee_multiplier'] = config.DAILY_EXPENSE_RATIO_MULTIPLIER * config.daily_fed_funds_rate_multiplier(leverage=cum['leverage'])
        annual_cum_returns[etf] = cum

def simulate_year(config, annual_cum_returns):
    for etf in config.ETF_NAMES:
        annual_cum_returns[etf]['return'] = 1

    for _ in range(config.NUM_TRADING_DAYS):
        random_generated_return = np.random.normal(loc=config.DAILY_RETURN, scale=config.DAILY_STANDARD_DEVIATION)
        for etf in config.ETF_NAMES:
            cum = annual_cum_returns[etf]
            cum['return'] *= (1 + random_generated_return*cum['multiple']) * cum['daily_fee_multiplier']
            annual_cum_returns[etf] = cum

def run_simulation(config, results, annual_cum_returns):
    start_time = time.time()
    print()

    for y in range(config.YEARS_TO_SIMULATE):
        simulate_year(config, annual_cum_returns)
        for etf in config.ETF_NAMES:
            results[etf].append(annual_cum_returns[etf]['return'])

        pct_complete = int((y/config.YEARS_TO_SIMULATE)*100)
        dot_count = int(80*pct_complete/100) - len(str(pct_complete)) - 1

        print(f"{pct_complete}%" + "."*dot_count)
        print(f"Simulating {y+1:,} years")
        print(f"{time.time() - start_time:.2f} seconds")
        sys.stdout.write("\033[F"*3)  # \033[F resets 'cursor' to begging of line (x3)

    print("100%" + "."*76 + "\033[K")  # \033[K clears remainder of line
    print(f"Simulated {y+1:,} years\033[K")
    print(f"{time.time() - start_time:.2f} seconds\033[K")

def main():
    config = Config()
    results = {etf: [] for etf in config.ETF_NAMES}
    annual_cum_returns = config.ETF_INFO.copy()

    build_annual_cum_returns(config, annual_cum_returns)
    run_simulation(config, results, annual_cum_returns)

    with open(Path(config.PATH, 'results', 'annual_sim_data.json'), 'w') as file:
        json.dump(results, file)

if __name__ == "__main__":
    main()
