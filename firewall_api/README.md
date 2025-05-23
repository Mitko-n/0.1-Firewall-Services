# Firewall API Client

A Python client library for interacting with firewall management systems. This library provides a simple and intuitive interface for managing firewall configurations, including IP addresses, services, and rules.

## Features

- **Connection Management**: Secure connection handling with SSL/TLS support
- **Authentication**: Built-in login management
- **CRUD Operations**: Create, Read, Update, and Delete operations for firewall entities
- **Batch Operations**: Support for executing multiple operations in sequence
- **Error Handling**: Comprehensive error handling and status reporting
- **Retry Mechanism**: Automatic retry for failed requests
- **Input Validation**: Robust validation of input parameters

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Connection

```python
from firewall_api import Firewall

# Initialize the firewall client
firewall = Firewall(
    username="your_username",
    password="your_password",
    hostname="firewall.example.com",
    port=4444,
    certificate_verify=False,  # Set to True for production environments
    timeout=30
)

# Test the connection
response = firewall.read("Login")
print(response)
```

### Managing IP Addresses

```python
# Create a new IP address
ip_data = {
    "Name": "Test_IP",
    "IPFamily": "IPv4",
    "HostType": "IP",
    "IPAddress": "192.168.1.1",
    "Comment": "Test IP address"
}
response = firewall.create("IPHost", ip_data)

# Read IP addresses
response = firewall.read("IPHost", "Test_IP", "=")

# Update an IP address
update_data = {
    "Name": "Test_IP",
    "Comment": "Updated comment"
}
response = firewall.update("IPHost", update_data)

# Delete an IP address
response = firewall.delete("IPHost", "Test_IP")
```

### Batch Operations

```python
operations = [
    {
        "action": "read",
        "entity": "IPHost",
        "filter_value": "Test_IP"
    },
    {
        "action": "create",
        "entity": "IPHost",
        "entity_data": {
            "Name": "New_IP",
            "IPFamily": "IPv4",
            "HostType": "IP",
            "IPAddress": "192.168.1.2"
        }
    }
]

results = firewall.batch_operation(operations, debug=True)
```

## API Reference

### Firewall Class

#### Initialization Parameters

- `username` (str): Username for authentication
- `password` (str): Password for authentication
- `hostname` (str): Firewall hostname or IP address
- `port` (int): Port number (default: 4444)
- `certificate_verify` (bool): Whether to verify SSL certificates (default: True)
- `timeout` (int): Request timeout in seconds (default: 30)
- `max_retries` (int): Maximum number of retry attempts (default: 3)
- `retry_backoff` (float): Backoff factor for retries (default: 0.5)

#### Methods

- `create(entity, entity_data)`: Create a new entity
- `read(entity, filter_value=None, filter_criteria=LIKE, filter_key_field=None)`: Read entities
- `update(entity, entity_data, entity_name=None, entity_name_key="Name")`: Update an entity
- `delete(entity, filter_value, filter_criteria=EQ, filter_key_field=None)`: Delete an entity
- `batch_operation(operations, debug=False)`: Execute multiple operations
- `close()`: Close the connection

### Filter Criteria Constants

- `EQ`: Equal to (=)
- `NOT`: Not equal to (!=)
- `LIKE`: Like operator (like)

## Response Format

All operations return a dictionary with the following structure:

```python
{
    "status": "216",  # Status code
    "message": "Operation completed successfully.",  # Status message
    "data": []  # Response data
}
```

## Error Handling

The library provides detailed error messages for various scenarios:

- Authentication failures
- Connection issues
- Invalid input parameters
- SSL/TLS errors
- Timeout errors
- Server errors

## Security Considerations

1. Always use HTTPS for connections
2. Enable certificate verification in production environments
3. Store credentials securely
4. Use appropriate timeout values
5. Implement proper error handling

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 