# Data Analysis Automation Script

## Overview

This script automates the process of analyzing datasets, generating analysis plans, writing Python code for data processing, and producing a detailed report (README.md). The report includes the generated code, analysis plans, results, and generated plots, providing a comprehensive overview of the dataset and the analysis performed.

## Features

- **Data Loading**: Handles CSV file loading with multiple encodings (UTF-8, ISO-8859-1, latin1, etc.).
- **Analysis Planning**: Uses GPT-4 to generate an analysis plan based on a sample of the dataset.
- **Code Generation**: Generates Python code for the analysis based on the plan.
- **Error Handling**: Catches and logs errors during execution, automatically attempting fixes.
- **Report Generation**: Creates a comprehensive README.md file that includes the analysis plan, generated code, results, and plots.

## Requirements

- Python 3.x
- `requests` library for API interaction
- `pandas` for data manipulation
- `chardet` for encoding detection
- OpenAI API access (via `AIPROXY_TOKEN` environment variable)

## Usage

1. Install dependencies:
   ```bash
   pip install requests pandas chardet
