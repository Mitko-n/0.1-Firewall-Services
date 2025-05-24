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
    retry_backoff=0.5,  # Backoff factor for retries
)

# Use as a context manager (recommended)
with Firewall(username="admin", password="password", hostname="firewall.example.com", port=4444, certificate_verify=False, timeout=30) as fw:
    # Test connection
    result = fw.read("Login")
    print("Connection Test:", result)

    # Create a new service
    service_data = {
        "Name": "CustomService",
        "Type": "TCPorUDP",
        "ServiceDetails": {"ServiceDetail": {"SourcePort": "1:65535", "DestinationPort": "8080", "Protocol": "TCP"}},
    }
    create_result = fw.create("Services", service_data)
    print("Create Service Result:", create_result)

    # Read services with filter
    services = fw.read("Services", "Custom", "like", "Name")
    print("Filtered Services:", services)

    # Update a service
    update_data = {
        "Name": "CustomService",
        "Type": "TCPorUDP",
        "ServiceDetails": {"ServiceDetail": {"SourcePort": "1:65535", "DestinationPort": "8443", "Protocol": "TCP"}},
    }
    update_result = fw.update("Services", update_data)
    print("Update Service Result:", update_result)

    # Delete a service
    delete_result = fw.delete("Services", "CustomService")
    print("Delete Service Result:", delete_result)
