# Firewall API

A Python client library for interacting with firewall devices via their XML API.

## Installation

```bash
# Installation instructions (adjust as needed)
pip install -r requirements.txt
```

## Basic Usage

```python
from firewall_api.FirewallAPI import Firewall

# Initialize the connection
firewall = Firewall(
    username="admin",
    password="your_password",
    hostname="192.168.1.1"
)

# Use context manager for automatic session cleanup
with Firewall(username="admin", password="your_password", hostname="192.168.1.1") as firewall:
    # Your operations here
    response = firewall.read("FirewallRule")
    print(response)
```

## API Methods

### Constructor

```python
Firewall(
    username: str,
    password: str,
    hostname: str,
    port: int = 4444,
    certificate_verify: bool = False,
    password_encrypted: bool = False,
    timeout: int = 30
)
```

**Parameters:**
- `username` (str): Username for authentication
- `password` (str): Password for authentication
- `hostname` (str): Hostname or IP address of the firewall
- `port` (int, optional): Port number for the API. Default is 4444
- `certificate_verify` (bool, optional): Whether to verify SSL certificates. Default is False
- `password_encrypted` (bool, optional): Whether the password is already encrypted. Default is False
- `timeout` (int, optional): Request timeout in seconds. Default is 30

### Create

Creates a new entity in the firewall.

```python
create(entity: str, entity_data: Dict[str, Any]) -> ResponseType
```

**Parameters:**
- `entity` (str): The type of entity to create (e.g., "FirewallRule", "IPHost")
- `entity_data` (Dict[str, Any]): Dictionary containing the entity data

**Returns:**
- Dictionary with status, message, and data

**Example:**
```python
# Create a new firewall rule
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

### Read

Retrieves entities from the firewall, with optional filtering.

```python
read(
    entity: str, 
    filter_value: Optional[str] = None, 
    filter_criteria: str = LIKE, 
    filter_key_field: Optional[str] = None
) -> ResponseType
```

**Parameters:**
- `entity` (str): The type of entity to read (e.g., "FirewallRule", "IPHost")
- `filter_value` (str, optional): Value to filter by. Default is None (returns all entities)
- `filter_criteria` (str, optional): Filter criteria. Can be "=" (EQ), "!=" (NOT), or "like" (LIKE). Default is "like"
- `filter_key_field` (str, optional): Field to filter on. Default is "Name"

**Returns:**
- Dictionary with status, message, and data

**Example:**
```python
# Get all firewall rules
all_rules = firewall.read("FirewallRule")

# Get firewall rules with "DNAT" in the name
dnat_rules = firewall.read("FirewallRule", "DNAT", LIKE, "Name")

# Get IP hosts with a specific IP address
ip_hosts = firewall.read("IPHost", "172.16.17.2", LIKE, "IPAddress")
```

### Update

Updates an existing entity in the firewall.

```python
update(
    entity: str, 
    entity_data: Dict[str, Any], 
    entity_name: Optional[str] = None, 
    entity_name_key: str = "Name"
) -> ResponseType
```

**Parameters:**
- `entity` (str): The type of entity to update (e.g., "FirewallRule", "IPHost")
- `entity_data` (Dict[str, Any]): Dictionary containing the updated entity data
- `entity_name` (str, optional): Name of the entity to update. If None, uses the value from entity_data[entity_name_key]
- `entity_name_key` (str, optional): Key field to identify the entity. Default is "Name"

**Returns:**
- Dictionary with status, message, and data

**Example:**
```python
# Update a firewall rule to enable it and add source networks
updated_data = {
    "Status": "Enable",
    "NetworkPolicy": {
        "SourceNetworks": {"Network": ["192.168.30.0/24", "192.168.10.0/24"]},
    },
}
response = firewall.update("FirewallRule", updated_data, entity_name="Demo Rule")
```

### Delete

Deletes an entity from the firewall.

```python
delete(
    entity: str, 
    filter_value: str, 
    filter_criteria: str = EQ, 
    filter_key_field: Optional[str] = None
) -> ResponseType
```

**Parameters:**
- `entity` (str): The type of entity to delete (e.g., "FirewallRule", "IPHost")
- `filter_value` (str): Value to identify the entity to delete
- `filter_criteria` (str, optional): Filter criteria. Default is "=" (EQ)
- `filter_key_field` (str, optional): Field to filter on. Default is "Name"

**Returns:**
- Dictionary with status, message, and data

**Example:**
```python
# Delete a firewall rule by name
response = firewall.delete("FirewallRule", "Demo Rule")

