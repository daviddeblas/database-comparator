import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize a list to store the data
data = []

# Directory containing the result files
results_dir = 'results/'

# List all files in the directory
files = os.listdir(results_dir)

# Process only files that match the pattern 'load*.csv'
for filename in files:
    if filename.startswith('load') and filename.endswith('.csv'):
        # Extract the database name and the number of nodes from the filename
        match = re.match(r'load(\w+)(\d+)\.csv', filename)
        if match:
            db_name = match.group(1)  # 'Mongo' or 'Redis'
            nodes = int(match.group(2))  # 3 or 5

            # Open and read the content of the file
            with open(os.path.join(results_dir, filename), 'r') as file:
                content = file.read()

            # Split the content into sections based on the separator
            sections = re.split(r'#+\n', content)

            # Process each section to extract the information
            for section in sections:
                if not section.strip():
                    continue  # Skip empty sections

                lines = section.strip().split('\n')

                # Extract the workload and the try number
                workload_try_line = lines[0]
                workload_match = re.match(r'Loading workload ([A-C]) try (\d+)', workload_try_line)
                if workload_match:
                    workload = workload_match.group(1)
                    try_number = int(workload_match.group(2))
                else:
                    continue  # Skip if the format doesn't match

                throughput = None
                avg_latency = None

                # Extract the throughput and average latency from the lines
                for line in lines:
                    if '[OVERALL], Throughput(ops/sec),' in line:
                        throughput = float(line.split(',')[2])
                    elif '[INSERT], AverageLatency(us),' in line:
                        avg_latency = float(line.split(',')[2])

                if throughput is not None and avg_latency is not None:
                    data.append({
                        'Database': db_name,
                        'Nodes': nodes,
                        'Workload': workload,
                        'Try': try_number,
                        'Throughput': throughput,
                        'AvgLatency': avg_latency
                    })

# Create a pandas DataFrame from the data
df = pd.DataFrame(data)

# Combine database and nodes into a single label for the x-axis
df['Database_Nodes'] = df['Database'] + df['Nodes'].astype(str)

# Map workloads to detailed labels
workload_labels = {
    'A': '50% Read / 50% Write',
    'B': '10% Read / 90% Write',
    'C': '100% Read / 0% Write'
}
df['Workload_Label'] = df['Workload'].map(workload_labels)

# Set the style for seaborn
sns.set(style="whitegrid")

# Ensure the 'figures' directory exists
figures_dir = 'figures/'
if not os.path.exists(figures_dir):
    os.makedirs(figures_dir)

# Graph 1: Throughput comparison with workloads in colors
plt.figure(figsize=(12, 6))
ax = sns.barplot(
    data=df,
    x='Database_Nodes',
    y='Throughput',
    hue='Workload_Label',
    palette='pastel',
    errorbar=('ci', 95),  # Confidence interval at 95%
    errwidth=1.5,
    capsize=0.1
)
for container in ax.containers:
    ax.bar_label(container, fmt='%.1f', padding=2, label_type='center', color='white')

plt.title('Throughput Comparison for the Load Phase (ops/sec)')
plt.ylabel('Throughput (ops/sec)')
plt.xlabel('Database and Nodes')
plt.legend(title='Workload')
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, 'load_throughput_comparison.png'))
plt.show()

# Graph 2: Average Latency comparison with workloads in colors
plt.figure(figsize=(12, 6))
ax = sns.barplot(
    data=df,
    x='Database_Nodes',
    y='AvgLatency',
    hue='Workload_Label',
    palette='pastel',
    errorbar=('ci', 95),  # Confidence interval at 95%
    errwidth=1.5,
    capsize=0.1
)
for container in ax.containers:
    ax.bar_label(container, fmt='%.1f', padding=2, label_type='center', color='white')

plt.title('Average Insert Latency for the Load Phase (µs)')
plt.ylabel('Average Latency (µs)')
plt.xlabel('Database and Nodes')
plt.legend(title='Workload')
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, 'load_latency_comparison.png'))
plt.show()
