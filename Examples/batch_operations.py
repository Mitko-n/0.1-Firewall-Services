from firewall_api.FirewallAPI import Firewall

# Initialize the client
firewall = Firewall(
    username="admin",
    password="password",
    hostname="firewall.example.com",
    port=4444,
    certificate_verify=False,  # Set to True in production
    timeout=30,  # Default timeout in seconds
    max_retries=3,  # Number of retry attempts
    retry_backoff=0.5  # Backoff factor for retries
)

# Use as a context manager (recommended)
with Firewall(
    username="admin",
    password="password",
    hostname="firewall.example.com",
    port=4444,
    certificate_verify=False,
    timeout=30
) as fw:
    # Define batch operations
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

    # Perform batch operations
    results = fw.batch_operation(operations, debug=True)
    print("Batch operation results:", results) 