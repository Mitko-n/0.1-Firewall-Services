# Firewall API Examples

This directory contains examples of how to use the Firewall API for various operations.

## Directory Description
This directory is organized to provide a comprehensive set of examples for working with the Firewall API. Each example file is designed to be self-contained and demonstrates specific functionality of the API. The examples progress from basic usage to more complex operations, making it easier for users to understand and implement different features of the firewall system.

The examples are structured to cover all major aspects of firewall management:
- Basic API interaction and authentication
- CRUD operations for various entities
- Batch processing capabilities
- IP address and host management
- Service and rule management
- Security features like brute force protection
- Data export functionality

Each example includes detailed comments and follows best practices for API usage, making them suitable for both learning and production use.

## Example Files

- **basic_usage.py**: Basic example of initializing the Firewall API client and performing a simple read operation.
- **crud_operations.py**: Examples of Create, Read, Update, and Delete operations for services.
- **batch_operations.py**: Example of performing multiple operations in a single batch.
- **ip_address_management.py**: Examples of managing IP addresses and FQDN host groups.
- **services_management.py**: Examples of creating, reading, updating, and deleting TCP/UDP services.
- **firewall_rules.py**: Examples of creating, reading, updating, and deleting firewall rules.
- **export_settings.py**: Example of exporting firewall settings to CSV files.
- **brute_force_protection.py**: Example of implementing brute force protection using IPHost and FirewallRule.

## Usage

Each example file can be run independently. They all follow a similar pattern:

1. Initialize the Firewall API client
2. Perform operations
3. Print results

To run an example:

```bash
python examples/basic_usage.py
```

## Notes

- All examples use placeholder credentials. Replace them with your actual firewall credentials.
- Set `certificate_verify=True` in production environments.
- Use encrypted passwords when possible by setting `password_encrypted=True`.
- For batch operations, set `debug=True` to get detailed information about each operation. 