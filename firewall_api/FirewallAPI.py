import requests
import xmltodict

# Constants for filter criteria
EQ = "="  # Equal to
NOT = "!="  # Not equal to
LIKE = "like"  # Like (for partial matches)


# Firewall class to interact with the Sophos Firewall
class Firewall:
    def __init__(self, username, password, hostname, port=4444, certificate_verify=False, password_encrypted=False):
        # Initialize the Firewall object with connection details
        # API endpoint
        self.url = f"https://{hostname}:{port}/webconsole/APIController"
        self.xml_login = f"""
            <Login>
                <Username>{username}</Username>
                <Password{" passwordform='encrypt'" if password_encrypted else ""}>{password}</Password>
            </Login>
        """  # XML login payload
        self.session = requests.Session()  # Create a session for persistent connections
        # Enable/disable SSL certificate verification
        self.session.verify = certificate_verify
        # Set headers to accept XML responses
        self.headers = {"Accept": "application/xml"}
        if not certificate_verify:
            # Disable SSL warnings if verification is off
            requests.packages.urllib3.disable_warnings()
        self.closed = False  # Track if the session is closed

    def __enter__(self):
        # Enable the use of 'with' statement for context management
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Ensure the session is closed when exiting the 'with' block
        self.close()

    def close(self):
        # Close the session if it's not already closed
        if not self.closed:
            if self.session:
                self.session.close()  # Close the session
                self.session = None
            self.closed = True
            return {"status": "200", "message": "Session closed successfully.", "data": []}
        else:
            return {"status": "400", "message": "Session was already closed.", "data": []}

    # Format the XML response from the firewall into a structured dictionary
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

            entity_data = [entity_data] if isinstance(
                entity_data, dict) else entity_data
            entity_data = [{k: v for k, v in item.items() if k != "@transactionid"}
                           for item in entity_data]

            return {"status": "216", "message": "Operation Successful.", "data": entity_data}

        return {"status": "404", "message": "Entity not found", "data": []}

    # Perform an action (e.g., CRUD operation) on the firewall
    def _perform_action(self, xml_action, entity):
        if self.closed:
            return {"status": "400", "message": "Session is closed and cannot be used.", "data": []}

        # Combine login and action XML
        full_request_xml = f"<Request>{self.xml_login}{xml_action}</Request>"

        try:
            response = self.session.post(self.url, headers=self.headers, data={
                                         "reqxml": full_request_xml}, timeout=30)
            response.raise_for_status()  # Raise an exception for HTTP errors
            # Parse and format response
            return self._format_xml_response(xmltodict.parse(response.content.decode()), entity)
        except requests.RequestException as e:
            return {"status": "500", "message": f"Request failed: {str(e)}", "data": []}

    # CRUD operations
    # CREATE method to add data to the firewall
    def create(self, entity, entity_data):
        # Validate that entity_data is a dictionary
        if not isinstance(entity_data, dict):
            return {"status": "400", "message": "entity_data must be a dictionary.", "data": []}

        # Generate the XML action for creating the entity
        xml_action = f"""
            <Set operation="add">
                <{entity}>{xmltodict.unparse(entity_data, full_document=False)}</{entity}>
            </Set>
        """

        # Perform the create action
        return self._perform_action(xml_action, entity)

    # READ method to fetch data from the firewall
    def read(self, entity, filter_value=None, filter_criteria=LIKE, filter_key_field=None):
        inner_xml = ""
        if filter_value:
            inner_xml = f"""
                <Filter>
                    <key name="{filter_key_field if filter_key_field else 'Name'}" criteria="{filter_criteria}">{filter_value}</key>
                </Filter>
            """  # Add filter criteria if provided

        xml_action = f"""<Get><{entity}>{inner_xml}</{entity}></Get>"""  # Generate the XML action for reading
        return self._perform_action(xml_action, entity)

    # UPDATE method to modify existing data in the firewall
    def update(self, entity, entity_data, entity_name=None, entity_name_key="Name"):
        # If entity_name is not provided, try to extract it from entity_data
        if entity_name is None:
            if entity_name_key not in entity_data:
                return {
                    "status": "400",
                    "message": f"Entity data must contain '{entity_name_key}' field or provide entity_name parameter.",
                    "data": [],
                }
            entity_name = entity_data[entity_name_key]
        # Fetch the existing entity using the entity_name
        existing_data = self.read(entity, entity_name, EQ, entity_name_key)
        # Check if the read operation was successful
        if existing_data["status"] != "216":
            return {"status": "404", "message": "Entity not found for update.", "data": []}
        # Ensure that only one entity matches the filter criteria
        if not existing_data["data"]:
            return {"status": "404", "message": "Entity not found for update.", "data": []}
        if len(existing_data["data"]) > 1:
            return {"status": "400", "message": "Multiple entities found for update. Provide a unique entity_name.", "data": []}
        # Extract the current entity data
        current_entity = existing_data["data"][0]
        # Merge  and replace existing data with new data
        updated_data = self._merge_entities(current_entity, entity_data)
        # Generate the XML action for the update
        xml_action = f"""
            <Set operation="update">
                <{entity}>{xmltodict.unparse(updated_data, full_document=False)}</{entity}>
            </Set>
        """
        # Perform the update action
        return self._perform_action(xml_action, entity)

    def _merge_entities(self, current_entity, new_entity):
        # Merge two entities, merging nested dictionaries and replacing other fields.
        for key, value in new_entity.items():
            if isinstance(value, dict) and isinstance(current_entity.get(key), dict):
                # Recursively merge nested dictionaries
                self._merge_entities(current_entity[key], value)
            else:
                current_entity[key] = value  # Replace non-dictionary fields
        return current_entity

    # DELETE method to remove data from the firewall
    def delete(self, entity, filter_value, filter_criteria=EQ, filter_key_field=None):
        # Generate the inner XML based on the entity type
        if entity == "FirewallRule":
            inner_xml = f"<Name>{filter_value}</Name>"
        elif entity == "LocalServiceACL":
            inner_xml = f"<RuleName>{filter_value}</RuleName>"
        else:
            filter_key_field = filter_key_field or "Name"  # Default if not provided
            inner_xml = f'<Filter><key name="{filter_key_field}" criteria="{filter_criteria}">{filter_value}</key></Filter>'

        xml_action = f"""<Remove><{entity}>{inner_xml}</{entity}></Remove>"""  # Generate the XML action for deletion
        return self._perform_action(xml_action, entity)
