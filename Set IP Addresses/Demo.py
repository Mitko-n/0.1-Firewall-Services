from library.xgs_crud import Firewall, EQ, NOT, LIKE
import json

# Firewall Credentials
# JSON File
# {
#     "firewall_ip": "<FIREWALL_IP_ADDRESS>",
#     "username": "<USER_NAME>",
#     "port" : "<FIREWALL_PORT>"
#     "password": "<PASSWORD",
#     "password_encrypted": <true|false>
# }

firewall_info = json.load(open("Credentials\\firewall_access.json"))
username = firewall_info["username"]
password = firewall_info["password"]
firewall_ip = firewall_info["firewall_ip"]
port = firewall_info["port"]
password_encrypted = firewall_info["password_encrypted"]

firewall = Firewall(username, password, firewall_ip, port, password_encrypted)

print("CREATE :: ", firewall.create("IPHost", {"Name": "TEST 1", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.100"}))
print("CREATE :: ", firewall.create("IPHost", {"Name": "TEST 2", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.100"}))
print("CREATE :: ", firewall.create("IPHost", {"Name": "TEST 3", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.100"}))
print("CREATE :: ", firewall.create("IPHost", {"Name": "TEST 4", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.100"}))

print("\nREAD :: ")
response = firewall.read("IPHost", "TEST", LIKE)
print("Code:", response["code"], "Text:", response["text"])
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")

print("\nUPDATE :: ", firewall.update("IPHost", {"Name": "TEST 1", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.101"}))
print("UPDATE :: ", firewall.update("IPHost", {"Name": "TEST 2", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.102"}))
print("UPDATE :: ", firewall.update("IPHost", {"Name": "TEST 3", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.103"}))
print("UPDATE :: ", firewall.update("IPHost", {"Name": "TEST 4", "IPFamily": "IPv4", "HostType": "IP", "IPAddress": "172.16.17.104"}))

print("\nREAD :: ")
response = firewall.read("IPHost", "TEST", LIKE)
print("Code:", response["code"], "Text:", response["text"])
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")

print("\nDELETE :: ", firewall.delete("IPHost", "TEST 1"))
print("DELETE :: ", firewall.delete("IPHost", "TEST 2"))

print("\nREAD :: ")
response = firewall.read("IPHost", "TEST", LIKE)
print("Code:", response["code"], "Text:", response["text"])
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")

print("\nDELETE :: ", firewall.delete("IPHost", "TEST", LIKE))

print("\nREAD :: ")
response = firewall.read("IPHost", "TEST", LIKE)
print("Code:", response["code"], "Text:", response["text"])
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")


print("\nREAD :: FirewallRule")
response = firewall.read("FirewallRule")
print("Code:", response["code"], "Text:", response["text"])
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")

firewall.close()
