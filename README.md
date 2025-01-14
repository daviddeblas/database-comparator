# Redis vs MongoDB: A Comparative Study

## Project Overview
This project compares the performance of two NoSQL databases, Redis and MongoDB, in distributed environments. Conducted as part of the **Software architecture and advanced design** course at Polytechnique Montréal, the study evaluates these databases based on speed, latency, and scalability under various workloads.

---

## Key Objectives
- Test Redis and MongoDB performance under different workloads:
  - **50% read / 50% write**
  - **100% read / 0% write**
  - **10% read / 90% write**
- Analyze scalability with 3-node and 5-node configurations.
- Highlight strengths and weaknesses in distributed setups.

---

## Environment
- **Tools**: Docker Compose, YCSB (Yahoo Cloud Serving Benchmark), Bash scripts, Python scripts.
- **Databases**:
  - **Redis**: In-memory key-value store.
  - **MongoDB**: Document-oriented database.
- **Tests**: Simulated real-world read/write workloads with metrics for latency and throughput.

---

## Key Results
- **Redis**:
  - Excels in write-heavy workloads with low latency.
- **MongoDB**:
  - Less performant than Redis but supports complex queries.

---
## Authors
- David de Blas
- Jenseth Alexandra Fuentes-Rodriguez
- Arnaud Larochelle
- Abdelkrim Nahi
