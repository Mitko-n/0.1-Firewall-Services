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
    # Test connection
    result = fw.read("Login")
    print("Connection Test:", result)
    
    # Perform operations
    result = fw.read("Services", "HTTP")
    print("Services Result:", result) 