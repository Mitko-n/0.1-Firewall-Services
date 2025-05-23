import requests
import xmltodict
import urllib3
import re
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import warnings
import sys

# Configure warning filter to show only the message
warnings.filterwarnings('always', category=UserWarning)
warnings.showwarning = lambda message, category, filename, lineno, file=None, line=None: print(f"{category.__name__}: {message}")

EQ = "="
NOT = "!="
LIKE = "like"


class Firewall:

    def __init__(
        self,
        username,
        password,
        hostname,
        port=4444,
        certificate_verify=True,
        timeout=30,
        max_retries=3,
        retry_backoff=0.5,
    ):
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

        self.url = f"https://{hostname}:{port}/webconsole/APIController"
        self.xml_login = f"""<Login><Username>{username}</Username><Password>{password}</Password></Login>"""
        
        self.session = requests.Session()
        
        # Handle certificate verification
        if certificate_verify:
            self.session.verify = True
            warnings.warn(
                "Certificate verification is active. For self-signed certificates,\n "
                "either disable verification or add the certificate to trusted certificates.",
                UserWarning
            )
        else:
            self.session.verify = False
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            warnings.warn(
                "Certificate verification is disabled. For production environments,\n "
                "it's recommended to use proper SSL certificates instead of disabling verification.",
                UserWarning
            )
        
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_backoff,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        self.headers = {
            "Accept": "application/xml",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
        
        self.closed = False
        self.timeout = timeout

    def _is_valid_hostname(self, hostname):
        if len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1]
        allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))

    def _validate_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme == 'https'
        except:
            return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
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

    def _format_xml_response(self, response, entity):
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
            response = self.session.post(
                self.url,
                headers=self.headers,
                data={"reqxml": full_request_xml},
                timeout=self.timeout
            )
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

    def create(self, entity, entity_data):
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

    def _remove_spaces(self, data):
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

    def read(self, entity, filter_value=None, filter_criteria=LIKE, filter_key_field=None):
        inner_xml = ""
        if filter_value:
            key_field = filter_key_field or "Name"
            inner_xml = f"""<Filter><key name="{key_field}" criteria="{filter_criteria}">{filter_value}</key></Filter>"""

        xml_action = f"""<Get><{entity}>{inner_xml}</{entity}></Get>"""
        return self._perform_action(xml_action, entity)

    def update(self, entity, entity_data, entity_name=None, entity_name_key="Name"):
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

    def _merge_entities(self, current_entity, new_entity):
        for key, value in new_entity.items():
            if isinstance(value, dict) and isinstance(current_entity.get(key), dict):
                self._merge_entities(current_entity[key], value)
            else:
                current_entity[key] = value
        return current_entity

    def delete(self, entity, filter_value, filter_criteria=EQ, filter_key_field=None):
        if entity == "FirewallRule":
            inner_xml = f"<Name>{filter_value}</Name>"
        elif entity == "LocalServiceACL":
            inner_xml = f"<RuleName>{filter_value}</RuleName>"
        else:
            key_field = filter_key_field or "Name"
            inner_xml = f'<Filter><key name="{key_field}" criteria="{filter_criteria}">{filter_value}</key></Filter>'

        xml_action = f"""<Remove><{entity}>{inner_xml}</{entity}></Remove>"""
        return self._perform_action(xml_action, entity)

    # Experimental batch operation
    # This is a simple implementation and may need to be adjusted based on the actual API requirements.
    def batch_operation(self, operations, debug=False):
        results = []

        for index, op in enumerate(operations, start=1):
            if debug:
                print(f"Processing operation {index}/{len(operations)}: {op}")

            action = op.get("action")
            entity = op.get("entity")

            if not action or not entity:
                error_response = {
                    "status": "400",
                    "message": "Missing 'action' or 'entity' in operation",
                    "data": [],
                }
                if debug:
                    print(f"Error in operation {index}: {error_response}")
                results.append(error_response)
                continue

            try:
                if action == "read":
                    result = self.read(
                        entity=entity,
                        filter_value=op.get("filter_value"),
                        filter_criteria=op.get("filter_criteria", LIKE),
                        filter_key_field=op.get("filter_key_field"),
                    )
                elif action == "create":
                    result = self.create(
                        entity=entity,
                        entity_data=op.get("entity_data", {}),
                    )
                elif action == "update":
                    result = self.update(
                        entity=entity,
                        entity_data=op.get("entity_data", {}),
                    )
                elif action == "delete":
                    result = self.delete(
                        entity=entity,
                        filter_value=op.get("filter_value", ""),
                        filter_criteria=op.get("filter_criteria", EQ),
                        filter_key_field=op.get("filter_key_field"),
                    )
                else:
                    result = {
                        "status": "400",
                        "message": f"Unsupported action: {action}",
                        "data": [],
                    }

                if debug:
                    print(f"Result of operation {index} ({action}): {result}")
                results.append(result)

            except Exception as e:
                error_response = {
                    "status": "500",
                    "message": f"Operation failed: {str(e)}",
                    "data": [],
                }
                if debug:
                    print(f"Error in operation {index} ({action}): {error_response}")
                results.append(error_response)

        return results
