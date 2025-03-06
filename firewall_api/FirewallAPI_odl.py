import requests
import xmltodict
from typing import Dict, List, Any, Optional, Union, Tuple

# Constants for Filter Criteria
EQ = "="
NOT = "!="
LIKE = "like"

ResponseType = Dict[str, Union[str, List[Dict[str, Any]]]]

class Firewall:
    def __init__(self, username: str, password: str, hostname: str, port: int = 4444, 
                 certificate_verify: bool = False, password_encrypted: bool = False,
                 timeout: int = 30):
        if not username or not password or not hostname:
            raise ValueError("Username, password, and hostname are required parameters")
        
        if not isinstance(port, int) or port <= 0:
            raise ValueError("Port must be a positive integer")
            
        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("Timeout must be a positive integer")
            
        self.url = f"https://{hostname}:{port}/webconsole/APIController"
        self.xml_login = f"""<Login><Username>{username}</Username><Password{" passwordform='encrypt'" if password_encrypted else ""}>{password}</Password></Login>"""
        self.session = requests.Session()
        self.session.verify = certificate_verify
        self.headers = {"Accept": "application/xml"}
        self.closed = False
        self.timeout = timeout
        
        if not certificate_verify:
            requests.packages.urllib3.disable_warnings()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if self.session is not None:
            self.session.close()
            self.session = None
            return {"status": "216", "message": "Session closed successfully.", "data": []}
        return {"status": "400", "message": "Session was already closed.", "data": []}

    def _format_xml_response(self, response, entity):
        response = response.get("Response", {})
        if "Status" in response:
            return {"status": response["Status"]["@code"], "message": response["Status"]["#text"], "data": []}
        if response.get("Login") and response["Login"].get("status") == "Authentication Failure":
            return {"status": "401", "message": response["Login"]["status"], "data": []}
        if entity in response:
            entity_data = response[entity]
            if "Status" in entity_data:
                if "@code" in entity_data["Status"]:
                    return {"status": entity_data["Status"]["@code"], "message": entity_data["Status"]["#text"], "data": []}
                elif entity_data["Status"] in ["No. of records Zero.", "Number of records Zero."]:
                    return {"status": "526", "message": "Record does not exist.", "data": []}
            entity_data = [entity_data] if isinstance(entity_data, dict) else entity_data
            entity_data = [{k: v for k, v in item.items() if k != "@transactionid"} for item in entity_data]
            return {"status": "216", "message": "Operation Successful.", "data": entity_data}
        return {"status": "404", "message": "Entity not found", "data": []}

    def _perform_action(self, xml_action: str, entity: str) -> ResponseType:
        if self.closed or self.session is None:
            return {"status": "400", "message": "Session is closed and cannot be used.", "data": []}

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
        except requests.Timeout:
            return {"status": "408", "message": f"Request timed out after {self.timeout} seconds", "data": []}
        except requests.ConnectionError:
            return {"status": "503", "message": "Connection error: Unable to connect to the firewall", "data": []}
        except requests.HTTPError as e:
            return {"status": str(e.response.status_code), "message": f"HTTP error: {str(e)}", "data": []}
        except xmltodict.expat.ExpatError:
            return {"status": "500", "message": "Invalid XML response from server", "data": []}
        except requests.RequestException as e:
            return {"status": "500", "message": f"Request failed: {str(e)}", "data": []}
        except Exception as e:
            return {"status": "500", "message": f"Unexpected error: {str(e)}", "data": []}

    def create(self, entity: str, entity_data: Dict[str, Any]) -> ResponseType:
        if not entity:
            return {"status": "400", "message": "Entity name cannot be empty", "data": []}
            
        if not isinstance(entity_data, dict):
            return {"status": "400", "message": "entity_data must be a dictionary.", "data": []}

        # Clean data for Services entity
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

    def read(self, entity: str, filter_value: Optional[str] = None, 
             filter_criteria: str = LIKE, filter_key_field: Optional[str] = None) -> ResponseType:
        if not entity:
            return {"status": "400", "message": "Entity name cannot be empty", "data": []}
            
        inner_xml = ""
        if filter_value:
            key_field = filter_key_field or "Name"
            inner_xml = f"""<Filter><key name="{key_field}" criteria="{filter_criteria}">{filter_value}</key></Filter>"""
            
        xml_action = f"""<Get><{entity}>{inner_xml}</{entity}></Get>"""
        return self._perform_action(xml_action, entity)

    def update(self, entity: str, entity_data: Dict[str, Any], 
               entity_name: Optional[str] = None, entity_name_key: str = "Name") -> ResponseType:
        if not entity:
            return {"status": "400", "message": "Entity name cannot be empty", "data": []}
            
        if not isinstance(entity_data, dict):
            return {"status": "400", "message": "entity_data must be a dictionary", "data": []}
            
        # Determine entity name
        if entity_name is None:
            if entity_name_key not in entity_data:
                return {
                    "status": "400",
                    "message": f"Entity data must contain '{entity_name_key}' field or provide entity_name parameter.",
                    "data": [],
                }
            entity_name = entity_data[entity_name_key]

        # Get existing entity
        existing_data = self.read(entity, entity_name, EQ, entity_name_key)
        if existing_data["status"] != "216" or not existing_data["data"]:
            return {"status": "404", "message": "Entity not found for update.", "data": []}
        if len(existing_data["data"]) > 1:
            return {"status": "400", "message": "Multiple entities found for update. Provide a unique entity_name.", "data": []}

        # Merge and update
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

    def delete(self, entity: str, filter_value: str, 
               filter_criteria: str = EQ, filter_key_field: Optional[str] = None) -> ResponseType:
        if not entity:
            return {"status": "400", "message": "Entity name cannot be empty", "data": []}
            
        if not filter_value:
            return {"status": "400", "message": "Filter value cannot be empty for delete operation", "data": []}
            
        # Handle special cases
        if entity == "FirewallRule":
            inner_xml = f"<Name>{filter_value}</Name>"
        elif entity == "LocalServiceACL":
            inner_xml = f"<RuleName>{filter_value}</RuleName>"
        else:
            key_field = filter_key_field or "Name"
            inner_xml = f'<Filter><key name="{key_field}" criteria="{filter_criteria}">{filter_value}</key></Filter>'

        xml_action = f"""<Remove><{entity}>{inner_xml}</{entity}></Remove>"""
        return self._perform_action(xml_action, entity)

    def batch_operation(self, operations: List[Dict[str, Any]], debug: bool = False) -> List[ResponseType]:
        if not operations:
            return [{"status": "400", "message": "Operations list cannot be empty", "data": []}]
            
        if not isinstance(operations, list):
            return [{"status": "400", "message": "Operations must be a list", "data": []}]
            
        results = []
        
        for index, op in enumerate(operations, start=1):
            if debug:
                print(f"Processing operation {index}/{len(operations)}: {op}")

            # Extract operation parameters
            action = op.get("action")
            entity = op.get("entity")
            
            # Validate required fields
            if not action or not entity:
                error_response = {"status": "400", "message": "Missing 'action' or 'entity' in operation", "data": []}
                if debug:
                    print(f"Error in operation {index}: {error_response}")
                results.append(error_response)
                continue

            try:
                # Execute appropriate action
                if action == "read":
                    result = self.read(
                        entity=entity, 
                        filter_value=op.get("filter_value"),
                        filter_criteria=op.get("filter_criteria", LIKE),
                        filter_key_field=op.get("filter_key_field")
                    )
                elif action == "create":
                    if "entity_data" not in op:
                        result = {"status": "400", "message": "Missing 'entity_data' for create operation", "data": []}
                    else:
                        result = self.create(entity=entity, entity_data=op.get("entity_data", {}))
                elif action == "update":
                    if "entity_data" not in op:
                        result = {"status": "400", "message": "Missing 'entity_data' for update operation", "data": []}
                    else:
                        result = self.update(
                            entity=entity, 
                            entity_data=op.get("entity_data", {}),
                            entity_name=op.get("entity_name"),
                            entity_name_key=op.get("entity_name_key", "Name")
                        )
                elif action == "delete":
                    if "filter_value" not in op:
                        result = {"status": "400", "message": "Missing 'filter_value' for delete operation", "data": []}
                    else:
                        result = self.delete(
                            entity=entity, 
                            filter_value=op.get("filter_value", ""),
                            filter_criteria=op.get("filter_criteria", EQ),
                            filter_key_field=op.get("filter_key_field")
                        )
                else:
                    result = {"status": "400", "message": f"Unsupported action: {action}", "data": []}

                if debug:
                    print(f"Result of operation {index} ({action}): {result}")
                results.append(result)

            except Exception as e:
                error_response = {"status": "500", "message": f"Operation failed: {str(e)}", "data": []}
                if debug:
                    print(f"Error in operation {index} ({action}): {error_response}")
                results.append(error_response)

        return results