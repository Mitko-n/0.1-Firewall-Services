from firewall_api.FirewallAPI import Firewall

# Initialize the client
firewall = Firewall(
    username="admin",
    password="password",
    hostname="firewall.example.com",
    port=4444,
    certificate_verify=False  # Set to True in production
)

# Use as a context manager (recommended)
with Firewall(username="admin", password="password", hostname="firewall.example.com") as fw:
    # Perform operations
    result = fw.read("Services", "HTTP")
    print(result) 