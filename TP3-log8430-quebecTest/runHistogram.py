import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Initialize a list to store the data
data = []

# Directory containing the result files
results_dir = 'results/'

# List all files in the directory
files = os.listdir(results_dir)

# Process only files that match the pattern 'run*.csv'
for filename in files:
    if filename.startswith('run') and filename.endswith('.csv'):
        # Extract the database name and the number of nodes from the filename
        match = re.match(r'run(\w+?)(\d+)\.csv', filename)
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

                # Skip the 'Initializing results' line if present
                while lines and ('Initializing results' in lines[0] or not lines[0].strip()):
                    lines = lines[1:]  # Skip the first line

                if not lines:
                    continue

                # Find the line that starts with 'Running workload'
                for idx, line in enumerate(lines):
                    workload_match = re.match(r'Running workload ([A-C]) try (\d+)', line)
                    if workload_match:
                        workload = workload_match.group(1)
                        try_number = int(workload_match.group(2))
                        # Adjust lines to start from this line
                        lines = lines[idx:]
                        break
                else:
                    continue  # If no matching line is found, skip the section

                throughput = None
                avg_read_latency = None
                avg_update_latency = None
                read_95th = None
                update_95th = None

                # Extract the metrics from the lines
                for line in lines:
                    if '[OVERALL], Throughput(ops/sec),' in line:
                        throughput = float(line.split(',')[2])
                    elif '[READ], AverageLatency(us),' in line:
                        avg_read_latency = float(line.split(',')[2])
                    elif '[UPDATE], AverageLatency(us),' in line:
                        avg_update_latency = float(line.split(',')[2])
                    elif '[READ], 95thPercentileLatency(us),' in line:
                        read_95th = float(line.split(',')[2])
                    elif '[UPDATE], 95thPercentileLatency(us),' in line:
                        update_95th = float(line.split(',')[2])

                if throughput is not None:
                    data_entry = {
                        'Database': db_name,
                        'Nodes': nodes,
                        'Workload': workload,
                        'Try': try_number,
                        'Throughput': throughput
                    }
                    if avg_read_latency is not None:
                        data_entry['AvgReadLatency'] = avg_read_latency
                    if avg_update_latency is not None:
                        data_entry['AvgUpdateLatency'] = avg_update_latency
                    if read_95th is not None:
                        data_entry['Read95thLatency'] = read_95th
                    if update_95th is not None:
                        data_entry['Update95thLatency'] = update_95th

                    data.append(data_entry)

# Create a pandas DataFrame from the data
df = pd.DataFrame(data)

# Ensure that numeric columns are of numeric type
numeric_columns = ['Try', 'Nodes', 'Throughput', 'AvgReadLatency', 'AvgUpdateLatency', 'Read95thLatency', 'Update95thLatency']
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Combine 'Database' and 'Nodes' into a single column for the x-axis
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

# Graph 1: Throughput comparison with adjusted error bars
plt.figure(figsize=(12, 6))
ax = sns.barplot(
    data=df,
    x='Database_Nodes',
    y='Throughput',
    hue='Workload_Label',
    palette='pastel',
    errorbar=('ci', 95),
    errwidth=1.5,
    capsize=0.1
)
for container in ax.containers:
    ax.bar_label(container, fmt='%.1f', padding=0, label_type='center', color='white')

plt.title('Throughput Comparison for the Run Phase (ops/sec)')
plt.ylabel('Throughput (ops/sec)')
plt.xlabel('Database and Nodes')
plt.legend(title='Workload')
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, 'throughput_run_comparison_single.png'))
plt.show()

# Graph 2: Average Read Latency
plt.figure(figsize=(12, 6))
ax = sns.barplot(
    data=df,
    x='Database_Nodes',
    y='AvgReadLatency',
    hue='Workload_Label',
    palette='pastel',
    errorbar=('ci', 95),
    errwidth=1.5,
    capsize=0.1
)
for container in ax.containers:
    ax.bar_label(container, fmt='%.1f', padding=0, label_type='center', color='white')

plt.title('Average Read Latency for the Run Phase (µs)')
plt.ylabel('Average Read Latency (µs)')
plt.xlabel('Database and Nodes')
plt.legend(title='Workload')
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, 'read_latency_run_comparison_single.png'))
plt.show()

# Graph 3: Average Update Latency (Workloads A and B)
df_update = df[df['Workload'] != 'C'].dropna(subset=['AvgUpdateLatency'])

plt.figure(figsize=(12, 6))
ax = sns.barplot(
    data=df_update,
    x='Database_Nodes',
    y='AvgUpdateLatency',
    hue='Workload_Label',
    palette='pastel',
    errorbar=('ci', 95),  # Intervalle de confiance à 95%
    errwidth=1.5,
    capsize=0.1
)
for container in ax.containers:
    ax.bar_label(container, fmt='%.1f', padding=0, label_type='center', color='white')

plt.title('Average Update Latency for the Run Phase (µs)')
plt.ylabel('Average Update Latency (µs)')
plt.xlabel('Database and Nodes')
plt.legend(title='Workload')
plt.tight_layout()
plt.savefig(os.path.join(figures_dir, 'update_latency_run_comparison_single.png'))
plt.show()
