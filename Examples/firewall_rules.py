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
    # Create a firewall rule
    print("=== Creating Firewall Rule ===")
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
    response = fw.create("FirewallRule", entity_data)
    print("Code:", response["status"], "Text:", response["message"])
    print("Result:", response)

    # Read all firewall rules
    print("\n=== Reading All Firewall Rules ===")
    response = fw.read("FirewallRule")
    print("Code:", response["status"], "Text:", response["message"])
    for index, item in enumerate(response["data"], start=1):
        print(f"{index:03}: {item}")

    # Read specific firewall rule
    print("\n=== Reading Specific Firewall Rule ===")
    rule_name = "Demo Rule"
    response = fw.read("FirewallRule", rule_name)
    print(f"Reading rule: {rule_name}")
    print("Code:", response["status"], "Text:", response["message"])
    for index, item in enumerate(response["data"], start=1):
        print(f"{index:03}: {item}")

    # Update firewall rule - add source networks
    print("\n=== Updating Firewall Rule - Add Source Networks ===")
    updated_data = {
        "Status": "Enable",
        "NetworkPolicy": {
            "Action": "Accept",
            "SourceNetworks": {"Network": ["192.168.30.0/24", "192.168.10.0/24"]},
        },
    }
    response = fw.update("FirewallRule", updated_data, entity_name="Demo Rule")
    print("Code:", response["status"], "Text:", response["message"])
    print("Result:", response)

    # Update firewall rule - disable rule
    print("\n=== Updating Firewall Rule - Disable Rule ===")
    updated_data = {
        "Status": "Disable",
    }
    response = fw.update("FirewallRule", updated_data, entity_name="Demo Rule")
    print("Code:", response["status"], "Text:", response["message"])
    print("Result:", response)

    # Delete firewall rule
    print("\n=== Deleting Firewall Rule ===")
    rule_name = "Demo Rule"
    response = fw.delete("FirewallRule", rule_name)
    print(f"Deleting rule: {rule_name}")
    print("Code:", response["status"], "Text:", response["message"])
    print("Result:", response)
