# Firewall API Client Library

A Python client library for managing firewall configurations through a secure XML API interface. This library provides a comprehensive set of operations for managing firewall rules, IP addresses, services, and other firewall entities.

## Features

- Secure HTTPS communication with firewalls
- Comprehensive CRUD operations (Create, Read, Update, Delete)
- SSL/TLS certificate handling
- Input validation and error handling
- Context manager support for automatic session cleanup

## Installation

```bash
pip install -r requirements.txt
```

Required dependencies:
- requests
- xmltodict
- urllib3

## Basic Usage

```python
from firewall_api import Firewall, LIKE, NOT, EQ

# Initialize the connection
firewall = Firewall(
    username="admin",
    password="your_password",
    hostname="firewall.example.com",
    port=4444,
    certificate_verify=False,  # Set to True in production
    timeout=30
)

# Using context manager (recommended)
with Firewall(username="admin",password="your_password",hostname="firewall.example.com") as fw:
    # Read all firewall rules
    response = fw.read("FirewallRule")
    print(response)
```

## API Reference

### Constructor

```python
Firewall(
    username: str,
    password: str,
    hostname: str,
    port: int = 4444,
    certificate_verify: bool = True,
    timeout: int = 30,
    max_retries: int = 3,
    retry_backoff: float = 0.5
)
```

### Methods

#### Create
```python
create(entity: str, entity_data: dict) -> dict
```
Creates a new entity in the firewall.

```python
# Example: Create an IP host
ip_data = {
    "Name": "TestHost",
    "IPFamily": "IPv4",
    "HostType": "IP",
    "IPAddress": "192.168.1.100"
}
response = firewall.create("IPHost", ip_data)
```

#### Read
```python
read(
    entity: str,
    filter_value: str = None,
    filter_criteria: str = LIKE,
    filter_key_field: str = None
) -> dict
```
Retrieves entities from the firewall with optional filtering.

```python
# Example: Read all firewall rules containing "DNAT"
response = firewall.read("FirewallRule", "DNAT", LIKE)
```

#### Update
```python
update(
    entity: str,
    entity_data: dict,
    entity_name: str = None,
    entity_name_key: str = "Name"
) -> dict
```
Updates an existing entity in the firewall.

```python
# Example: Update a firewall rule
update_data = {
    "Name": "ExistingRule",
    "Status": "Enable"
}
response = firewall.update("FirewallRule", update_data)
```

#### Delete
```python
delete(
    entity: str,
    filter_value: str,
    filter_criteria: str = EQ,
    filter_key_field: str = None
) -> dict
```
Deletes an entity from the firewall.

```python
# Example: Delete an IP host
response = firewall.delete("IPHost", "TestHost")
```

### Filter Constants

- `EQ`: Exact match (=)
- `NOT`: Not equal (!=)
- `LIKE`: Partial match (like)

## Response Format

All operations return a dictionary with the following structure:
```python
{
    "status": str,    # HTTP-like status code
    "message": str,   # Human-readable message
    "data": list     # List of results (if any)
}
```

Common status codes:
- "200": Success
- "216": Operation successful with data
- "400": Bad request
- "401": Authentication failure
- "404": Not found
- "495": SSL/TLS error
- "500": Server error
- "503": Connection error
- "504": Timeout
- "526": No matching records

## Security Considerations

1. Always use HTTPS (enforced by the library)
2. Enable certificate verification in production environments
3. Use appropriate timeout values
4. Implement proper error handling
5. Store credentials securely
6. Use context managers to ensure proper session cleanup

## License

This project is licensed under the MIT License.