import boto3
import datetime
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# 🔧 CONFIG
REGION = 'us-east-1'  # update with your AWS region
INSTANCE_ID = 'i-056250a7e38a6d0a7'  # update with your EC2 instance ID
PUSHGATEWAY_URL = 'http://localhost:9091/'  # update with Pushgateway address

# Create CloudWatch client

cloudwatch = boto3.client('cloudwatch', region_name=REGION)

# Time window for metric query
end_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
start_time = end_time - datetime.timedelta(minutes=15)


# Pull CPU utilization
print(f"Querying CloudWatch from {start_time.isoformat()} to {end_time.isoformat()}")

response = cloudwatch.get_metric_statistics(
    Namespace='AWS/EC2',
    MetricName='CPUUtilization',
    Dimensions=[{'Name': 'InstanceId', 'Value': INSTANCE_ID}],
    StartTime=start_time,
    EndTime=end_time,
    Period=300,  # 5-minute buckets
    Statistics=['Average'],
    Unit='Percent'
)

# Set up Prometheus metric
registry = CollectorRegistry()
cpu_gauge = Gauge('aws_ec2_cpu_utilization', 'Average CPU utilization (%)',
                  ['instance_id'], registry=registry)

# Parse and push metric
datapoints = response.get('Datapoints', [])
#print("CloudWatch raw response:")
#print(response)
if datapoints:
    latest = sorted(datapoints, key=lambda x: x['Timestamp'])[-1]
    value = latest['Average']
    print(f"CPU for {INSTANCE_ID}: {value:.2f}%")
    cpu_gauge.labels(instance_id=INSTANCE_ID).set(value)

    push_to_gateway(PUSHGATEWAY_URL, job='aws_ec2_metrics', registry=registry)
    print("✅ Pushed to Prometheus")
else:
    print("⚠️ No datapoints returned by CloudWatch")

