# Firewall API Examples

This document provides comprehensive examples of how to use the Firewall API for various operations.

## Table of Contents

- [Basic Usage](#basic-usage)
- [CRUD Operations](#crud-operations)
  - [Create](#create)
  - [Read](#read)
  - [Update](#update)
  - [Delete](#delete)
- [Batch Operations](#batch-operations)
- [IP Address Management](#ip-address-management)
  - [IPHost](#iphost)
  - [FQDNHostGroup](#fqdnhostgroup)
- [Services Management](#services-management)
- [Firewall Rules](#firewall-rules)
- [Export Settings](#export-settings)
- [Brute Force Protection](#brute-force-protection)

## Basic Usage

Initialize the Firewall API client:

```python
from firewall_api.FirewallAPI import Firewall

# Initialize the client
firewall = Firewall(
    username="admin",
    password="password",
    hostname="firewall.example.com",
    port=4444,
    certificate_verify=False  # Set to True in production
)

# Use as a context manager (recommended)
with Firewall(username="admin", password="password", hostname="firewall.example.com") as fw:
    # Perform operations
    result = fw.read("Services", "HTTP")
    print(result)
```

## CRUD Operations

### Create

Create a new service:

```python
service_data = {
    "Name": "CustomHTTP",
    "Type": "TCP",
    "DestinationPort": "8080"
}
result = firewall.create("Services", service_data)
print("Create result:", result)
```

### Read

Read all services:

```python
all_services = firewall.read("Services")
print("All services:", all_services)
```

Read with filter:

```python
# Read FirewallRule with name containing "DNAT"
response = firewall.read("FirewallRule", "DNAT", LIKE, "Name")

# Read IPHost with specific IP address
response = firewall.read("IPHost", "172.16.17.2", LIKE, "IPAddress")
```

### Update

Update an existing service:

```python
updated_data = {
    "Name": "CustomHTTP",
    "DestinationPort": "9090"  # Only updating the port
}
result = firewall.update("Services", updated_data)
print("Update result:", result)
```

Update a firewall rule:

```python
updated_data = {
    "Status": "Enable",
    "NetworkPolicy": {
        "Action": "Accept",
        "SourceNetworks": {
            "Network": ["192.168.30.0/24", "192.168.10.0/24"]
        },
    },
}
response = firewall.update("FirewallRule", updated_data, entity_name="Demo Rule")
```

### Delete

Delete a service:

```python
result = firewall.delete("Services", "CustomHTTP")
print("Delete result:", result)
```

## Batch Operations

Perform multiple operations in a single batch:

```python
operations = [
    {
        "action": "create",
        "entity": "Services",
        "entity_data": {
            "Name": "Service1",
            "Type": "TCP",
            "DestinationPort": "8080"
        }
    },
    {
        "action": "read",
        "entity": "Services",
        "filter_value": "HTTP"
    },
    {
        "action": "update",
        "entity": "Services",
        "entity_data": {
            "Name": "HTTP",
            "DestinationPort": "8080"
        }
    }
]

results = firewall.batch_operation(operations, debug=True)
print("Batch operation results:", results)
```

## IP Address Management

### IPHost

Create, read, update, and delete an IPHost:

```python
entity_type = "IPHost"
entity_name = "TEST"
entity_data = {
    "Name": entity_name,
    # "IPFamily": "IPv4",   #IPv4 is Default settings
    "HostType": "IP",
    "IPAddress": "172.16.17.100",
}
print("CREATE :: ", firewall.create(entity_type, entity_data))
print("READ   :: ", firewall.read(entity_type, entity_name))
print("UPDATE :: ", firewall.update(entity_type, {"Name": entity_name, "HostType": "IP", "IPAddress": "172.16.17.222"}))
print("READ   :: ", firewall.read(entity_type, entity_name))
print("DELETE :: ", firewall.delete(entity_type, entity_name))
```

### FQDNHostGroup

Create and read a FQDNHostGroup:

```python
entity_type = "FQDNHostGroup"
entity_name = "TEST FQDNHostGroup"
entity_data = {
    "Name": entity_name,
    # "Description": "TEST FQDNHostGroup",
    # "FQDNHostList": {"FQDNHost": []},
}

print("CREATE :: ", firewall.create(entity_type, entity_data))
print("READ   :: ", firewall.read(entity_type, entity_name))
```

## Services Management

Create TCP/UDP services:

```python
data = [
    {
        "Name": "test service TCP/UDP",
        "Description": "None",
        "Type": "TCPorUDP",
        "ServiceDetails": {
            "ServiceDetail": [
                {"SourcePort": "1: 65535", "DestinationPort": "1", "Protocol": "TCP"},
                {"SourcePort": "1: 65535", "DestinationPort": "1", "Protocol": "UDP"},
                {"SourcePort": "1: 65535", "DestinationPort": "2", "Protocol": "TCP"},
                {"SourcePort": "1: 65535", "DestinationPort": "2", "Protocol": "UDP"},
            ]
        },
    },
    {
        "Name": "test service TCP/UDP one",
        "Description": "None",
        "Type": "TCPorUDP",
        "ServiceDetails": {"ServiceDetail": {"SourcePort": "1:65535", "DestinationPort": "1", "Protocol": "TCP"}},
    },
    {
        "Name": "test service TCP/UDP one range",
        "Description": "None",
        "Type": "TCPorUDP",
        "ServiceDetails": {"ServiceDetail": {"SourcePort": "1: 65535", "DestinationPort": "1: 123", "Protocol": "TCP"}},
    }
]

for item in data:
    print(firewall.create("Services", item))
```

## Firewall Rules

Create a firewall rule:

```python
entity_data = {
    "Name": "Demo Rule",
    "Status": "Disable",
    "Position": "Top",
    "PolicyType": "Network",
    "NetworkPolicy": {
        "Action": "Accept",
        "SourceZones": {"Zone": ["LAN"]},
        "DestinationZones": {"Zone": ["WAN"]},
    },
}
response = firewall.create("FirewallRule", entity_data)
```

## Export Settings

Export firewall settings:

```python
import os
import csv
import sys
from firewall_api import Firewall, LIKE, EQ, NOT

# Filter responses to extract specific fields
def filter_responses(responses, requested_fields):
    def extract_fields(data, fields):
        if isinstance(data, dict):
            result = {}
            for field in fields:
                keys = field.split(".")
                value = data
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        value = None
                        break
                if value is not None:
                    result[keys[-1]] = value
            return result
        return {}

    filtered_responses_list = [extract_fields(item, requested_fields) for item in responses]
    return filtered_responses_list

# Setup export directory
customer_name = "GW LAB"
exports_path = "Exports\\" + customer_name
if not os.path.exists(exports_path):
    os.makedirs(exports_path)

# Initialize firewall connection
firewall = Firewall(username, password, hostname, port, certificate_verify=False, password_encrypted=True)

# Export data
response = firewall.read("Interface")
# Process and save the data as needed
```

## Brute Force Protection

Implement brute force protection:

```python
import os
import sys
from firewall_api.FirewallAPI import Firewall, LIKE, EQ, NOT
import json
import ipaddress
import csv

# Helper functions for entity operations
def create_entity(firewall, entity_type, entity_data, print_data=False, print_result=False):
    if print_data:
        print(f"Creating {entity_type} with data: {entity_data}")
    response = firewall.create(entity_type, entity_data)
    if print_result:
        print(f"CREATE :: {response}\n")
    return response

def update_entity(firewall, entity_type, entity_data, print_data=False, print_result=False):
    if print_data:
        print(f"Updating {entity_type} with data: {entity_data}")
    response = firewall.update(entity_type, entity_data)
    if print_result:
        print(f"UPDATE :: {response}\n")
    return response

def read_entity(firewall, entity_type, filter_value=None, filter_selector=LIKE, filter_key=None, print_data=False, print_result=False):
    response = firewall.read(entity_type, filter_value, filter_selector, filter_key)
    if print_result:
        print(f"READ :: {response}\n")
    return response

# Initialize firewall connection
firewall = Firewall(username, password, hostname, port, certificate_verify=False, password_encrypted=True)

# Implement brute force protection rules
# (Specific implementation depends on your requirements)
```

## Additional Notes

- Always close the firewall connection when done (automatically handled when using context manager)
- Set `certificate_verify=True` in production environments
- Use encrypted passwords when possible by setting `password_encrypted=True`
- For batch operations, set `debug=True` to get detailed information about each operation 