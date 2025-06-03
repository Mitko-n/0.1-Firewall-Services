import configparser
import os
import sys
import csv
import ipaddress

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Add parent directory to path

from firewall_api import Firewall, LIKE, EQ, NOT

# Read configuration
config = configparser.ConfigParser(interpolation=None)
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Credentials', 'config.ini')
config.read(config_path)

# Get firewall credentials from config
username = config['Firewall']['username']
password = config['Firewall']['password']
firewall_ip = config['Firewall']['firewall_ip']
port = config['Firewall'].getint('port', fallback=4444)
certificate_verify = config['Firewall'].getboolean('certificate_verify', fallback=False)
timeout = config['Firewall'].getint('timeout', fallback=30)

firewall = Firewall(username, password, firewall_ip, port, certificate_verify, timeout)


print("CREATE :: ", firewall.create("IPHost", {"Name": "TEST 1", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.100"}))
print("CREATE :: ", firewall.create("IPHost", {"Name": "TEST 2", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.100"}))
print("CREATE :: ", firewall.create("IPHost", {"Name": "TEST 3", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.100"}))
print("CREATE :: ", firewall.create("IPHost", {"Name": "TEST 4", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.100"}))

print("\nREAD :: ")
response = firewall.read("IPHost", "TEST", LIKE)
print("Code:", response["status"], "Text:", response["message"])
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")

print("\nUPDATE :: ", firewall.update("IPHost", {"Name": "TEST 1", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.101"}))
print("UPDATE :: ", firewall.update("IPHost", {"Name": "TEST 2", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.102"}))
print("UPDATE :: ", firewall.update("IPHost", {"Name": "TEST 3", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.103"}))
print("UPDATE :: ", firewall.update("IPHost", {"Name": "TEST 4", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.104"}))

print("\nREAD :: ")
response = firewall.read("IPHost", "TEST", LIKE)
print("Code:", response["status"], "Text:", response["message"])
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")

print("\nDELETE :: ", firewall.delete("IPHost", "TEST 1"))
print("DELETE :: ", firewall.delete("IPHost", "TEST 2"))

print("\nREAD :: ")
response = firewall.read("IPHost", "TEST", LIKE)
print("Code:", response["status"], "Text:", response["message"])
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")

print("\nDELETE :: ", firewall.delete("IPHost", "TEST", LIKE))

print("\nREAD :: ")
response = firewall.read("IPHost", "TEST", LIKE)
print("Code:", response["status"], "Text:", response["message"])
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")


print("\nREAD :: FirewallRule")
response = firewall.read("FirewallRule")
print("Code:", response["status"], "Text:", response["message"])
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")

firewall.close()
