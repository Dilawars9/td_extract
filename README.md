# Gaussian TD Log File Parser

## Overview
This Python script parses Gaussian TD (Time-Dependent) log files to extract excited state data and calculates Singlet-Triplet (S-T) energy gaps, with output in a user-friendly format. It can generate both minimal and full data output files, depending on user options.

## Features
- **Extracts Excited State Data**: Parses state type, energy, wavelength, oscillator strength, and computes energy in different units.
- **Supports Energy Unit Conversion**:
  - Converts excitation energies from eV to kcal/mol, cm⁻¹, and Hartree.
- **Calculates S-T Energy Gaps**: Computes energy gaps between each singlet and triplet state, outputting them in eV.
- **Flexible Output**: Provides full or minimal data outputs based on command-line options.

## Requirements
- Python 3.x

## Usage
The script accepts command-line arguments for input file specification and output options. Run the script as follows:

```bash
python parse_gaussian_log.py -i <input_log_file> [--full] [--minimal]

