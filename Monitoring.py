import pandas as pd
import datetime
import json
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset
from evidently import ColumnMapping

# Function to get metadata
def get_metadata(event_type, source_system, user, model_version, reference, current):
    metadata = {
        "event_timestamp": datetime.datetime.now().isoformat(),  # Current time as event timestamp
        "event_type": event_type,  # Event type like 'data loaded', 'model run', etc.
        "load_date": datetime.date.today().isoformat(),  # Current date as load date
        "record_count_reference": len(reference),  # Record count in reference data
        "record_count_current": len(current),  # Record count in current data
        "source_system": source_system,  # Origin of the data, e.g., 'ECR'
        "user": user,  # User who triggered the action
        "model_version": model_version  # Model version being used
    }
    return metadata

# Function to calculate statistical summary for numerical features
def calculate_statistics(numerical_features, reference, current):
    statistics = {}
    for feature in numerical_features:
        stats = {
            'mean_reference': reference[feature].mean(),
            'std_reference': reference[feature].std(),
            'var_reference': reference[feature].var(),
            'mean_current': current[feature].mean(),
            'std_current': current[feature].std(),
            'var_current': current[feature].var()
        }
        statistics[feature] = stats
    
    return statistics

# Function to generate a data drift report
def generate_data_drift_report(reference, current, column_mapping):
    data_drift_report = Report(metrics=[DataDriftPreset()])
    data_drift_report.run(reference_data=reference, current_data=current, column_mapping=column_mapping)
    data_drift_report.save_html('data_drift_report.html')
    return data_drift_report.as_dict()

# Function to generate target drift report
def generate_target_drift_report(reference, current, column_mapping):
    target_drift_report = Report(metrics=[TargetDriftPreset()])
    target_drift_report.run(reference_data=reference, current_data=current, column_mapping=column_mapping)
    target_drift_report.save_html('target_drift_report.html')
    return target_drift_report.as_dict()

# Function to save results as JSON and Excel files
def save_results_as_files(final_results):
    # Save as JSON file
    with open('monitoring_results.json', 'w') as json_file:
        json.dump(final_results, json_file, indent=4)

    # Prepare data for Excel export
    # Flatten metadata, data drift, and target drift for easier export to Excel
    metadata_df = pd.DataFrame([final_results['metadata']])

    # Flatten data drift metrics and target drift metrics (if needed, adjust the structure)
    data_drift_df = pd.json_normalize(final_results['data_drift_metrics'])
    target_drift_df = pd.json_normalize(final_results['target_drift_metrics'])

    # Convert statistical summary to DataFrame
    statistics_df = pd.DataFrame(final_results['statistical_summary']).T

    # Create a writer to save multiple DataFrames to different sheets in Excel
    with pd.ExcelWriter('monitoring_results.xlsx') as writer:
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        data_drift_df.to_excel(writer, sheet_name='Data Drift Metrics', index=False)
        target_drift_df.to_excel(writer, sheet_name='Target Drift Metrics', index=False)
        statistics_df.to_excel(writer, sheet_name='Statistical Summary', index=True)

# Main function to execute and collect metadata, drift reports, and statistics
def monitor_model_data(reference, current, column_mapping, source_system, user, model_version):
    # Get Metadata
    metadata = get_metadata(
        event_type='model run',
        source_system=source_system,
        user=user,
        model_version=model_version,
        reference=reference,
        current=current
    )

    # Generate Data Drift Report
    data_drift_results = generate_data_drift_report(reference, current, column_mapping)

    # Generate Target Drift Report
    target_drift_results = generate_target_drift_report(reference, current, column_mapping)

    # Calculate statistics for numerical features
    numerical_features = column_mapping.numerical_features
    statistics = calculate_statistics(numerical_features, reference, current)

    # Compile all metrics into a single dictionary
    final_results = {
        "metadata": metadata,
        "data_drift_metrics": data_drift_results,
        "target_drift_metrics": target_drift_results,
        "statistical_summary": statistics
    }

    # Save the results as JSON and Excel files
    save_results_as_files(final_results)

    return final_results

# Example usage
if __name__ == "__main__":
    # Load data
    data = pd.read_csv('sample_data.csv')

    # Define the data and column mapping
    target = 'cnt'
    prediction = 'prediction'
    numerical_features = ['temp', 'atemp', 'hum', 'windspeed', 'hr', 'weekday']
    categorical_features = ['season', 'holiday', 'workingday']

    reference = data.iloc[:12000]  
    current = data.iloc[12000:17379]

    column_mapping = ColumnMapping()
    column_mapping.target = target
    column_mapping.prediction = prediction
    column_mapping.numerical_features = numerical_features
    column_mapping.categorical_features = categorical_features

    # Define metadata details
    source_system = 'ECR'
    user = 'admin_user'
    model_version = '1.0.0'

    # Call the monitoring function
    final_results = monitor_model_data(reference, current, column_mapping, source_system, user, model_version)

    print("\nFinal Monitoring Results Saved as JSON and Excel Files.")
