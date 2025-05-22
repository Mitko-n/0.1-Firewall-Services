from firewall_api import Firewall

# Initialize the client
firewall = Firewall(
    username="admin",
    password="password",
    hostname="firewall.example.com",
    port=4444,
    certificate_verify=False  # Set to True in production
)

# Create a service
service_data = {
    "Name": "CustomHTTP",
    "Type": "TCP",
    "DestinationPort": "8080"
}
result = firewall.create("Services", service_data)
print("Create result:", result)

# Read all services
all_services = firewall.read("Services")
print("All services:", all_services)

# Update a service
updated_data = {
    "Name": "CustomHTTP",
    "DestinationPort": "9090"  # Only updating the port
}
result = firewall.update("Services", updated_data)
print("Update result:", result)

# Delete a service
result = firewall.delete("Services", "CustomHTTP")
print("Delete result:", result) 