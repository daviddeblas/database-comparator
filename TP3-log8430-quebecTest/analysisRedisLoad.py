import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt  # Import matplotlib for visualization

# Load the CSV file
data_path = 'results-pc-david/outputLoadRedis3.csv'
df = pd.read_csv(data_path, delimiter=';', engine='python')

# Correct workload identification to differentiate A, B, C explicitly
workload_data = {}
current_workload = None

for _, row in df.iterrows():
    line = row.iloc[0].strip()  # Use iloc to access the first column value correctly

    # Detect workload header line and correctly extract the workload identifier ('A', 'B', or 'C')
    if line.startswith("Loading data worload"):
        parts = line.split()
        current_workload = parts[3]  # Extract the workload identifier correctly

        # Initialize workload entry if it doesn't exist
        if current_workload not in workload_data:
            workload_data[current_workload] = {
                "RunTime_ms": [],
                "Throughput_ops_sec": [],
                "Insert_AvgLatency_us": [],
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
        elif "[INSERT]" in line and "AverageLatency(us)" in line:
            value = float(line.split(",")[-1].strip())
            workload_data[current_workload]["Insert_AvgLatency_us"].append(value)
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
for metric in ["RunTime_ms", "Throughput_ops_sec", "Insert_AvgLatency_us", "Cleanup_AvgLatency_us"]:
    fig, ax = plt.subplots()
    workloads = ci_df.index
    means = [ci_df.loc[workload, metric]["mean"] for workload in workloads]
    cis = [ci_df.loc[workload, metric]["ci"] for workload in workloads]

    ax.bar(workloads, means, yerr=cis, capsize=5, alpha=0.7, color='b')
    ax.set_ylabel(metric)
    ax.set_title(f'{metric} with Confidence Intervals for Workloads A, B, C')
    ax.set_xlabel('Workload')

    plt.show()
