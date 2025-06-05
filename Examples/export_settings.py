import os
import csv
import sys
from firewall_api.FirewallAPI import Firewall, LIKE, EQ, NOT


# Filter responses to extract specific fields
def filter_responses(responses, requested_fields):
    def extract_fields(data, fields):
        if isinstance(data, dict):
            result = {}
            for field in fields:
                keys = field.split(".")
                value = data
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        value = None
                        break
                if value is not None:
                    result[keys[-1]] = value
            return result
        return {}

    filtered_responses_list = [extract_fields(item, requested_fields) for item in responses]
    return filtered_responses_list


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
    # Setup export directory
    customer_name = "GW LAB"
    exports_path = "Exports\\" + customer_name
    if not os.path.exists(exports_path):
        os.makedirs(exports_path)

    # Export Interface settings
    print("=== Exporting Interface Settings ===")
    response = fw.read("Interface")
    print("Code:", response["status"], "Text:", response["message"])

    if response["status"] == "216" and response["data"]:
        # Define fields to extract
        interface_fields = ["Name", "IPAddress", "Netmask", "Status"]

        # Filter responses to get only the requested fields
        filtered_data = filter_responses(response["data"], interface_fields)

        # Save to CSV
        csv_file_path = os.path.join(exports_path, "interfaces.csv")
        with open(csv_file_path, mode="w", encoding="UTF8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=interface_fields)
            writer.writeheader()
            writer.writerows(filtered_data)

        print(f"Interface settings exported to {csv_file_path}")
    else:
        print("Failed to export interface settings")

    # Export Firewall Rules
    print("\n=== Exporting Firewall Rules ===")
    response = fw.read("FirewallRule")
    print("Code:", response["status"], "Text:", response["message"])

    if response["status"] == "216" and response["data"]:
        # Define fields to extract
        rule_fields = ["Name", "Status", "Position", "PolicyType", "NetworkPolicy.Action"]

        # Filter responses to get only the requested fields
        filtered_data = filter_responses(response["data"], rule_fields)

        # Save to CSV
        csv_file_path = os.path.join(exports_path, "firewall_rules.csv")
        with open(csv_file_path, mode="w", encoding="UTF8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=rule_fields)
            writer.writeheader()
            writer.writerows(filtered_data)

        print(f"Firewall rules exported to {csv_file_path}")
    else:
        print("Failed to export firewall rules")

    # Export Services
    print("\n=== Exporting Services ===")
    response = fw.read("Services")
    print("Code:", response["status"], "Text:", response["message"])

    if response["status"] == "216" and response["data"]:
        # Define fields to extract
        service_fields = ["Name", "Type", "Description"]

        # Filter responses to get only the requested fields
        filtered_data = filter_responses(response["data"], service_fields)

        # Save to CSV
        csv_file_path = os.path.join(exports_path, "services.csv")
        with open(csv_file_path, mode="w", encoding="UTF8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=service_fields)
            writer.writeheader()
            writer.writerows(filtered_data)

        print(f"Services exported to {csv_file_path}")
    else:
        print("Failed to export services")
