# Leveraged ETF Simulation

This repository contains Python scripts to simulate thousands or millions of years of leveraged exchange traded funds (ETFs) against an index. The simulation generates annual returns for the underlying index and its leveraged ETF counterparts based on a given configuration and then aggregates the simulated data to generate probabilities.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Files](#files)
- [Configuration](#configuration)
- [Scripts Description](#scripts-description)

## Installation

To use this simulation, clone the repository to your local machine.

## Usage

To run the simulation and aggregation, execute the `run_both.py` script in the root directory of the project.

```bash
python run_both.py
```

## Files

The repository contains the following key files:

- `run_both.py`: This is the main script that you should run. It executes both the simulation and the aggregation scripts.
- `run_simulation.py`: This script simulates the annual returns for the ETFs based on the configuration provided in `config.yml`.
- `run_aggregation.py`: This script aggregates the simulated data and writes the results to a CSV file.
- `helper.py`: This script contains helper functions used by other scripts.
- `thread_timer.py`: This script contains a thread that prints the elapsed time.
- `config.yml`: This is the configuration file where you can specify the parameters for the simulation.

## Configuration

The `config.yml` file contains the following parameters:

- `index_annual_return`: The expected annual return.
- `index_annual_standard_deviation`: The expected annual standard deviation.
- `fed_funds_annual_rate`: The annual federal funds rate.
- `years_to_simulate`: The number of years to simulate.
- `etfs`: A dictionary where the keys are the names of the ETFs and the values are dictionaries containing the multiple for each ETF.
- `blends`: A dictionary where the keys are the names of the blends and the values are dictionaries containing the proportion of each ETF in the blend.

Here is an example configuration:

```yaml
index_annual_return: 0.08
index_annual_standard_deviation: 0.12
fed_funds_annual_rate: 0.03
years_to_simulate: 10000
etfs: {
  # 1x represents the underlying index
  1x: {
    multiple: 1,
    annual_expense_ratio: 0
  },
  2x: {
    multiple: 2,
    annual_expense_ratio: 0.0095
  },
  3x: {
    multiple: 3,
    annual_expense_ratio: 0.0095
  }
}
blends: {
  '70_30': {
    1x: 0.7,
    3x: 0.3
  },
  '50_50': {
    1x: 0.5,
    3x: 0.5
  }
}
```

## Scripts Description

### `run_simulation.py`

This script simulates the annual returns for the ETFs based on the configuration provided in `config.yml`. It uses a class `Data` to store all the necessary information for the simulation. The `Data` class has several methods to calculate daily returns, daily expense ratio multiplier, and daily federal funds rate multiplier. The simulation is run for the number of years specified in the configuration file. The results of the simulation are written to a JSON file.

### `run_aggregation.py`

This script aggregates the simulated data and writes the results to a CSV file. It uses a class `Data` to store all the necessary information for the aggregation. The `Data` class reads the simulated data from the JSON file and calculates the return percentiles for each ETF and each year bucket. It also calculates the return percentiles for the blends specified in the configuration file. The results of the aggregation are written to a CSV file.

### `helper.py`

This script contains a helper function `getAbsPath` that returns the absolute path of the project directory.

### `thread_timer.py`

This script contains a thread `ElapsedTimeThread` that prints the elapsed time. The thread is started before the aggregation and stopped after the aggregation is complete.