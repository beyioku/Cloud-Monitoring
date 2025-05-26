import boto3
import datetime
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# 🔧 CONFIG
REGION = 'us-east-1'  # My current AWS region
INSTANCE_ID = 'i-056250a7e38a6d0a7'  # update with your EC2 instance ID
VOLUME_ID = 'vol-0e331fe5df83e4803'    # my EBS volume ID
PUSHGATEWAY_URL = 'http://localhost:9091/'  # update with Pushgateway address


def main():
    # Create CloudWatch client
    cloudwatch = boto3.client('cloudwatch', region_name=REGION)

    # Time window for metric query
    end_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
    start_time = end_time - datetime.timedelta(minutes=15)
    print(f"Querying CloudWatch from {start_time.isoformat()} to {end_time.isoformat()}")


    # Setting Up Prometheus metric Registry
    registry = CollectorRegistry()


    #................CPU utilization Block................
    print("\n Currently Collecting CPUUtilization....")
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': INSTANCE_ID}],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,  # Set at 5-minute buckets
        Statistics=['Average'],
        Unit='Percent'
    )

    datapoints = response.get('Datapoints', [])

    if datapoints:
        latest = sorted(datapoints, key=lambda x: x['Timestamp'])[-1]
        value = latest['Average']
        cpu_gauge = Gauge('aws_ec2_cpu_utilization', 'Average CPU utilization (%)',
                          ['instance_id'], registry=registry)
        cpu_gauge.labels(instance_id=INSTANCE_ID).set(value)
        print(f"CPUUtilization: {value:.2f}%")
    else:
        print(f" ⚠️ No datapoints returned for CPUUtilization")

    #................Network Metric Block................
    print("\n Currently Collecting NetworkIn and NetworkOut....")
    for metric_name in ['NetworkIn', 'NetworkOut']:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName=metric_name,
            Dimensions=[{'Name': 'InstanceId', 'Value': INSTANCE_ID}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=['Average'],
            Unit='Bytes'
        )

        datapoints = response.get('Datapoints', [])
        if datapoints:
            latest = sorted(datapoints, key=lambda x: x['Timestamp'])[-1]
            value = latest['Average']
            net_gauge = Gauge(f'aws_ec2_{metric_name.lower()}', f'Average {metric_name} (Bytes)',
                              ['instance_id'], registry=registry)
            net_gauge.labels(instance_id=INSTANCE_ID).set(value)
            print(f"{metric_name}: {value:.2f} Bytes")
        else:
            print(f"⚠️ No datapoints returned for {metric_name} ")

    # ................Volume Read bytes................
    print("\n Currently Collecting VolumeReadBytes....")
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EBS',
        MetricName='VolumeReadBytes',
        Dimensions=[{'Name': 'VolumeId', 'Value': VOLUME_ID}],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=['Average'],
        Unit='Bytes'
    )
    datapoints = response.get('Datapoints', [])
    if datapoints:
        latest = sorted(datapoints, key=lambda x: x['Timestamp'])[-1]
        value = latest['Average']
        print(f"📥 VolumeReadBytes: {value:.2f} Bytes")

        read_gauge = Gauge('aws_ebs_volumereadbytes', 'Avg EBS Volume Read (Bytes)', ['volume_id'], registry=registry)
        read_gauge.labels(volume_id=VOLUME_ID).set(value)

        push_to_gateway(PUSHGATEWAY_URL, job='aws_ebs_metrics', registry=registry)
        print("✅ Pushed VolumeReadBytes to Prometheus")
    else:
        print("⚠️ No datapoints returned for VolumeReadBytes")


    # ................Volume Write bytes................
    print("\n Currently Collecting VolumeWriteBytes....")
    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EBS',
        MetricName='VolumeWriteBytes',
        Dimensions=[{'Name': 'VolumeId', 'Value': VOLUME_ID}],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=['Average'],
        Unit='Bytes'
    )
    datapoints = response.get('Datapoints', [])
    if datapoints:
        latest = sorted(datapoints, key=lambda x: x['Timestamp'])[-1]
        value = latest['Average']
        print(f"📥 VolumeWriteBytes: {value:.2f} Bytes")

        read_gauge = Gauge('aws_ebs_volumewritebytes', 'Avg EBS Volume Write (Bytes)', ['volume_id'], registry=registry)
        read_gauge.labels(volume_id=VOLUME_ID).set(value)

        push_to_gateway(PUSHGATEWAY_URL, job='aws_ebs_metrics', registry=registry)
        print("✅ Pushed VolumeWriteBytes to Prometheus")
    else:
        print("⚠️ No datapoints returned for VolumeWriteBytes")




    """     
    # ................Disk I/O Block................
    print("\n Currently Collecting DiskReadBytes and DiskWriteBytes.. ")
    for metric_name in ['DiskReadBytes', 'DiskWriteBytes']:
        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName=metric_name,
            Dimensions=[{'Name': 'InstanceId', 'Value': INSTANCE_ID}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=['Average'],
            Unit='Bytes'
        )
        datapoints = response.get('Datapoints', [])
        if datapoints:
            latest = sorted(datapoints, key=lambda x: x['Timestamp'])[-1]
            value = latest['Average']
            disk_gauge = Gauge(f'aws_ec2_{metric_name.lower()}', f'Average {metric_name} (Bytes)',
                               ['instance_id'], registry=registry)
            disk_gauge.labels(instance_id=INSTANCE_ID).set(value)
            print(f"{metric_name}: {value:.2f} Bytes")
        else:
            print(f" No datapoints returned for {metric_name}")
            
    """



    push_to_gateway(PUSHGATEWAY_URL, job='aws_ec2_metrics', registry=registry)
    print("✅ All metrics Pushed to the Prometheus Pushgateway")

if __name__ == "__main__":
    main()