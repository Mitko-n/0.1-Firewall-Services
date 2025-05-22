# Firewall API Client

A Python client for interacting with firewall systems through their API.

## Overview

This library provides a simple interface to interact with firewall systems, allowing you to:

- Create, read, update, and delete firewall entities
- Perform batch operations
- Handle authentication and session management

## Installation

```bash
pip install -r requirements.txt
```

## Requirements

- Python 3.6+
- requests
- xmltodict

## Usage

### Basic Usage

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

### CRUD Operations

#### Create an Entity

```python
# Create a service
service_data = {
    "Name": "CustomHTTP",
    "Type": "TCP",
    "DestinationPort": "8080"
}
result = firewall.create("Services", service_data)
```

#### Read Entities

```python
# Read all services
all_services = firewall.read("Services")

# Read a specific service
http_service = firewall.read("Services", "HTTP", filter_criteria="=")

# Use different filter criteria
custom_services = firewall.read("Services", "Custom", filter_criteria="like")
```

#### Update an Entity

```python
# Update a service
updated_data = {
    "Name": "CustomHTTP",
    "DestinationPort": "9090"  # Only updating the port
}
result = firewall.update("Services", updated_data)
```

#### Delete an Entity

```python
# Delete a service
result = firewall.delete("Services", "CustomHTTP")
```

### Batch Operations

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
```

## Response Format

All methods return a response in the following format:

```python
{
    "status": "216",  # Status code
    "message": "Operation Successful.",  # Status message
    "data": [...]  # List of entity data dictionaries
}
```

Common status codes:
- 216: Operation successful
- 400: Bad request
- 401: Authentication failure
- 404: Entity not found
- 500: Server error
- 526: Record does not exist

## Error Handling

```python
result = firewall.read("Services", "NonExistentService")
if result["status"] != "216":
    print(f"Error: {result['message']}")
else:
    services = result["data"]
    # Process services
```

## Closing the Connection

When not using the context manager, always close the connection when done:

```python
firewall.close()
```

## Constants

The library provides constants for filter criteria:
- `EQ` (=): Exact match
- `NOT` (!=): Not equal
- `LIKE` (like): Partial match

## Notes

- Set `certificate_verify=True` in production environments
- For security, consider using `password_encrypted=True` if your firewall supports it 


## How to Use

1. Use `read()` to identify all necessary entity_data.
2. Next, use `create()`, `update()` to create or update entity.
3. Use `delete()` to delete entity by `"Name"`. It is possiblr to delete more that one entity using `LIKE` filter.