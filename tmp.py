from jinja2 import Template
import requests
import xmltodict

EQ = "="
NOT = "!="
LIKE = "like"


class Firewall:

    raw_templates_dict = {
        "create": """
        <Set operation="add"><{{ entity_type }}>{{ entity_data | safe }}</{{ entity_type }}></Set>
    """,
        "read": """
            {%- set entity_type_map = {
              'IPAddress': 'IPHost'
            } -%}
        <Get><{{ entity_type_map.get(entity_type,entity_type) }}>

            {%- set entity_map = {
                'LocalServiceACL': 'RuleName',
                'FirewallRule': 'Name',
                'IPAddress': 'IPAddress',
                'EntityType2': 'Type2',
                'EntityType3': 'Type3',
                'EntityType4': 'Type4',
                'EntityType5': 'Type5',
                'EntityType6': 'Type6',
                'EntityType7': 'Type7',
                'EntityType8': 'Type8',
                'EntityType9': 'Type9',
                'EntityType10': 'Type10'
            } -%}
            {%- if entity_data -%}
                <Filter><key name="{{ entity_map.get(entity_type, 'Name') }}" criteria="{{ filter_selector }}">{{ entity_data }}</key></Filter>
            {%- endif -%}
        </<{{ entity_type_map.get(entity_type,entity_type) }}></Get>
    """,
        "update": """
        <Set operation="update"><{{ entity_type }}>{{ entity_data | safe }}</{{ entity_type }}></Set>
    """,
        "delete": """
        <Remove><{{ entity_type }}>
            {%- set entity_map = {
                'FirewallRule': '<Name>{}</Name>',
                'LocalServiceACL': '<RuleName>{}</RuleName>',
                'EntityType1': '<Type1>{}</Type1>',
                'EntityType2': '<Type2>{}</Type2>',
                'EntityType3': '<Type3>{}</Type3>',
                'EntityType4': '<Type4>{}</Type4>',
                'EntityType5': '<Type5>{}</Type5>',
                'EntityType6': '<Type6>{}</Type6>',
                'EntityType7': '<Type7>{}</Type7>',
                'EntityType8': '<Type8>{}</Type8>',
                'EntityType9': '<Type9>{}</Type9>',
                'EntityType10': '<Type10>{}</Type10>'
            } -%}
            {%- if entity_type in entity_map -%}
                {{ entity_map[entity_type].format(entity_data) | safe }}
            {%- else -%}
                {%- if entity_data -%}
                    <Filter><key name="Name" criteria="{{ filter_selector }}">{{ entity_data }}</key></Filter>
                {%- endif -%}
            {%- endif -%}
        </{{ entity_type }}></Remove>
    """,
    }

    def __init__(self, username, password, hostname, port=4444, certificate_verify=False, password_encrypted=False):
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

        # Pre-compile Jinja2 templates
        self.templates_dict = {key: Template(template_str) for key, template_str in self.raw_templates_dict.items()}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _format_xml_response(self, response, entity_type):
        response = response.get("Response", {})

        if "Status" in response:
            formatted_response = {
                "status": response["Status"]["@code"],
                "message": response["Status"]["#text"],
            }
            return formatted_response  # Remove empty "data"

        if response.get("Login") and response["Login"].get("status") == "Authentication Failure":
            return {"status": "401", "message": response["Login"]["status"]}

        if entity_type in response:
            entity_data = response[entity_type]
            if "Status" in entity_data:
                if "@code" in entity_data["Status"]:
                    return {
                        "status": entity_data["Status"]["@code"],
                        "message": entity_data["Status"]["#text"],
                    }
                elif entity_data["Status"] in ["No. of records Zero.", "Number of records Zero."]:
                    return {"status": "526", "message": "Record does not exist."}

            entity_data = [entity_data] if isinstance(entity_data, dict) else entity_data
            entity_data = [{k: v for k, v in item.items() if k != "@transactionid"} for item in entity_data]

            return (
                {"status": "216", "message": "Operation Successful.", "data": entity_data}
                if entity_data
                else {"status": "216", "message": "Operation Successful."}
            )

        return {"status": "404", "message": "Entity not found"}

    # Remove extra spaces in dict value
    def _fix_data(self, data):
        if isinstance(data, dict):
            return {k: self._fix_data(v) if not (isinstance(v, str) and ":" in v) else v.replace(" ", "") for k, v in data.items()}
        elif isinstance(data, list):
            return [self._fix_data(item) for item in data]
        return data

    def _perform_action(self, action_template_key, entity_type, entity_data=None, filter_selector=None):
        if self.closed:
            return {"status": "400", "message": "Session is closed and cannot be used."}

        entity_data = self._fix_data(entity_data)  # fix minor formating problems

        # Use the pre-compiled template
        template_action = self.templates_dict[action_template_key]
        entity_data_xml = xmltodict.unparse(entity_data, full_document=False) if isinstance(entity_data, dict) else entity_data
        xml_action = template_action.render(entity_type=entity_type, entity_data=entity_data_xml, filter_selector=filter_selector)
        full_request_xml = f"<Request>{self.xml_login}{xml_action}</Request>"
        ########## Debugging
        print(full_request_xml)

        try:
            response = self.session.post(self.url, headers=self.headers, data={"reqxml": full_request_xml}, timeout=30)
            ########## Debugging
            # print(response.text)

            return self._format_xml_response(xmltodict.parse(response.content.decode()), entity_type)
        except requests.RequestException as e:
            return {"status": "500", "message": f"Request failed: {str(e)}"}

    def close(self):
        if not self.closed:
            if self.session:
                self.session.close()
                self.session = None
            self.closed = True
            return {"status": "200", "message": "Session closed successfully."}
        else:
            return {"status": "400", "message": "Session was already closed."}

    # CRUD Operations

    def create(self, entity_type, entity_data):
        return self._perform_action("create", entity_type, entity_data=entity_data)

    def read(self, entity_type, entity_data=None, filter_selector=LIKE):
        return self._perform_action("read", entity_type, entity_data, filter_selector)

    def update(self, entity_type, entity_data):
        return self._perform_action("update", entity_type, entity_data=entity_data)

    def delete(self, entity_type, entity_data=None, filter_selector=EQ):
        return self._perform_action("delete", entity_type, entity_data, filter_selector)
