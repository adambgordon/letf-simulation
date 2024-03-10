### Simulation for thousands or millions years of leveraged ETFs vs index.
___

# Leveraged ETF Simulation

This repository contains a Python scripts to simulate thousands or millions of years leveraged exchange traded funds (ETFs) against an index. The simulation generates annual returns for for the underlying index and it's leveraged ETF counterparts based on a given configuration and then aggregates the simulated data to generate probabilites.

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

1. `run_both.py`: This is the main script that you should run. It executes both the simulation and the aggregation scripts.

2. `run_simulation.py`: This script simulates the annual returns for the ETFs based on the configuration provided in `config.yml`.

3. `run_aggregation.py`: This script aggregates the simulated data and writes the results to a CSV file.

4. `helper.py`: This script contains helper functions used by other scripts.

5. `thread_timer.py`: This script contains a thread that prints the elapsed time.

6. `config.yml`: This is the configuration file where you can specify the parameters for the simulation.

## Configuration

The `config.yml` file contains the following parameters:

- `annual_return`: The expected annual return.
- `annual_standard_deviation`: The expected annual standard deviation.
- `annual_expense_ratio`: The annual expense ratio.
- `annual_fed_funds_rate`: The annual federal funds rate.
- `years_to_simulate`: The number of years to simulate.
- `etfs`: A dictionary where the keys are the names of the ETFs and the values are dictionaries containing the `multiple` for each ETF.
- `blends`: A dictionary where the keys are the names of the blends and the values are dictionaries containing the proportion of each ETF in the blend.

Here is an example configuration:

```yaml
annual_return: 0.08
annual_standard_deviation: 0.12
annual_expense_ratio: 0.0095
annual_fed_funds_rate: 0.03
years_to_simulate: 10000
etfs: {
  1x: {multiple: 1},
  2x: {multiple: 2},
  3x: {multiple: 3}
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

### run_simulation.py

This script simulates the annual returns for the ETFs based on the configuration provided in `config.yml`. It uses a class `Data` to store all the necessary information for the simulation. The `Data` class has several methods to calculate daily returns, daily expense ratio multiplier, and daily federal funds rate multiplier. The simulation is run for the number of years specified in the configuration file. The results of the simulation are written to a JSON file.

### run_aggregation.py

This script aggregates the simulated data and writes the results to a CSV file. It uses a class `Data` to store all the necessary information for the aggregation. The `Data` class reads the simulated data from the JSON file and calculates the return percentiles for each ETF and each year bucket. It also calculates the return percentiles for the blends specified in the configuration file. The results of the aggregation are written to a CSV file.

### helper.py

This script contains a helper function `getAbsPath` that returns the absolute path of the project directory.

### thread_timer.py

This script contains a thread `ElapsedTimeThread` that prints the elapsed time. The thread is started before the aggregation and stopped after the aggregation is complete.