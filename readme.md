# Infoblox Python Scripts

This repository contains Python scripts for working with Infoblox Grids.

# Scripts

- `infoblox_backup.py`: Downloads the Infoblox database backup from a specified Infoblox Grid and saves it locally with the current date appended to the filename.
- `infoblox_export_networks.py`: Exports all networks from a specified Infoblox Grid to a CSV file.

# Requirements

- Python 3.x
- `requests` library
- `csv` library (for `infoblox_export_networks.py`)

# Installation

1. Install Python 3.x  
2. Install the `requests` library by running `pip install requests` in the command line.
3. Install the `csv` library by running `pip install csv` in the command line (for `infoblox_export_networks.py`).

# Contributing
Feel free to contribute to this repository by submitting pull requests or opening issues.

# License

These scripts are licensed under the MIT License.