# Standard library imports for core functionality
import re                  # For hostname validation
import urllib.parse       # For URL parsing and validation
import warnings          # For handling warning messages
import xml.sax.saxutils  # For XML string escaping

# Third-party imports for HTTP and XML operations
import requests          # For HTTP requests
import urllib3          # For HTTP/HTTPS related utilities
import xmltodict        # For XML-dict conversion
from requests.adapters import HTTPAdapter      # For HTTP connection management
from urllib3.util.retry import Retry          # For retry functionality

# Configure warnings handling
# Suppress SyntaxWarning for invalid escape sequences
warnings.filterwarnings("ignore", category=SyntaxWarning, message=".*invalid escape sequence.*")
warnings.filterwarnings("always", category=UserWarning)
warnings.showwarning = lambda message, category, filename, lineno, file=None, line=None: print(f"{category.__name__}: {message}")

# Filter comparison operators for API queries
EQ = "="      # Equals operator
NOT = "!="    # Not equals operator
LIKE = "like" # Pattern matching operator


class Firewall:
    """
    A class to interact with Sophos Firewall API.
    Handles authentication, CRUD operations, and connection management.
    """

    def __init__(self, username, password, hostname, port=4444, certificate_verify=True, timeout=30, max_retries=3, retry_backoff=0.5):
        """
        Initialize firewall connection with authentication and connection parameters.
        Validates all input parameters and sets up the HTTP session with retry mechanism.
        """
        # Input validation section
        # Validate username and password
        if not username or not isinstance(username, str):
            raise ValueError("Username is required and must be a text value")
        if not password or not isinstance(password, str):
            raise ValueError("Password is required and must be a text value")

        # Validate hostname
        if not self._is_valid_hostname(hostname):
            raise ValueError("Invalid hostname format. Please provide a valid hostname or IP address")

        # Validate port
        try:
            port = int(port)
            if not (1 <= port <= 65535):
                raise ValueError("Port number must be between 1 and 65535")
        except (TypeError, ValueError):
            raise ValueError("Port must be a valid number between 1 and 65535")

        # Validate timeout
        try:
            timeout = float(timeout)
            if timeout <= 0:
                raise ValueError("Timeout value must be greater than 0")
        except (TypeError, ValueError):
            raise ValueError("Timeout must be a valid number greater than 0")

        # Validate retry parameters
        if not isinstance(max_retries, int) or max_retries < 0:
            raise ValueError("Maximum retry attempts must be a positive number")
        if not isinstance(retry_backoff, (int, float)) or retry_backoff < 0:
            raise ValueError("Retry backoff must be a positive number")

        # Setup base URL for API endpoint
        self.url = f"https://{hostname}:{port}/webconsole/APIController"

        # Create XML login credentials with escaped special characters
        escaped_password = xml.sax.saxutils.escape(password)
        self.xml_login = f"""<Login><Username>{username}</Username><Password>{escaped_password}</Password></Login>"""

        # Initialize HTTP session with retry mechanism
        self.session = requests.Session()
        self._setup_certificate_verification(certificate_verify)
        self._setup_retry_strategy(max_retries, retry_backoff)

        # Configure secure HTTP headers
        self.headers = {
            "Accept": "application/xml",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        }

        self.closed = False
        self.timeout = timeout

    def _setup_certificate_verification(self, certificate_verify):
        """Configure SSL certificate verification behavior"""
        if certificate_verify:
            self.session.verify = True # type: ignore
            warnings.warn(
                "Certificate verification is active. For self-signed certificates,\n "
                "either disable verification or add the certificate to trusted certificates.",
                UserWarning,
            )
        else:
            self.session.verify = False # type: ignore
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            warnings.warn(
                "Certificate verification is disabled. For production environments,\n "
                "it's recommended to use proper SSL certificates instead of disabling verification.",
                UserWarning,
            )

    def _setup_retry_strategy(self, max_retries, retry_backoff):
        """Set up automatic retry mechanism for failed requests"""
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter) # type: ignore

    # Resource management methods
    def __enter__(self):
        """Context manager entry point"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Context manager exit point - ensures proper cleanup"""
        self.close()

    def close(self):
        """Clean up resources and close the session"""
        if not self.closed and self.session is not None:
            self.session.close()
            self.session = None
            self.closed = True
            return {
                "status": "200",
                "message": "Session closed successfully.",
                "data": [],
            }
        return {
            "status": "400",
            "message": "Session was already closed.",
            "data": [],
        }

    # CRUD Operations
    def create(self, entity, entity_data):
        """Create a new entity in the firewall"""
        if not isinstance(entity_data, dict):
            return {
                "status": "400",
                "message": "entity_data must be a dictionary.",
                "data": [],
            }

        if entity == "Services":
            entity_data = self._remove_spaces(entity_data)

        xml_action = f"""<Set operation="add"><{entity}>{xmltodict.unparse(entity_data, full_document=False)}</{entity}></Set>"""
        return self._perform_action(xml_action, entity)

    def read(self, entity, filter_value=None, filter_criteria=LIKE, filter_key_field=None):
        """Read entity/entities matching the filter criteria"""
        inner_xml = ""
        if filter_value:
            key_field = filter_key_field or "Name"
            inner_xml = f"""<Filter><key name="{key_field}" criteria="{filter_criteria}">{filter_value}</key></Filter>"""

        xml_action = f"""<Get><{entity}>{inner_xml}</{entity}></Get>"""
        return self._perform_action(xml_action, entity)

    def update(self, entity, entity_data, entity_name=None, entity_name_key="Name"):
        """Update an existing entity with new data"""
        if entity_name is None:
            if entity_name_key not in entity_data:
                return {
                    "status": "400",
                    "message": f"Entity data must contain '{entity_name_key}' field or provide entity_name parameter.",
                    "data": [],
                }
            entity_name = entity_data[entity_name_key]

        existing_data = self.read(entity, entity_name, EQ, entity_name_key)
        if existing_data["status"] != "216" or not existing_data["data"]:
            return {
                "status": "404",
                "message": "Entity not found for update.",
                "data": [],
            }
        if len(existing_data["data"]) > 1:
            return {
                "status": "400",
                "message": "Multiple entities found for update. Provide a unique entity_name.",
                "data": [],
            }

        current_entity = existing_data["data"][0]
        updated_data = self._merge_entities(current_entity, entity_data)

        xml_action = f"""<Set operation="update"><{entity}>{xmltodict.unparse(updated_data, full_document=False)}</{entity}></Set>"""
        return self._perform_action(xml_action, entity)

    def delete(self, entity, filter_value, filter_criteria=EQ, filter_key_field=None):
        """Delete an entity matching the filter criteria"""
        if entity == "FirewallRule":
            inner_xml = f"<Name>{filter_value}</Name>"
        elif entity == "LocalServiceACL":
            inner_xml = f"<RuleName>{filter_value}</RuleName>"
        else:
            key_field = filter_key_field or "Name"
            inner_xml = f'<Filter><key name="{key_field}" criteria="{filter_criteria}">{filter_value}</key></Filter>'

        xml_action = f"""<Remove><{entity}>{inner_xml}</{entity}></Remove>"""
        return self._perform_action(xml_action, entity)

    # Helper methods
    def _is_valid_hostname(self, hostname):
        """Validate hostname format"""
        if len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1]
        allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))

    def _validate_url(self, url):
        """Ensure URL is well-formed and uses HTTPS"""
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme == "https"
        except:
            return False

    def _format_xml_response(self, response, entity):
        """Parse and format XML response from the API"""
        response = response.get("Response", {})

        if "Status" in response:
            return {
                "status": response["Status"]["@code"],
                "message": response["Status"]["#text"],
                "data": [],
            }

        if response.get("Login", {}).get("status") == "Authentication Failure":
            return {
                "status": "401",
                "message": "Authentication failed. Please check your username and password.",
                "data": [],
            }

        if entity in response:
            entity_data = response[entity]

            if "Status" in entity_data:
                if "@code" in entity_data["Status"]:
                    return {
                        "status": entity_data["Status"]["@code"],
                        "message": entity_data["Status"]["#text"],
                        "data": [],
                    }
                elif entity_data["Status"] in ["No. of records Zero.", "Number of records Zero."]:
                    return {
                        "status": "526",
                        "message": "No matching records found.",
                        "data": [],
                    }

            entity_data = [entity_data] if isinstance(entity_data, dict) else entity_data

            entity_data = [{k: v for k, v in item.items() if k != "@transactionid"} for item in entity_data]

            return {
                "status": "216",
                "message": "Operation completed successfully.",
                "data": entity_data,
            }

        return {
            "status": "404",
            "message": "The requested resource was not found.",
            "data": [],
        }

    def _perform_action(self, xml_action, entity):
        """Execute API request and handle response/errors"""
        if self.closed or self.session is None:
            return {
                "status": "400",
                "message": "The connection is closed. Please create a new connection to continue.",
                "data": [],
            }

        if not self._validate_url(self.url):
            return {
                "status": "400",
                "message": "Invalid connection URL. Please check the hostname and port settings.",
                "data": [],
            }

        full_request_xml = f"<Request>{self.xml_login}{xml_action}</Request>"

        try:
            response = self.session.post(self.url, headers=self.headers, data={"reqxml": full_request_xml}, timeout=self.timeout)
            response.raise_for_status()
            return self._format_xml_response(xmltodict.parse(response.content.decode()), entity)
        except requests.exceptions.SSLError as e:
            error_msg = str(e)
            if "CERTIFICATE_VERIFY_FAILED" in error_msg and "self-signed certificate" in error_msg:
                return {
                    "status": "495",
                    "message": "Unable to verify the server's certificate. This is likely due to a self-signed certificate. Please set certificate_verify=False or add the certificate to your trusted certificates.",
                    "data": [],
                }
            return {
                "status": "495",
                "message": "Secure connection failed. Please check your SSL/TLS settings and certificate configuration.",
                "data": [],
            }
        except requests.exceptions.ConnectionError as e:
            return {
                "status": "503",
                "message": "Unable to connect to the server.\nPlease check your network connection and server availability.",
                "data": [],
            }
        except requests.exceptions.Timeout as e:
            return {
                "status": "504",
                "message": "The request timed out. Please check your connection and try again.",
                "data": [],
            }
        except requests.RequestException as e:
            return {
                "status": "500",
                "message": "The request failed. Please check your connection settings and try again.",
                "data": [],
            }

    def _merge_entities(self, current_entity, new_entity):
        """Deep merge two entity dictionaries"""
        for key, value in new_entity.items():
            if isinstance(value, dict) and isinstance(current_entity.get(key), dict):
                self._merge_entities(current_entity[key], value)
            else:
                current_entity[key] = value
        return current_entity

    def _remove_spaces(self, data):
        """Remove spaces from values except for specific fields"""
        if not isinstance(data, dict):
            return data

        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = self._remove_spaces(value)
            elif isinstance(value, list):
                data[key] = [self._remove_spaces(item) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, str) and key not in ["Name", "Description", "RuleName"]:
                data[key] = value.replace(" ", "")
        return data
