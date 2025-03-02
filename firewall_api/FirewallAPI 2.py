import requests
import xmltodict
import functools

# Define constants
EQ = "="
NOT = "!="
LIKE = "like"


# Define a decorator for session validation
def requires_active_session(func):
    """Decorator to check if the session is active before executing a method."""

    def wrapper(self, *args, **kwargs):
        if self.closed:
            return {"status": "400", "message": "Session is closed and cannot be used.", "data": []}
        return func(self, *args, **kwargs)

    return wrapper


class Firewall:
    def __init__(self, username, password, hostname, port=4444, certificate_verify=False, password_encrypted=False, timeout=30):
        """
        Initialize the Firewall object with connection details.

        :param username: Username for authentication.
        :param password: Password for authentication.
        :param hostname: Hostname of the firewall.
        :param port: Port number for the API connection (default is 4444).
        :param certificate_verify: Boolean to verify SSL certificates (default is False).
        :param password_encrypted: Boolean indicating if the password is encrypted (default is False).
        :param timeout: Request timeout in seconds (default is 30).
        """
        self.url = f"https://{hostname}:{port}/webconsole/APIController"
        self.xml_login = f"""
            <Login>
                <Username>{username}</Username>
                <Password{" passwordform='encrypt'" if password_encrypted else ""}>{password}</Password>
            </Login>
        """
        self.session = requests.Session()
        self.session.verify = certificate_verify
        self.headers = {"Accept": "application/xml"}
        self.timeout = timeout
        self.closed = False

        # Cache for frequently accessed entities
        self._cache = {}

        if not certificate_verify:
            requests.packages.urllib3.disable_warnings()

    def __enter__(self):
        """
        Enter the runtime context related to this object.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the runtime context related to this object.
        """
        self.close()

    def close(self):
        """
        Close the session if it is open.

        :return: A dictionary with the status and message of the operation.
        """
        if not self.closed:
            self.session.close()
            self.closed = True
            self._cache.clear()  # Clear cache on close
            return {"status": "200", "message": "Session closed successfully.", "data": []}
        return {"status": "400", "message": "Session was already closed.", "data": []}

    def clear_cache(self, entity=None):
        """
        Clear the cache for a specific entity or all entities.

        :param entity: The entity to clear from cache. If None, clears all cache.
        """
        if entity:
            self._cache.pop(entity, None)
        else:
            self._cache.clear()

    def _format_xml_response(self, response, entity):
        """
        Format the XML response from the API.

        :param response: The XML response from the API.
        :param entity: The entity to extract from the response.
        :return: A dictionary with the status, message, and data of the operation.
        """
        response = response.get("Response", {})

        # Check for error status
        if "Status" in response:
            return {"status": response["Status"]["@code"], "message": response["Status"]["#text"], "data": []}

        # Check for authentication failure
        if response.get("Login") and response["Login"].get("status") == "Authentication Failure":
            return {"status": "401", "message": response["Login"]["status"], "data": []}

        # Process entity data
        if entity in response:
            entity_data = response[entity]

            # Check for status in entity data
            if "Status" in entity_data:
                if "@code" in entity_data["Status"]:
                    return {"status": entity_data["Status"]["@code"], "message": entity_data["Status"]["#text"], "data": []}
                elif entity_data["Status"] in ["No. of records Zero.", "Number of records Zero."]:
                    return {"status": "526", "message": "Record does not exist.", "data": []}

            # Normalize entity data
            entity_data = [entity_data] if isinstance(entity_data, dict) else entity_data
            entity_data = [{k: v for k, v in item.items() if k != "@transactionid"} for item in entity_data]

            return {"status": "216", "message": "Operation Successful.", "data": entity_data}

        return {"status": "404", "message": "Entity not found", "data": []}

    @requires_active_session
    def _perform_action(self, xml_action, entity):
        """
        Perform an action by sending an XML request to the API.

        :param xml_action: The XML action to perform.
        :param entity: The entity to perform the action on.
        :return: A dictionary with the status, message, and data of the operation.
        """
        full_request_xml = f"<Request>{self.xml_login}{xml_action}</Request>"
        try:
            response = self.session.post(self.url, headers=self.headers, data={"reqxml": full_request_xml}, timeout=self.timeout)
            response.raise_for_status()
            parsed_response = xmltodict.parse(response.content.decode())
            return self._format_xml_response(parsed_response, entity)
        except requests.RequestException as e:
            return {"status": "500", "message": f"Request failed: {str(e)}", "data": []}
        except Exception as e:
            return {"status": "500", "message": f"Unexpected error: {str(e)}", "data": []}

    @requires_active_session
    def create(self, entity, entity_data):
        """
        Create a new entity in the firewall.

        :param entity: The type of entity to create.
        :param entity_data: The data for the entity to create.
        :return: A dictionary with the status, message, and data of the operation.
        """
        if not isinstance(entity_data, dict):
            return {"status": "400", "message": "entity_data must be a dictionary.", "data": []}

        # Only clean ports for "Services" entities
        if entity == "Services":
            entity_data = self._remove_spaces(entity_data)

        xml_action = f"""
            <Set operation="add">
                <{entity}>{xmltodict.unparse(entity_data, full_document=False)}</{entity}>
            </Set>
        """
        result = self._perform_action(xml_action, entity)

        # Clear cache for this entity type if operation was successful
        if result["status"] == "216":
            self.clear_cache(entity)

        return result

    def _remove_spaces(self, data):
        """
        Recursively removes spaces from string values in a dictionary or list.

        Args:
            data (dict, list, or str): The input data, which can be a dictionary, list,
                                        or string. The method processes nested dictionaries
                                        and lists recursively.

        Returns:
            The input data with spaces removed from string values (except for "Name",
            "Description", and "RuleName").
        """
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

    @requires_active_session
    def read(self, entity, filter_value=None, filter_criteria=LIKE, filter_key_field=None, use_cache=True):
        """
        Read an entity from the firewall.

        :param entity: The type of entity to read.
        :param filter_value: The value to filter the entity by.
        :param filter_criteria: The criteria to filter the entity (default is LIKE).
        :param filter_key_field: The key field to filter the entity by.
        :param use_cache: Whether to use cached results if available (default is True).
        :return: A dictionary with the status, message, and data of the operation.
        """
        # Generate cache key if using cache
        cache_key = None
        if use_cache and filter_value:
            cache_key = f"{entity}_{filter_key_field or 'Name'}_{filter_criteria}_{filter_value}"
            if cache_key in self._cache:
                return self._cache[cache_key]

        inner_xml = ""
        if filter_value:
            inner_xml = f"""
                <Filter>
                    <key name="{filter_key_field if filter_key_field else 'Name'}" criteria="{filter_criteria}">{filter_value}</key>
                </Filter>
            """
        xml_action = f"""<Get><{entity}>{inner_xml}</{entity}></Get>"""
        result = self._perform_action(xml_action, entity)

        # Cache successful results with a filter
        if use_cache and filter_value and result["status"] == "216":
            self._cache[cache_key] = result

        return result

    @requires_active_session
    def update(self, entity, entity_data, entity_name=None, entity_name_key="Name"):
        """
        Update an existing entity in the firewall.

        :param entity: The type of entity to update.
        :param entity_data: The new data for the entity.
        :param entity_name: The name of the entity to update.
        :param entity_name_key: The key field to identify the entity (default is "Name").
        :return: A dictionary with the status, message, and data of the operation.
        """
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
            return {"status": "404", "message": "Entity not found for update.", "data": []}
        if len(existing_data["data"]) > 1:
            return {"status": "400", "message": "Multiple entities found for update. Provide a unique entity_name.", "data": []}

        current_entity = existing_data["data"][0]
        updated_data = self._merge_entities(current_entity, entity_data)

        xml_action = f"""
            <Set operation="update">
                <{entity}>{xmltodict.unparse(updated_data, full_document=False)}</{entity}>
            </Set>
        """
        result = self._perform_action(xml_action, entity)

        # Clear cache for this entity if operation was successful
        if result["status"] == "216":
            self.clear_cache(entity)

        return result

    def _merge_entities(self, current_entity, new_entity):
        """
        Merge two entities, updating the current entity with new data.

        :param current_entity: The current entity data.
        :param new_entity: The new entity data to merge.
        :return: The merged entity data.
        """
        for key, value in new_entity.items():
            if isinstance(value, dict) and isinstance(current_entity.get(key), dict):
                self._merge_entities(current_entity[key], value)
            else:
                current_entity[key] = value

        return current_entity

    @requires_active_session
    def delete(self, entity, filter_value, filter_criteria=EQ, filter_key_field=None):
        """
        Delete an entity from the firewall.

        :param entity: The type of entity to delete.
        :param filter_value: The value to filter the entity by for deletion.
        :param filter_criteria: The criteria to filter the entity (default is EQ).
        :param filter_key_field: The key field to filter the entity by.
        :return: A dictionary with the status, message, and data of the operation.
        """
        if entity == "FirewallRule":
            inner_xml = f"<Name>{filter_value}</Name>"
        elif entity == "LocalServiceACL":
            inner_xml = f"<RuleName>{filter_value}</RuleName>"
        else:
            filter_key_field = filter_key_field or "Name"
            inner_xml = f'<Filter><key name="{filter_key_field}" criteria="{filter_criteria}">{filter_value}</key></Filter>'

        xml_action = f"""<Remove><{entity}>{inner_xml}</{entity}></Remove>"""
        result = self._perform_action(xml_action, entity)

        # Clear cache for this entity if operation was successful
        if result["status"] == "216":
            self.clear_cache(entity)

        return result

    def batch_operation(self, operations):
        """
        Perform multiple operations in sequence.

        :param operations: List of operation dictionaries with keys:
                          - 'action': One of 'create', 'read', 'update', 'delete'
                          - 'entity': Entity type
                          - 'data': Entity data (for create/update)
                          - Other parameters specific to the action
        :return: List of results for each operation
        """
        results = []
        for op in operations:
            action = op.pop("action", None)
            if not action:
                results.append({"status": "400", "message": "Missing 'action' in operation", "data": []})
                continue

            try:
                if action == "create":
                    results.append(self.create(**op))
                elif action == "read":
                    results.append(self.read(**op))
                elif action == "update":
                    results.append(self.update(**op))
                elif action == "delete":
                    results.append(self.delete(**op))
                else:
                    results.append({"status": "400", "message": f"Unknown action: {action}", "data": []})
            except Exception as e:
                results.append({"status": "500", "message": f"Operation failed: {str(e)}", "data": []})

        return results
