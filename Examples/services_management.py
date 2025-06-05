from firewall_api.FirewallAPI import Firewall, LIKE, EQ, NOT

# Initialize the client
firewall = Firewall(
    username="admin",
    password="password",
    hostname="firewall.example.com",
    port=4444,
    certificate_verify=False,  # Set to True in production
    timeout=30,  # Default timeout in seconds
)

# Use as a context manager (recommended)
with Firewall(username="admin", password="password", hostname="firewall.example.com", port=4444, certificate_verify=False, timeout=30) as fw:
    # Create TCP/UDP services
    print("=== Creating TCP/UDP Services ===")
    data = [
        {
            "Name": "test service TCP/UDP",
            "Description": "None",
            "Type": "TCPorUDP",
            "ServiceDetails": {
                "ServiceDetail": [
                    {"SourcePort": "1: 65535", "DestinationPort": "1", "Protocol": "TCP"},
                    {"SourcePort": "1: 65535", "DestinationPort": "1", "Protocol": "UDP"},
                    {"SourcePort": "1: 65535", "DestinationPort": "2", "Protocol": "TCP"},
                    {"SourcePort": "1: 65535", "DestinationPort": "2", "Protocol": "UDP"},
                ]
            },
        },
        {
            "Name": "test service TCP/UDP one",
            "Description": "None",
            "Type": "TCPorUDP",
            "ServiceDetails": {"ServiceDetail": {"SourcePort": "1:65535", "DestinationPort": "1", "Protocol": "TCP"}},
        },
        {
            "Name": "test service TCP/UDP one range",
            "Description": "None",
            "Type": "TCPorUDP",
            "ServiceDetails": {"ServiceDetail": {"SourcePort": "1: 65535", "DestinationPort": "1: 123", "Protocol": "TCP"}},
        },
        {
            "Name": "test service TCP/UDP one range multy",
            "Description": "None",
            "Type": "TCPorUDP",
            "ServiceDetails": {
                "ServiceDetail": [
                    {"SourcePort": "1:             65535", "DestinationPort": "1     : 123", "Protocol": "TCP"},
                    {"SourcePort": "1        : 65535", "DestinationPort": "2          :             890", "Protocol": "UDP"},
                ]
            },
        },
    ]

    for item in data:
        print(f"Creating service: {item['Name']}")
        result = fw.create("Services", item)
        print(f"Result: {result}\n")

    # Read all services
    print("=== Reading All Services ===")
    response = fw.read("Services")
    print("Code:", response["status"], "Text:", response["message"])
    for index, item in enumerate(response["data"], start=1):
        print(f"{index:03}: {item}")

    # Read specific service
    print("\n=== Reading Specific Service ===")
    service_name = "test service TCP/UDP"
    response = fw.read("Services", service_name)
    print(f"Reading service: {service_name}")
    print("Code:", response["status"], "Text:", response["message"])
    for index, item in enumerate(response["data"], start=1):
        print(f"{index:03}: {item}")

    # Update service
    print("\n=== Updating Service ===")
    service_name = "test service TCP/UDP"
    updated_data = {
        "Name": service_name,
        "Description": "Updated description",
    }
    response = fw.update("Services", updated_data)
    print(f"Updating service: {service_name}")
    print("Code:", response["status"], "Text:", response["message"])
    print("Result:", response)

    # Delete service
    print("\n=== Deleting Service ===")
    service_name = "test service TCP/UDP"
    response = fw.delete("Services", service_name)
    print(f"Deleting service: {service_name}")
    print("Code:", response["status"], "Text:", response["message"])
    print("Result:", response)
