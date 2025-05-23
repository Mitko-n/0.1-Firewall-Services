from firewall_api.FirewallAPI import Firewall, LIKE, EQ, NOT

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
    # IPHost Example
    print("=== IPHost Example ===")
    entity_type = "IPHost"
    entity_name = "TEST"
    entity_data = {
        "Name": entity_name,
        # "IPFamily": "IPv4",   #IPv4 is Default settings
        "HostType": "IP",
        "IPAddress": "172.16.17.100",
    }
    print("CREATE :: ", fw.create(entity_type, entity_data))
    print("READ   :: ", fw.read(entity_type, entity_name))
    print("UPDATE :: ", fw.update(entity_type, {"Name": entity_name, "HostType": "IP", "IPAddress": "172.16.17.222"}))
    print("READ   :: ", fw.read(entity_type, entity_name))
    print("DELETE :: ", fw.delete(entity_type, entity_name))
    print("READ   :: ", fw.read(entity_type, entity_name))  # No IPHosts with the entity_name "TEST"

    # Read all IPHosts
    response = fw.read("IPHost")  # READ all IPHost
    print("\nAll IPHosts:")
    print("Code:", response["status"], "Text:", response["message"])
    for index, item in enumerate(response["data"], start=1):
        print(f"{index:03}: {item}")

    # FQDNHostGroup Example
    print("\n=== FQDNHostGroup Example ===")
    entity_type = "FQDNHostGroup"
    entity_name = "TEST FQDNHostGroup"
    entity_data = {
        "Name": entity_name,
        # "Description": "TEST FQDNHostGroup",
        # "FQDNHostList": {"FQDNHost": []},
    }

    print("CREATE :: ", fw.create(entity_type, entity_data))
    print("READ   :: ", fw.read(entity_type, entity_name)) 