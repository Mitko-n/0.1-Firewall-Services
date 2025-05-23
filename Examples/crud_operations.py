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
    # Create a service
    service_data = {
        "Name": "CustomHTTP",
        "Type": "TCP",
        "DestinationPort": "8080"
    }
    result = fw.create("Services", service_data)
    print("Create result:", result)

    # Read all services
    all_services = fw.read("Services")
    print("All services:", all_services)

    # Update a service
    updated_data = {
        "Name": "CustomHTTP",
        "DestinationPort": "9090"  # Only updating the port
    }
    result = fw.update("Services", updated_data)
    print("Update result:", result)

    # Delete a service
    result = fw.delete("Services", "CustomHTTP")
    print("Delete result:", result) 