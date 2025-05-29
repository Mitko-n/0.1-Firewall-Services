# Firewall API

A Python client library for interacting with firewall devices via their XML API. This library provides a simple and intuitive interface for managing firewall configurations, rules, services, and more.

## Features

- Simple and intuitive API for firewall management
- Support for CRUD operations on firewall entities
- Automatic session management with context manager
- Configurable retry mechanism for failed requests
- SSL certificate verification options
- Comprehensive error handling
- Detailed logging capabilities

## Requirements

- Python 3.7 or higher
- Network access to the firewall device
- Valid credentials for the firewall API

## Installation

### Using pip

```bash

# Install from source
git clone https://github.com/yourusername/firewall-api.git
cd firewall-api
pip install -e .
```

### Using requirements.txt

```bash
# Clone the repository
git clone https://github.com/yourusername/firewall-api.git
cd firewall-api

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in your project root with the following variables:

```env
FIREWALL_USERNAME=admin
FIREWALL_PASSWORD=your_password
FIREWALL_HOSTNAME=192.168.1.1
FIREWALL_PORT=4444
FIREWALL_CERTIFICATE_VERIFY=False
FIREWALL_TIMEOUT=30
FIREWALL_MAX_RETRIES=3
FIREWALL_RETRY_BACKOFF=0.5
```

## Basic Usage

```python
from firewall_api.FirewallAPI import Firewall
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize the connection
firewall = Firewall(
    username=os.getenv("FIREWALL_USERNAME"),
    password=os.getenv("FIREWALL_PASSWORD"),
    hostname=os.getenv("FIREWALL_HOSTNAME"),
    port=int(os.getenv("FIREWALL_PORT", "4444")),
    certificate_verify=os.getenv("FIREWALL_CERTIFICATE_VERIFY", "False").lower() == "true",
    timeout=int(os.getenv("FIREWALL_TIMEOUT", "30")),
    max_retries=int(os.getenv("FIREWALL_MAX_RETRIES", "3")),
    retry_backoff=float(os.getenv("FIREWALL_RETRY_BACKOFF", "0.5"))
)

# Use context manager for automatic session cleanup
with Firewall(
    username=os.getenv("FIREWALL_USERNAME"),
    password=os.getenv("FIREWALL_PASSWORD"),
    hostname=os.getenv("FIREWALL_HOSTNAME")
) as firewall:
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
    timeout: int = 30,
    max_retries: int = 3,
    retry_backoff: float = 0.5
)
```

**Parameters:**
- `username` (str): Username for authentication
- `password` (str): Password for authentication
- `hostname` (str): Hostname or IP address of the firewall
- `port` (int, optional): Port number for the API. Default is 4444
- `certificate_verify` (bool, optional): Whether to verify SSL certificates. Default is False
- `timeout` (int, optional): Request timeout in seconds. Default is 30
- `max_retries` (int, optional): Maximum number of retry attempts. Default is 3
- `retry_backoff` (float, optional): Delay between retry attempts. Default is 0.5

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

## Examples

Check the `Examples` directory for comprehensive examples of using the API:

- Basic usage and authentication
- CRUD operations for various entities
- IP address and host management
- Service and rule management
- Security features like brute force protection
- Data export functionality

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Security

- Always use encrypted passwords in production
- Enable SSL certificate verification in production
- Store credentials securely using environment variables
- Follow the principle of least privilege when creating API users
- Regularly audit firewall rules and configurations

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.