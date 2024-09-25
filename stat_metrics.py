import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, roc_curve
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Functions for PSI and K-S statistic
def calculate_psi(expected, actual, bins=10, epsilon=1e-10):
    """Calculate psi"""
    
    def scale_range(input, min_val, max_val):
        """scales the input array to a specified range"""
        input += -(np.min(input))  # Shifts the input data so that the minimum value is 0.
        input /= np.max(input) / (max_val - min_val) 
        input += min_val          # Shifts the scaled data to start from min_val
        return input

    breakpoints = np.linspace(0, 1, bins + 1)
    expected_percents = np.histogram(scale_range(expected, 0, 1), bins=breakpoints)[0] / len(expected)
    actual_percents = np.histogram(scale_range(actual, 0, 1), bins=breakpoints)[0] / len(actual)

    # Add epsilon to prevent log(0) and division by zero
    expected_percents = np.where(expected_percents == 0, epsilon, expected_percents)
    actual_percents = np.where(actual_percents == 0, epsilon, actual_percents)

    psi_value = np.sum((expected_percents - actual_percents) * np.log(expected_percents / actual_percents)) # formula
    return psi_value

def visualize_psi_distribution(expected, actual, bins=10):
    """Visualize the distributions of expected and actual probabilities."""
    # Bin the data for both expected and actual
    breakpoints = np.linspace(0, 1, bins + 1)
    expected_percents = np.histogram(expected, bins=breakpoints, density=True)[0]
    actual_percents = np.histogram(actual, bins=breakpoints, density=True)[0]

    # Visualization
    plt.figure(figsize=(10, 6))
    
    # Create a bar plot for the expected distribution
    sns.histplot(expected, bins=breakpoints, color='blue', alpha=0.6, label='Expected (Training)', stat='density')
    
    # Create a bar plot for the actual distribution
    sns.histplot(actual, bins=breakpoints, color='orange', alpha=0.6, label='Actual (Testing)', stat='density')
    
    # Calculate PSI
    psi_value = calculate_psi(expected, actual, bins)
    
    # Add labels and title
    plt.xlabel("Probability Scores")
    plt.ylabel("Density")
    plt.title(f"Distribution Comparison (PSI: {psi_value:.4f})")
    plt.legend()
    
    # Show the plot
    plt.show()
    
    return psi_value

def calculate_ks_statistic(y_true, y_pred_prob):
    """Calculate KS stats"""
    fpr, tpr, _ = roc_curve(y_true, y_pred_prob)
    ks_stat = np.max(tpr - fpr)
    return ks_stat

def compute_metrics(df, target_col, pred_prob_col):
    """Compute metrics."""
    
    # Step 1: Create binary prediction from probabilities
    df['prediction'] = np.where(df[pred_prob_col] > 0.5, 1, 0)
    
    # Step 2: Extract true labels and predicted probabilities
    y_true = df[target_col]
    y_pred = df['prediction']
    y_pred_prob = df[pred_prob_col]
    
    # Step 3: Compute performance metrics
    accuracy = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    auc = roc_auc_score(y_true, y_pred_prob)
    # psi = calculate_psi(y_true, y_pred_prob)
    psi = calculate_psi(y_true, y_pred)
    ks_stat = calculate_ks_statistic(y_true, y_pred_prob)
    
    # Print or return the metrics
    metrics = {
        "Accuracy": accuracy,
        "F1 Score": f1,
        "AUC": auc,
        "PSI": psi,
        "K-S Statistic": ks_stat
    }
    
    return metrics

# Simulate Excel data in a pandas DataFrame
def generate_random_sample_data():
    """Generate a sample dataset with target and predicted probability."""
    np.random.seed(42)  # For reproducibility

    # Creating 100 rows of sample data
    sample_size = 100
    data = {
        'feature1': np.random.randn(sample_size),
        'feature2': np.random.randn(sample_size),
        'predicted_probability': np.random.rand(sample_size),  # Random probabilities between 0 and 1
        'target': np.random.randint(0, 2, sample_size)  # Binary target (0 or 1)
    }
    
    df = pd.DataFrame(data)
    return df

def generate_sample_data(sample_size=100):
    """Generate a sample dataset with target and predicted probability."""
    np.random.seed(42) 

    feature1 = np.random.randn(sample_size)
    feature2 = np.random.randn(sample_size)

    # Generate binary target values with 50% chance for 0s and 1s
    target = np.random.choice([0, 1], size=sample_size, p=[0.5, 0.5])

    predicted_probability = np.zeros(sample_size)

    # Assign probabilities based on target values
    predicted_probability[target == 1] = np.random.uniform(0.5, 1, size=np.sum(target == 1))  
    predicted_probability[target == 0] = np.random.uniform(0, 0.5, size=np.sum(target == 0))

    # Creating the DataFrame
    data = {
        'feature1': feature1,
        'feature2': feature2,
        'predicted_probability': predicted_probability,
        'target': target
    }
    
    df = pd.DataFrame(data)
    return df


def save_dataframe(df, filename):
    """Save a DataFrame to a CSV file."""
    output_path = os.path.join("output", filename)
    df.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}")

def main():
    # Generate sample data
    # df = generate_random_sample_data()
    df = generate_sample_data()
    df = pd.read_csv("input_data")
    
    # Define target column and predicted probability column
    target_col = 'target'
    pred_prob_col = 'predicted_probability'
    
    # Save the original input data
    # save_dataframe(df, "input_random_data.csv")
    save_dataframe(df, "input_data.csv")
    
    # Compute and display the metrics
    metrics = compute_metrics(df, target_col, pred_prob_col)
    
    print("Performance Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")
    
    # Add the computed metrics to a DataFrame for saving
    metrics_df = pd.DataFrame([metrics])
    
    # Save the output metrics to a CSV file
    # save_dataframe(metrics_df, "outputrandom_metrics.csv")
    save_dataframe(metrics_df, "output_metrics.csv")
    
    # Save the DataFrame with predictions and true labels
    # save_dataframe(df, "output_random_predictions.csv")
    save_dataframe(df, "output_predictions.csv")
    
    # Visualize the PSI distribution
    visualize_psi_distribution(df[pred_prob_col], df[target_col])

if __name__ == "__main__":
    if not os.path.exists('output'):
        os.makedirs('output')  # Create the output directory if it doesn't exist
    main()
