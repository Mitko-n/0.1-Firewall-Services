# Simple Sophos Firewall CRUD API 
#### version v 0.5.0
#
## General Informatin
This is the Sophos Firewall API, which simplifies the management of Sophos Firewall systems. API allows for CRUD operations, including create, read, update, and delete functions for all firewall entities. There is no guarantee that everything will run seamlessly, although the API has been designed to help streamline your daily firewall management tasks. Feel free to utilize our code, but please remember that the responsibility for any usage falls solely on the user.

***NOTE:***
Simple Sophos Firewall CRUD API is still under development.

***Currente library***  
```xgs_crud.py```    &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;utilises **request** library.  

***NEW Libary Release***  
```crud_httpx.py```    &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;utilises **httpx** library.  
```crud_requests.py``` &nbsp; &nbsp;utilises **requests** library. (the same as ```xgs_crud.py```)  
```crud_session.py```  &nbsp; &nbsp; &nbsp;utilises **requests** with **session** library.       
#
## How to Use
To view the entity structure, utilize the **```read(entity_type)```** method.\
The response obtained from this method can be used to generate data for the **```create(entity_type, entity_data)```** and **```update(entity_type, entity_data)```** methods.\
It's worth noting that while the syntax for **```read()```** and **```delete()```** are similar, their operations differ.
#
## Sophos Firewall password encryption

From Advanced Shell run:
```
aes-128-cbc-tool -k Th1s1Ss1mPlygR8API -t 1 -s <PASSWORD>
```
#
## Firewall CRUD API Description

### Entity Type
```python
entity_type = "FirewallRule"
entity_type = "IPHost"
```
### Respone Format
API response is Python Diction with following format:
```python
response = {
    "data":[
        {...},
        {...},
        ...,
        ], 
    "code":"<RESULT_CODE>", 
    "text":"<RESULT_DESCRIPTION_TEXT>",
    }
```

List of data elements:  **```response["data"]```**\
First data element: **```response["data"][0]```**\
Result code: **```response["code"]```**\
Result description text: **```response["text"]```**

### Initialization
```python
from xgs_crud import Firewall, EQ, NOT, LIKE
firewall = Firewall(username, password, firewall_ip)
firewall = Firewall(username, password, firewall_ip, password_encrypted)
firewall = Firewall(username, password, firewall_ip, port, password_encrypted)
```
### Create Entity
```python
response = firewall.create(entity_type, entity_data)
```
### Read Entity
```python
response = firewall.read(entity_type)
response = firewall.read(entity_type, entity_name)
response = firewall.read(entity_type, entity_name, filter_type)
```
### Update Entity
```python
response = firewall.update(entity_type, entity_data)
```
### Delete Entity
```python
response = firewall.delete(entity_type, entity_name)
response = firewall.delete(entity_type, entity_name, filter_type)
```
### Filter Type

```python
EQ      # matches entities with an exact name match
NOT     # matches entities where the name does not match at all
LIKE    # matches entities with partial name matches
```
Default Filter Type for ***Read Entity*** and ***Delete Entity*** is ***EQ***

## Examples
### Read/Download Entiy/Template
```python
response = firewall.read(entity_type)

response["code"]    # Result Code
response["text"]    # Result Description Text
response["data"]    # Result Data (List of Dict)
```
### Print All IPHost
```python
username = "<USER_NAME>"
password = "<PASSWORD>"
firewall_ip = "<IP_ADDRESS>"

firewall = Firewall(username, password, firewall_ip, password_encrypted=False)

entity_type = "IPHost"

response = firewall.read(entity_type)
print("Code:", response["code"], "Text:", response["text"])
for index, item in enumerate(response["data"], start=1):
    print(f"{index:002}: {item}")
```
### Create IPHost
```python
username = "<USER_NAME>"
password = "<PASSWORD>"
firewall_ip = "<IP_ADDRESS>"

firewall = Firewall(username, password, firewall_ip, password_encrypted=False)

entity_type = "IPHost"
entity_data = {
    "Name": "Host_172.16.17.100",
    "HostType": "IP",
    "IPAddress": "172.16.17.100",
}

firewall.create(entity_type, entity_data)
```
### Read all FirewallRules
```python
username = "<USER_NAME>"
password = "<PASSWORD>"
firewall_ip = "<IP_ADDRESS>"

firewall = Firewall(username, password, firewall_ip, password_encrypted=False)

entity_type = "FirewallRule"

response = firewall.read(entity_type)

print("Code:", response["code"], "Text:", response["text"])
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")
```
### Read all IPHost entities with entity_name in the Name
```python
username = "<USER_NAME>"
password = "<PASSWORD>"
firewall_ip = "<IP_ADDRESS>"

firewall = Firewall(username, password, firewall_ip, password_encrypted=False)
entity_type = "IPHost"
entity_name = "Internet"

print(f"\nREAD :: {entity_type} entity with {entity_name} in the 'Name'")
response = firewall.read(entity_type, entity_name, LIKE)    # LIKE
print("Code:", response["code"], "Text:", response["text"])
for index, item in enumerate(response["data"], start=1):
    print(f"{index:03}: {item}")

```