# Delete an IP host with a specific name
response = firewall.delete("IPHost", "TestHost")
```

### Batch Operation

Performs multiple operations in a single batch.

```python
batch_operation(operations: List[Dict[str, Any]], debug: bool = False) -> List[ResponseType]
```

**Parameters:**
- `operations` (List[Dict[str, Any]]): List of operation dictionaries
- `debug` (bool, optional): Whether to print debug information. Default is False

**Returns:**
- List of response dictionaries

**Example:**
```python
# Perform multiple operations in a batch
operations = [
    {
        "action": "create",
        "entity": "IPHost",
        "entity_data": {
            "Name": "BatchHost1",
            "IPFamily": "IPv4",
            "HostType": "IP",
            "IPAddress": "192.168.1.10"
        }
    },
    {
        "action": "read",
        "entity": "FirewallRule",
        "filter_value": "DNAT"
    },
    {
        "action": "delete",
        "entity": "IPHost",
        "filter_value": "BatchHost1"
    }
]
results = firewall.batch_operation(operations, debug=True)
```

### Close

Closes the session with the firewall.

```python
close() -> ResponseType
```

**Returns:**
- Dictionary with status, message, and data

**Example:**
```python
# Close the session
response = firewall.close()
```

## Response Format

All methods return a response in the following format:

```python
{
    "status": str,  # HTTP-like status code as string
    "message": str,  # Status message
    "data": List[Dict[str, Any]]  # List of entity data dictionaries
}
```

Common status codes:
- "200": Success (general)
- "216": Operation successful with data
- "400": Bad request
- "401": Authentication failure
- "404": Entity not found
- "500": Server error
- "526": Record does not exist

## Constants

The module provides the following constants for filter criteria:
- `EQ`: Equals ("=")
- `NOT`: Not equals ("!=")
- `LIKE`: Like comparison ("like")

## Error Handling

```python
try:
    response = firewall.read("NonExistentEntity")
except Exception as e:
    print(f"Error: {str(e)}")
```

## Context Manager

The Firewall class supports the context manager protocol for automatic session cleanup:

```python
with Firewall(username="admin", password="password", hostname="192.168.1.1") as firewall:
    # Your operations here
    response = firewall.read("FirewallRule")
    # Session is automatically closed when exiting the with block
```

## Advanced Examples

### Loading Credentials from JSON

```python
import json

# Load credentials from a JSON file
with open("firewall_access.json", "r") as file:
    firewall_info = json.load(file)

# Initialize the firewall with loaded credentials
firewall = Firewall(
    username=firewall_info["username"],
    password=firewall_info["password"],
    hostname=firewall_info["firewall_ip"],
    port=firewall_info["port"],
    certificate_verify=False,
    password_encrypted=firewall_info["password_encrypted"]
)

# Test connection
print(f"Connection Test: {firewall.read('Login')}")
```

### Managing IP Hosts and Groups

```python
# Create an IP Host Group
prefix = "MSS_"
entity_type = "IPHostGroup"
ip_host_group_name = prefix + "IPHost_Group"
entity_data = {
    "Name": ip_host_group_name,
    "IPFamily": "IPv4",
    "Description": "Created by Firewall API",
}
response = firewall.create(entity_type, entity_data)
print(f"Create IP Host Group: {response}")

# Create an FQDN Host Group
entity_type = "FQDNHostGroup"
fqdn_group_name = prefix + "FQDN_Group"
entity_data = {
    "Name": fqdn_group_name,
    "IPFamily": "IPv4",
    "Description": "Created by Firewall API",
}
response = firewall.create(entity_type, entity_data)
print(f"Create FQDN Host Group: {response}")

