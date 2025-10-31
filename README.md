# 📘 FastAPI Books API

FastAPI Books API is a modern, containerized project for managing books — originally built with in-memory storage and later upgraded to use a **PostgreSQL** database for persistence. It’s designed as a **production-like FastAPI environment**, fully Dockerized for seamless development and deployment, featuring **load balancing**, **automated backups**, **performance testing**, and complete **monitoring** and **visualization** through **Prometheus and Grafana**.

<img width="1296" height="928" alt="Screenshot 2025-10-25 at 20-31-14 FastAPI - Swagger UI" src="https://github.com/user-attachments/assets/cc1594f6-4a7a-4f0d-9a73-2b9850bae092" />

### successfull run after refactoring
<img width="1303" height="297" alt="Screenshot from 2025-10-25 21-01-46" src="https://github.com/user-attachments/assets/6b9fbc9c-9781-4019-b4fa-2c75f41d1cae" />

## Overview
- This project simulates a microservice-style deployment that integrates:
- A FastAPI application
- A PostgreSQL database
- An NGINX load balancer
- Automated database backups
- Load testing via Apache Benchmark (AB)
- Customized log parser and metrics exporter
- Monitoring and visualization using Prometheus + Grafana

 ## Architecture Diagrams
 <img width="1662" height="418" alt="p01 drawio(1)" src="https://github.com/user-attachments/assets/618d1ad1-a777-4c07-acaf-63b8f78f4f05" />
 
## Components
| **Service**        | **Purpose**                                | **Technology**        |
|--------------------|--------------------------------------------|-----------------------|
| **FastAPI App**     | Handles requests, exposes metrics endpoint | FastAPI, Python       |
| **PostgreSQL**      | Main database                              | PostgreSQL 16         |
| **NGINX (Load Balancer)** | Distributes traffic across API containers | Nginx                 |
| **Backup Service**  | Periodically dumps DB for recovery         | pg_dump               |
| **Apache Benchmark**| Simulates concurrent requests              | jordi/ab              |
| **Prometheus**      | Scrapes metrics from app                   | Prometheus            |
| **Grafana**         | Visualizes system metrics                  | Grafana               |
| **Metrics Parser**  | Processes AB results into readable insights| Python                |

## 📂 Project Structure
```bash

├── ab_results
│   ├── benchmark_20251026_081409.txt
│   └── benchmark_20251026_092558.txt
├── app
│   ├── database.py
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── backups
│   ├── backup_20251026_081358.sql
│   └── backup_20251026_092548.sql
├── docker-compose.yaml
├── dockerfile
├── LICENSE
├── loadtest
│   ├── lb_test.py
│   ├── requirements.txt
│   └── test.sh
├── monitoring
│   └── metrics_exporter.py
├── nginx.conf
├── prometheus.yml
├── README.md
├── requirements.txt
└── static
    └── favicon.ico

6 directories, 21 files
✔ ~/Dev/Experiments/fasta
```
## Run
#### Start all services with 3 replicas of api 
```bash
docker compose up -d --scale api=3
```
#### Access the system
```bash
http://localhost:8080
```
#### test the load balancer
```python
python3 lb_test.py
```
#### load balancer is working well
<img width="1303" height="318" alt="image" src="https://github.com/user-attachments/assets/c2536623-4464-402d-aed1-5f32a55b78f8" />
<img width="1286" height="162" alt="image" src="https://github.com/user-attachments/assets/81f03df3-d549-41f2-b6bf-123932d5b114" />

## Database Backups
Automated backups are taken hourly 
```
/backups/backup_YYYYMMDD_HHMMSS.sql
```
You can restore any snapshot using:
```
psql -U postgres -d books -f backup_<timestamp>.sql
```
## Observability stack
<img width="1327" height="965" alt="p01 drawio(4)" src="https://github.com/user-attachments/assets/6a947bb1-46ec-47a6-ba90-fbbf6ea7c2b0" />

#### Load Testing
Simulate 200 requests with concurrency of 20:
```
ab -n 200 -c 20 http://localhost:8080/
```
Requests are routed through the Nginx load balancer, which distributes them evenly across multiple api replicas.
Results are stored in ```ab_results/benchmark_<timestamp>.txt ```

#### Result Storage
Benchmark outputs are saved in:
```
ab_results/benchmark_<timestamp>.txt
```
These raw results capture latency, throughput, and error data for each test run.

#### Metrics Parsing
The metrics service periodically parses the raw benchmark files and generates a structured JSON summary:
```
ab_results/ab_summary.json
```
This transformation makes metrics machine-readable and ready for monitoring systems.

#### Metrics Exporter
The ``` ab_exporter``` container reads the parsed JSON summaries and exposes them as **Prometheus metrics** on port 9100.

#### Prometheus Integration
Prometheus scrapes data from the Metrics Exporter at regular intervals, building a time-series database of test results.

#### Visualization with Grafana
Grafana queries Prometheus to present real-time dashboards — including request rate, latency, and error metrics

<img width="1054" height="754" alt="image" src="https://github.com/user-attachments/assets/e01303a2-80fa-4d38-8f24-98de296d605b" />
