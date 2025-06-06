# Firewall API Client

A Python client library for interacting with Sophos Firewall devices via their XML API. This library provides a simple and intuitive interface for managing firewall configurations, rules, services, and more.

## Features

- Simple and intuitive API for firewall management
- Support for CRUD operations on firewall entities
- Automatic session management with context manager
- SSL certificate verification options
- Comprehensive error handling
- Detailed logging capabilities

## Requirements

- Python 3.7 or higher
- Network access to the firewall device
- Valid credentials for the firewall API

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/firewall-api.git
cd firewall-api

# Install dependencies
pip install -r requirements.txt
```

## Basic Usage Examples

### Initialize Connection

```python
from firewall_api import Firewall

# Basic initialization
firewall = Firewall(
    username="admin",
    password="your_password",
    hostname="192.168.1.1",
    port=4444,
    certificate_verify=False
)

# Using context manager (recommended)
with Firewall(
    username="admin",
    password="your_password",
    hostname="192.168.1.1"
) as fw:
    # Your operations here
    pass
```

### Create Operations

```python
# Create a new IP Host
ip_host = {
    "Name": "Server1",
    "IPFamily": "IPv4",
    "HostType": "IP",
    "IPAddress": "192.168.1.100"
}
response = firewall.create("IPHost", ip_host)

# Create a new service
service = {
    "Name": "Custom_HTTP",
    "Type": "TCP",
    "Port": "8080"
}
response = firewall.create("Services", service)

# Create a firewall rule
rule = {
    "Name": "Allow_Web",
    "Status": "Enable",
    "Position": "Top",
    "PolicyType": "Network",
    "NetworkPolicy": {
        "Action": "Accept",
        "SourceZones": {"Zone": ["LAN"]},
        "DestinationZones": {"Zone": ["WAN"]},
        "Services": {"Service": ["HTTP", "HTTPS"]}
    }
}
response = firewall.create("FirewallRule", rule)
```

### Read Operations

```python
# Get all firewall rules
rules = firewall.read("FirewallRule")

# Get specific IP host
host = firewall.read("IPHost", "Server1", EQ)

# Search services containing "HTTP"
services = firewall.read("Services", "HTTP", LIKE)

# Get IP hosts with specific IP address
ip_hosts = firewall.read("IPHost", "192.168", LIKE, "IPAddress")
```

### Update Operations

```python
# Update an IP host
update_host = {
    "Name": "Server1",
    "IPAddress": "192.168.1.200"
}
response = firewall.update("IPHost", update_host)

# Enable a firewall rule
update_rule = {
    "Name": "Allow_Web",
    "Status": "Enable"
}
response = firewall.update("FirewallRule", update_rule)
```

### Delete Operations

```python
# Delete an IP host
response = firewall.delete("IPHost", "Server1")

# Delete a firewall rule (special case)
response = firewall.delete("FirewallRule", "Allow_Web")

# Delete all services containing "Custom"
response = firewall.delete("Services", "Custom", LIKE)

# Delete all IP hosts with IP addresses starting with "192.168"
response = firewall.delete("IPHost", "192.168", LIKE, "IPAddress")
```

## Error Handling

```python
try:
    with Firewall(
        username="admin",
        password="password",
        hostname="192.168.1.1",
        certificate_verify=False
    ) as fw:
        response = fw.create("IPHost", ip_host)
        if response["status"] != "216":
            print(f"Operation failed: {response['message']}")
except ValueError as e:
    print(f"Invalid parameters: {e}")
except Exception as e:
    print(f"Connection failed: {e}")
```

## Response Format

All operations return a dictionary with the following structure:

```python
{
    "status": str,      # Status code ("216" for success)
    "message": str,     # Human-readable message
    "data": list       # List of entities or empty list
}
```

Common status codes:
- "216": Success
- "400": Bad request
- "401": Authentication failure
- "404": Resource not found
- "495": SSL certificate error
- "503": Service unavailable
- "504": Timeout

## Security Notes

1. SSL Certificate Verification:
   ```python
   # For production (recommended)
   firewall = Firewall(..., certificate_verify=True)
   
   # For testing/self-signed certificates
   firewall = Firewall(..., certificate_verify=False)
   ```

2. Always use context managers for proper session cleanup:
   ```python
   with Firewall(...) as fw:
       # Your code here
       pass  # Session automatically closed
   ```

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.