# Search for IP Hosts with a specific name pattern
entity_name = "RW"
entity_type = "IPHost"
response = firewall.read(entity_type, entity_name, LIKE)
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03} : {item}")
```

### Creating Services

```python
# Create TCP/UDP services
service_data = {
    "Name": "Custom TCP/UDP Service",
    "Description": "Custom service created via API",
    "Type": "TCPorUDP",
    "ServiceDetails": {
        "ServiceDetail": [
            {"SourcePort": "1:65535", "DestinationPort": "8080", "Protocol": "TCP"},
            {"SourcePort": "1:65535", "DestinationPort": "8443", "Protocol": "TCP"},
            {"SourcePort": "1:65535", "DestinationPort": "53", "Protocol": "UDP"}
        ]
    }
}
response = firewall.create("Services", service_data)
print(f"Create Service: {response}")

# Create a service with a single port
single_port_service = {
    "Name": "Single Port Service",
    "Description": "Service with a single port",
    "Type": "TCPorUDP",
    "ServiceDetails": {
        "ServiceDetail": {
            "SourcePort": "1:65535", 
            "DestinationPort": "443", 
            "Protocol": "TCP"
        }
    }
}
response = firewall.create("Services", single_port_service)
print(f"Create Single Port Service: {response}")

# Create a service with port range
port_range_service = {
    "Name": "Port Range Service",
    "Description": "Service with a port range",
    "Type": "TCPorUDP",
    "ServiceDetails": {
        "ServiceDetail": {
            "SourcePort": "1:65535", 
            "DestinationPort": "1024:2048", 
            "Protocol": "TCP"
        }
    }
}
response = firewall.create("Services", port_range_service)
print(f"Create Port Range Service: {response}")
```

### Exporting Firewall Settings

```python
import os
import csv

# Create export directory if it doesn't exist
exports_path = "Exports/Firewall"
if not os.path.exists(exports_path):
    os.makedirs(exports_path)

# Export firewall rules to CSV
rules = firewall.read("FirewallRule")["data"]
if rules:
    with open(f"{exports_path}/firewall_rules.csv", "w", newline="") as csvfile:
        # Extract field names from the first rule
        fieldnames = list(rules[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for rule in rules:
            writer.writerow(rule)
    print(f"Exported {len(rules)} firewall rules to {exports_path}/firewall_rules.csv")
```

### Helper Functions for Common Operations

```python
def create_entity(firewall, entity_type, entity_data, print_data=False, print_result=False):
    """
    Create and log an entity.
    
    :param firewall: Firewall instance
    :param entity_type: The type of entity to create
    :param entity_data: The data for the entity to create
    :param print_data: Boolean to print the data being sent (default is False)
    :param print_result: Boolean to print the result of the operation (default is False)
    :return: The response from the create operation
    """
    if print_data:
        print(f"Creating {entity_type} with data: {entity_data}")
    response = firewall.create(entity_type, entity_data)
    if print_result:
        print(f"CREATE :: {response}\n")
    return response

def update_entity(firewall, entity_type, entity_data, print_data=False, print_result=False):
    """
    Update and log an entity.
    
    :param firewall: Firewall instance
    :param entity_type: The type of entity to update
    :param entity_data: The data for the entity to update
    :param print_data: Boolean to print the data being sent (default is False)
    :param print_result: Boolean to print the result of the operation (default is False)
    :return: The response from the update operation
    """
    if print_data:
        print(f"Updating {entity_type} with data: {entity_data}")
    response = firewall.update(entity_type, entity_data)
    if print_result:
        print(f"UPDATE :: {response}\n")
    return response

def read_entity(firewall, entity_type, filter_value=None, filter_selector=LIKE, filter_key=None, print_result=False):
    """
    Read and log an entity.
    
    :param firewall: Firewall instance
    :param entity_type: The type of entity to read
    :param filter_value: Value to filter by (default is None)
    :param filter_selector: Filter criteria (default is LIKE)
    :param filter_key: Field to filter on (default is None)
    :param print_result: Boolean to print the result of the operation (default is False)
    :return: The response from the read operation
    """
    response = firewall.read(entity_type, filter_value, filter_selector, filter_key)
    if print_result:
        print(f"READ :: {response}\n")
    return response

# Example usage of helper functions
ip_host_data = {
    "Name": "TestHost",
    "IPFamily": "IPv4",
    "HostType": "IP",
    "IPAddress": "192.168.1.100"
}
create_entity(firewall, "IPHost", ip_host_data, print_result=True)