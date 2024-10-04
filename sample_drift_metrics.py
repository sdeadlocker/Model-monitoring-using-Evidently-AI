import pandas as pd
import numpy as np
from scipy import stats

class DriftMetrics:
    def __init__(self, reference_df, current_df, col='probabilities_score'):
        '''Initialize the class with reference and current datasets.'''
        self.reference_df = reference_df
        self.current_df = current_df
        self.col = col
    
    # Instance method for assigning static deciles based on fixed bin ranges
    def assign_static_deciles(self):
        '''This function assigns static deciles based on predefined bin ranges.'''

        # Define static bin ranges (adjust these based on your needs)
        bin_edges = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 1.0]
        bin_labels = [f'Decile_{i+1}' for i in range(len(bin_edges)-1)]

        # Assign deciles based on static bin ranges
        self.reference_df['decile'] = pd.cut(self.reference_df[self.col], bins=bin_edges, labels=bin_labels, include_lowest=True)
        self.current_df['decile'] = pd.cut(self.current_df[self.col], bins=bin_edges, labels=bin_labels, include_lowest=True)

        return self.reference_df, self.current_df

    # Instance method for calculating KS Statistic for drift detection
    def calculate_ks_stat(self, p_value_threshold=0.05):
        '''This function performs the KS test on the decile column of two datasets to detect drift.'''

        test = stats.ks_2samp(self.reference_df['decile'].cat.codes, self.current_df['decile'].cat.codes)
        if test[1] < p_value_threshold:
            print(f"Significant drift detected in column: {self.col} as KS Statistic: {test[0]:.4f}, p-value: {test[1]:.4f}")
            return True
        else:
            print(f"No significant drift detected in column: {self.col} as KS Statistic: {test[0]:.4f}, p-value: {test[1]:.4f}")
            return False

    # Instance method for calculating Population Stability Index (PSI)
    def calculate_psi(self):
        '''Calculates the PSI based on the decile column between two datasets.'''

        # Calculate decile distributions (proportions) for reference and current datasets
        reference_dist = self.reference_df['decile'].value_counts(normalize=True).sort_index()
        current_dist = self.current_df['decile'].value_counts(normalize=True).sort_index()

        # Ensure both distributions have all deciles represented (if missing, fill with 0)
        all_deciles = pd.Series([f'Decile_{i+1}' for i in range(10)])
        reference_dist = reference_dist.reindex(all_deciles, fill_value=0)
        current_dist = current_dist.reindex(all_deciles, fill_value=0)

        # Replace zeroes to avoid division by zero or log of zero errors
        reference_dist = np.where(reference_dist == 0, 1e-6, reference_dist)
        current_dist = np.where(current_dist == 0, 1e-6, current_dist)

        # Calculate PSI using the formula
        psi_values = (current_dist - reference_dist) * np.log(current_dist / reference_dist)
        psi = np.sum(psi_values)

        return psi


# Sample data
data = {
    'probabilities_score': [0.0192, 0.05, 0.1537, 0.2141, 0.35, 0.65, 0.79, 0.101, 0.27, 0.6]
}

current1 = {
    'probabilities_score': [0.0192, 0.05, 0.1537, 0.2141, 0.35, 0.65, 0.79, 0.101, 0.27, 0.6]
}
current2 = {
    'probabilities_score': [0.06, 0.16, 0.24, 0.34, 0.44, 0.35, 0.66, 0.58, 0.28, 0.9]
}

# Create DataFrames
reference = pd.DataFrame(data)
current1 = pd.DataFrame(current1)
current2 = pd.DataFrame(current2)

# Create DriftMetrics instance
drift_metrics1 = DriftMetrics(reference, current1)
drift_metrics2 = DriftMetrics(reference, current2)

# Assign deciles
reference, current1 = drift_metrics1.assign_static_deciles()
reference, current2 = drift_metrics2.assign_static_deciles()

# Calculate KS Statistic
print("KS Test for current dataset 1:")
drift_metrics1.calculate_ks_stat()

print("KS Test for current dataset 2:")
drift_metrics2.calculate_ks_stat()

# Calculate PSI
psi_value1 = drift_metrics1.calculate_psi()
psi_value2 = drift_metrics2.calculate_psi()

print("PSI value for current1 dataset:", psi_value1)
print("PSI value for current2 dataset:", psi_value2)
