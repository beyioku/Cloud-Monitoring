# Cloud Monitoring Project

This project implements a multi-cloud monitoring system across AWS and Azure using:
- Python for cloud metric collectors
- Prometheus and Pushgateway for metric ingestion
- Grafana for visualization

## Architecture

Each cloud VM runs a dedicated Python script to collect metrics from its native environment:
- `aws_collector.py` runs on the AWS VM
- `azure_collector.py` runs on the Azure VM

## Setup Instructions

1. Clone this repo
2. Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3. Edit collector scripts with correct instance IDs and Pushgateway address
4. Deploy to respective cloud VMs

