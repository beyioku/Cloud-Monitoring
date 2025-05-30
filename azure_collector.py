import datetime
from azure.identity import DefaultAzureCredential
from azure.monitor.query import MetricsQueryClient
from azure.monitor.query import MetricAggregationType
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Azure CONFIGURATION
SUBSCRIPTION_ID = "5790d298-ecc9-4815-8d90-5b1270bd3bf6"
RESOURCE_GROUP = "centralized-cloud-monitoring"
VM_NAME = "azure-monitoring-vm"
PUSHGATEWAY_URL = "http://localhost:9091"
LOCATION = "East US (Zone 1)"  # or whatever region your VM is in

# Format the full resource ID for the VM
RESOURCE_ID = (
    f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/{RESOURCE_GROUP}"
    f"/providers/Microsoft.Compute/virtualMachines/{VM_NAME}"
)
def main():
    # Time window
    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(minutes=15)

    print(f"\nCurrently Querying Azure Monitor from {start_time.isoformat()} to {end_time.isoformat()}")

    # Authentication and client
    credential = DefaultAzureCredential()
    client = MetricsQueryClient(credential)

    # Creating a Prometheus Registry
    registry = CollectorRegistry()

    # ..........CPU Utilization..........
    print("\n Currently collecting CPU percentage...")

    try:
        response = client.query_resource(
            resource_uri=RESOURCE_ID,
            metric_names=["Percentage CPU"],
            timespan=(start_time, end_time),
            granularity=datetime.timedelta(minutes=5),
            aggregations=[MetricAggregationType.AVERAGE]
        )

        datapoints = response.metrics[0].timeseries[0].data
        if datapoints:
            latest = sorted(datapoints, key=lambda x: x.timestamp)[-1]
            value = latest.average
            print(f"CPU: {value:.2f}%")
            cpu_gauge = Gauge("azure_vm_cpu_utilization", "CPU utilization (%)",
                              ["vm_name", "cloud_provider"], registry=registry)
            cpu_gauge.labels(vm_name=VM_NAME, cloud_provider="azure").set(value)
        else:
            print("⚠️ No datapoints returned for CPU")
    except Exception as e:
        print(f"❌ Error collecting CPU: {e}")

    # ..........Network IN..........
    print("\n Currently collecting Network in Total...")
    try:
        response = client.query_resource(
            resource_uri=RESOURCE_ID,
            metric_names=["Network in Total"],
            timespan=(start_time, end_time),
            granularity=datetime.timedelta(minutes=5),
            aggregations=[MetricAggregationType.AVERAGE]
        )

        datapoints = response.metrics[0].timeseries[0].data
        if datapoints:
            latest = sorted(datapoints, key=lambda x: x.timestamp)[-1]
            value = latest.average
            print(f"Network In: {value:.2f} Bytes")
            net_in_gauge = Gauge("azure_vm_network_in", "Network In (Bytes)",
                              ["vm_name", "cloud_provider"], registry=registry)
            net_in_gauge.labels(vm_name=VM_NAME, cloud_provider="azure").set(value)
        else:
            print("⚠️ No datapoints returned for Network In")
    except Exception as e:
        print(f"❌ Error collecting Network In: {e}")

    # ..........Network Out..........
    print("\n Currently collecting Network Out Total...")
    try:
        response = client.query_resource(
            resource_uri=RESOURCE_ID,
            metric_names=["Network Out Total"],
            timespan=(start_time, end_time),
            granularity=datetime.timedelta(minutes=5),
            aggregations=[MetricAggregationType.AVERAGE]
        )

        datapoints = response.metrics[0].timeseries[0].data
        if datapoints:
            latest = sorted(datapoints, key=lambda x: x.timestamp)[-1]
            value = latest.average
            print(f"Network Out: {value:.2f} Bytes")
            net_out_gauge = Gauge("azure_vm_network_out", "Network Out (Bytes)",
                              ["vm_name", "cloud_provider"], registry=registry)
            net_out_gauge.labels(vm_name=VM_NAME, cloud_provider="azure").set(value)
        else:
            print("⚠️ No datapoints returned for Network Out")
    except Exception as e:
        print(f"❌ Error collecting Network Out: {e}")

    # ..........Disk Read Bytes..........
    print("\n Currently collecting Disk Read Bytes...")
    try:
        response = client.query_resource(
            resource_uri=RESOURCE_ID,
            metric_names=["Disk Read Bytes"],
            timespan=(start_time, end_time),
            granularity=datetime.timedelta(minutes=5),
            aggregations=[MetricAggregationType.AVERAGE]
        )

        datapoints = response.metrics[0].timeseries[0].data
        if datapoints:
            latest = sorted(datapoints, key=lambda x: x.timestamp)[-1]
            value = latest.average
            print(f"Disk Read: {value:.2f} Bytes")
            disk_read_gauge = Gauge("azure_vm_disk_read_bytes", "Disk Read (Bytes)",
                                  ["vm_name", "cloud_provider"], registry=registry)
            disk_read_gauge.labels(vm_name=VM_NAME, cloud_provider="azure").set(value)
        else:
            print("⚠️ No datapoints returned for Disk Read Bytes")
    except Exception as e:
        print(f"❌ Error collecting Disk Read Bytes: {e}")

    # ..........Disk Write Bytes..........
    print("\n Currently collecting Disk Write Bytes...")
    try:
        response = client.query_resource(
            resource_uri=RESOURCE_ID,
            metric_names=["Disk Write Bytes"],
            timespan=(start_time, end_time),
            granularity=datetime.timedelta(minutes=5),
            aggregations=[MetricAggregationType.AVERAGE]
        )

        datapoints = response.metrics[0].timeseries[0].data
        if datapoints:
            latest = sorted(datapoints, key=lambda x: x.timestamp)[-1]
            value = latest.average
            print(f"Disk Write: {value:.2f} Bytes")
            disk_write_gauge = Gauge("azure_vm_disk_write_bytes", "Disk Write (Bytes)",
                                    ["vm_name", "cloud_provider"], registry=registry)
            disk_write_gauge.labels(vm_name=VM_NAME, cloud_provider="azure").set(value)
        else:
            print("⚠️ No datapoints returned for Disk Write Bytes")
    except Exception as e:
        print(f"❌ Error collecting Disk Write Bytes: {e}")

    # PUSHING TO PROMETHEUS
    try:
        push_to_gateway(PUSHGATEWAY_URL, job="azure_vm_metrics", registry=registry)
        print("\n✅ All Azure metrics have been pushed to Prometheus")
    except Exception as e:
        print(f"\n❌ Failed to push to Prometheus: {e}")

if __name__ == "__main__":
    main()