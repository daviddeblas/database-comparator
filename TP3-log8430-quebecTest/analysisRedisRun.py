import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt  # Import matplotlib for visualization

# Load the CSV file
data_path = 'results-pc-david/outputRunRedis3.csv'  # Updated to reflect the "Run" analysis
df = pd.read_csv(data_path, delimiter=';', engine='python')

# Correct workload identification to differentiate A, B, C explicitly for the Run analysis
workload_data = {}
current_workload = None

for _, row in df.iterrows():
    line = row.iloc[0].strip()  # Use iloc to access the first column value correctly

    # Detect workload header line and correctly extract the workload identifier ('A', 'B', or 'C')
    if line.startswith("Running test workoad"):
        parts = line.split()
        current_workload = parts[3]  # Extract the workload identifier correctly

        # Initialize workload entry if it doesn't exist
        if current_workload not in workload_data:
            workload_data[current_workload] = {
                "RunTime_ms": [],
                "Throughput_ops_sec": [],
                "Read_AvgLatency_us": [],
                "Update_AvgLatency_us": [],
                "Cleanup_AvgLatency_us": []
            }

    elif current_workload in workload_data:
        # Parse fields of interest and append to the corresponding workload data
        if "[OVERALL]" in line and "RunTime(ms)" in line:
            value = int(line.split(",")[-1].strip())
            workload_data[current_workload]["RunTime_ms"].append(value)
        elif "[OVERALL]" in line and "Throughput(ops/sec)" in line:
            value = float(line.split(",")[-1].strip())
            workload_data[current_workload]["Throughput_ops_sec"].append(value)
        elif "[READ]" in line and "AverageLatency(us)" in line:
            value = float(line.split(",")[-1].strip())
            workload_data[current_workload]["Read_AvgLatency_us"].append(value)
        elif "[UPDATE]" in line and "AverageLatency(us)" in line:
            value = float(line.split(",")[-1].strip())
            workload_data[current_workload]["Update_AvgLatency_us"].append(value)
        elif "[CLEANUP]" in line and "AverageLatency(us)" in line:
            value = float(line.split(",")[-1].strip())
            workload_data[current_workload]["Cleanup_AvgLatency_us"].append(value)

# Function to calculate the confidence interval
def calculate_confidence_interval(data, confidence=0.95):
    if len(data) < 2:
        return None, None  # Not enough data to calculate CI
    mean = np.mean(data)
    sem = stats.sem(data)
    h = sem * stats.t.ppf((1 + confidence) / 2, len(data) - 1)
    return mean, h

# Calculate confidence intervals for each workload and each metric individually
confidence_intervals = {}
for workload, metrics in workload_data.items():
    confidence_intervals[workload] = {}
    for metric, values in metrics.items():
        mean, ci = calculate_confidence_interval(values)
        confidence_intervals[workload][metric] = {"mean": mean, "ci": ci}

# Convert confidence intervals to a DataFrame for better readability
ci_df = pd.DataFrame(confidence_intervals).T
print(ci_df)

# Plotting the results using matplotlib
for metric in ["RunTime_ms", "Throughput_ops_sec", "Read_AvgLatency_us", "Update_AvgLatency_us"]:
    fig, ax = plt.subplots()
    workloads = []
    means = []
    cis = []

    # Collect only valid data (i.e., no None values)
    for workload in ci_df.index:
        if ci_df.loc[workload, metric]["mean"] is not None and ci_df.loc[workload, metric]["ci"] is not None:
            workloads.append(workload)
            means.append(ci_df.loc[workload, metric]["mean"])
            cis.append(ci_df.loc[workload, metric]["ci"])

    # Plot only if there is valid data
    if workloads:
        ax.bar(workloads, means, yerr=cis, capsize=5, alpha=0.7, color='b')
        ax.set_ylabel(metric)
        ax.set_title(f'{metric} with Confidence Intervals for Workloads A, B, C')
        ax.set_xlabel('Workload')

        plt.show()
