import requests
import xmltodict

EQ = "="
NOT = "!="
LIKE = "like"

class Firewall:
    def __init__(self, username, password, hostname, port=4444, certificate_verify=False, password_encrypted=False):
        """
        Initialize the Firewall object with connection details.

        :param username: Username for authentication.
        :param password: Password for authentication.
        :param hostname: Hostname of the firewall.
        :param port: Port number for the API connection (default is 4444).
        :param certificate_verify: Boolean to verify SSL certificates (default is False).
        :param password_encrypted: Boolean indicating if the password is encrypted (default is False).
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
        if not certificate_verify:
            requests.packages.urllib3.disable_warnings()
        self.closed = False

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
            return {"status": "200", "message": "Session closed successfully.", "data": []}
        return {"status": "400", "message": "Session was already closed.", "data": []}

    def _format_xml_response(self, response, entity):
        """
        Format the XML response from the API.

        :param response: The XML response from the API.
        :param entity: The entity to extract from the response.
        :return: A dictionary with the status, message, and data of the operation.
        """
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

    def _perform_action(self, xml_action, entity):
        """
        Perform an action by sending an XML request to the API.

        :param xml_action: The XML action to perform.
        :param entity: The entity to perform the action on.
        :return: A dictionary with the status, message, and data of the operation.
        """
        if self.closed:
            return {"status": "400", "message": "Session is closed and cannot be used.", "data": []}
        full_request_xml = f"<Request>{self.xml_login}{xml_action}</Request>"
        try:
            response = self.session.post(self.url, headers=self.headers, data={"reqxml": full_request_xml}, timeout=30)
            response.raise_for_status()
            return self._format_xml_response(xmltodict.parse(response.content.decode()), entity)
        except requests.RequestException as e:
            return {"status": "500", "message": f"Request failed: {str(e)}", "data": []}

    def create(self, entity, entity_data):
        """
        Create a new entity in the firewall.

        :param entity: The type of entity to create.
        :param entity_data: The data for the entity to create.
        :return: A dictionary with the status, message, and data of the operation.
        """
        if not isinstance(entity_data, dict):
            return {"status": "400", "message": "entity_data must be a dictionary.", "data": []}
        xml_action = f"""
            <Set operation="add">
                <{entity}>{xmltodict.unparse(entity_data, full_document=False)}</{entity}>
            </Set>
        """
        return self._perform_action(xml_action, entity)

    def read(self, entity, filter_value=None, filter_criteria=LIKE, filter_key_field=None):
        """
        Read an entity from the firewall.

        :param entity: The type of entity to read.
        :param filter_value: The value to filter the entity by.
        :param filter_criteria: The criteria to filter the entity (default is LIKE).
        :param filter_key_field: The key field to filter the entity by.
        :return: A dictionary with the status, message, and data of the operation.
        """
        inner_xml = ""
        if filter_value:
            inner_xml = f"""
                <Filter>
                    <key name="{filter_key_field if filter_key_field else 'Name'}" criteria="{filter_criteria}">{filter_value}</key>
                </Filter>
            """
        xml_action = f"""<Get><{entity}>{inner_xml}</{entity}></Get>"""
        return self._perform_action(xml_action, entity)

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
        return self._perform_action(xml_action, entity)

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
        return self._perform_action(xml_action, entity)
