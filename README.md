# Model Data Monitoring Script

This Python script monitors model performance and data drift between a reference dataset (e.g., training data) and a current dataset (e.g., data in production). It generates reports for data drift, target drift, and statistical metrics for numerical features, and stores results along with metadata in both JSON and Excel formats.

## Features
- **Metadata Generation**: Captures event metadata such as the timestamp, record count, source system, user, and model version.
- **Data Drift Report**: Automatically generates a data drift report comparing reference and current datasets.
- **Target Drift Report**: Monitors drift in target labels between datasets.
- **Statistical Summary**: Computes statistics (mean, standard deviation, variance) for numerical features across both datasets.
- **Report Storage**: Saves the final results in JSON and Excel formats for easy sharing and analysis.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.x
- Required packages (install with the command below):

```bash

pip install pandas evidently openpyxl
 ```

## How to Run

1. **Prepare the Data**: Ensure you have your reference and current datasets loaded in CSV format. The script compares these datasets.

2. **Define Column Mappings**: Set the numerical and categorical features, target, and prediction column names in the script.

3. **Run the Script**: You can run the script directly from the command line or in a Python environment. Make sure to update paths for your data files if needed.

    ```bash
    python monitoring.py
    ```

4. **Results**: The script will generate:
   - A data drift report (`data_drift_report.html`)
   - A target drift report (`target_drift_report.html`)
   - A JSON file with metadata, drift metrics, and statistics (`monitoring_results.json`)
   - An Excel file summarizing the results (`monitoring_results.xlsx`)
  

### Notes:
- Replace `monintoring.py` with the actual name of your script.
- Update the `usage example` section if there are additional parameters or specifics for data loading.
     
