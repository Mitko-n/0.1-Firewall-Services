import os
import sys
from firewall_api.FirewallAPI import Firewall, LIKE, EQ, NOT
import json
import ipaddress
import csv


# Helper functions for entity operations
def create_entity(firewall, entity_type, entity_data, print_data=False, print_result=False):
    """
    Create and log an entity.

    :param entity_type: The type of entity to create.
    :param entity_data: The data for the entity to create.
    :param print_data: Boolean to print the data being sent (default is False).
    :param print_result: Boolean to print the result of the operation (default is False).
    :return: The response from the create operation.
    """
    if print_data:
        print(f"Creating {entity_type} with data: {entity_data}")
    response = firewall.create(entity_type, entity_data)
    if print_result:
        print(f"CREATE :: {response}\n")
    return response


def update_entity(firewall, entity_type, entity_data, print_data=False, print_result=False):
    """
    Update and log an entity.

    :param entity_type: The type of entity to update.
    :param entity_data: The data for the entity to update.
    :param print_data: Boolean to print the data being sent (default is False).
    :param print_result: Boolean to print the result of the operation (default is False).
    :return: The response from the update operation.
    """
    if print_data:
        print(f"Updating {entity_type} with data: {entity_data}")
    response = firewall.update(entity_type, entity_data)
    if print_result:
        print(f"UPDATE :: {response}\n")
    return response


def read_entity(firewall, entity_type, filter_value=None, filter_selector=LIKE, filter_key=None, print_data=False, print_result=False):
    """
    Read and log an entity.

    :param entity_type: The type of entity to read.
    :param filter_value: The value to filter by (default is None).
    :param filter_selector: The filter selector to use (default is LIKE).
    :param filter_key: The key to filter by (default is None).
    :param print_data: Boolean to print the data being sent (default is False).
    :param print_result: Boolean to print the result of the operation (default is False).
    :return: The response from the read operation.
    """
    response = firewall.read(entity_type, filter_value, filter_selector, filter_key)
    if print_result:
        print(f"READ :: {response}\n")
    return response


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
    # Test connection
    print("=== Testing Connection ===")
    response = fw.read("Login")
    print(f"Connection Test :: {response}\n")

    # Create IPHost for brute force protection
    print("=== Creating IPHost for Brute Force Protection ===")
    iphost_data = {
        "Name": "BruteForceBlock",
        "HostType": "IP",
        "IPAddress": "192.168.1.100",  # Example IP to block
    }
    response = create_entity(fw, "IPHost", iphost_data, print_data=True, print_result=True)

    # Create Firewall Rule for brute force protection
    print("=== Creating Firewall Rule for Brute Force Protection ===")
    rule_data = {
        "Name": "Block Brute Force Attempts",
        "Status": "Enable",
        "Position": "Top",
        "PolicyType": "Network",
        "NetworkPolicy": {
            "Action": "Drop",
            "SourceZones": {"Zone": ["WAN"]},
            "DestinationZones": {"Zone": ["LAN"]},
            "SourceNetworks": {"Network": ["BruteForceBlock"]},
        },
    }
    response = create_entity(fw, "FirewallRule", rule_data, print_data=True, print_result=True)

    # Read all firewall rules
    print("=== Reading All Firewall Rules ===")
    response = read_entity(fw, "FirewallRule", print_result=True)

    # Update firewall rule to disable it
    print("=== Disabling Brute Force Protection Rule ===")
    update_data = {
        "Name": "Block Brute Force Attempts",
        "Status": "Disable",
    }
    response = update_entity(fw, "FirewallRule", update_data, print_data=True, print_result=True)

    # Read all IPHosts
    print("=== Reading All IPHosts ===")
    response = read_entity(fw, "IPHost", print_result=True)

    # Delete IPHost
    print("=== Deleting Brute Force Block IPHost ===")
    response = fw.delete("IPHost", "BruteForceBlock")
    print(f"DELETE :: {response}\n")

    # Delete Firewall Rule
    print("=== Deleting Brute Force Protection Rule ===")
    response = fw.delete("FirewallRule", "Block Brute Force Attempts")
    print(f"DELETE :: {response}\n")
