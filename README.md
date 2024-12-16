# **FastAPI Keycloak Auth** ![Version](https://img.shields.io/badge/version-1.0.0-blue) ![License](https://img.shields.io/badge/license-MIT-green)
<br>
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"  alt="Fast API"/>
<img src="https://img.shields.io/badge/Keycloak-103060?style=for-the-badge&logo=keycloak&logoColor=white"  alt="Keycloak"/>


A lightweight library to secure FastAPI APIs using Keycloak, enabling **Role-Based Access Control (RBAC)** with minimal configuration.

---

## **Features**

- Simple integration with Keycloak for FastAPI applications.
- Built-in support for Role-Based Access Control (RBAC) using Keycloak roles.
- Works seamlessly with both realm roles and client roles.
- Automatically decodes and validates JWT tokens.

---

## **Minimum Requirements**

- **Python**: 3.12 or higher
- **FastAPI**: 0.115.6 or higher
- **Keycloak**: 5.1.1 or higher

---

## **Installation**

Install the library using pip:

```bash
pip install fastapi-keycloak-auth
```

---

## **Usage Guide**

### **1. Initialize KeycloakAuth**

Start by initializing the `KeycloakAuth` instance with your Keycloak server configuration.
There are two ways that you can use to initialize the `KeycloakAuth` instance:

1. Providing keycloak configurations as arguments in the initializer

      ```python
      from keycloak_auth.keycloak_auth import KeycloakAuth
      
      auth = KeycloakAuth(
      server_url=KEYCLOAK_URL,
      client_id=KEYCLOAK_CLIENT_ID,
      realm_name=KEYCLOAK_REALM_NAME,
      client_secret_key=KEYCLOAK_CLIENT_SECRET,
      use_resource_access=True
      )
      ```
   Replace `KEYCLOAK_URL`, `KEYCLOAK_CLIENT_ID`, `KEYCLOAK_REALM_NAME`, and `KEYCLOAK_CLIENT_SECRET` with your Keycloak instance details.

    * `server_url`: The URL of your Keycloak server. Ex: `http://localhost:8080/auth/`
    * `client_id`: The client ID of your Keycloak client.
    * `realm_name`: The name of your Keycloak realm.
    * `client_secret_key`: The client secret of your Keycloak client.
    * `use_resource_access`: Set to `True` if you want to use client roles in RBAC instead of realm roles (Default is set to `False`).


2. Setting up Keycloak configurations as environmental variables (This method is recommended when this application is running in a containerized environment)

    ```python
    from keycloak_auth.keycloak_auth import KeycloakAuth
    import os
    
    os.environ['KEYCLOAK_URL'] = KEYCLOAK_URL
    os.environ['KEYCLOAK_CLIENT_ID'] = KEYCLOAK_CLIENT_ID
    os.environ['KEYCLOAK_REALM_NAME'] = KEYCLOAK_REALM_NAME
    os.environ['KEYCLOAK_CLIENT_SECRET'] = KEYCLOAK_CLIENT_SECRET
    
    auth = KeycloakAuth()
    ```
   Replace `KEYCLOAK_URL`, `KEYCLOAK_CLIENT_ID`, `KEYCLOAK_REALM_NAME`, and `KEYCLOAK_CLIENT_SECRET` with your Keycloak instance details.

    * `KEYCLOAK_URL`: The URL of your Keycloak server. Ex: `http://localhost:8080/auth/`
    * `KEYCLOAK_CLIENT_ID`: The client ID of your Keycloak client.
    * `KEYCLOAK_REALM_NAME`: The name of your Keycloak realm.
    * `KEYCLOAK_CLIENT_SECRET`: The client secret of your Keycloak client.

---

### **2. Protect Routes with Roles**

Use the `RolesAllowed` decorator to protect your FastAPI routes based on roles defined in Keycloak.
You can pass a list of roles that are allowed to access the route.

***Important Note:*** make sure to add `authorization: str | None = Header(default=None)` as a parameter in the route function to receive the JWT token.
Otherwise, the library will not be able to decode and validate the token.

```python
from fastapi import FastAPI, Header
from keycloak_auth.keycloak_auth import KeycloakAuth

app = FastAPI()

auth: KeycloakAuth = KeycloakAuth(
    server_url=KEYCLOAK_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM_NAME,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
    use_resource_access=True
)


@app.get('/admin')
@auth.RolesAllowed(['admin'])
async def admin_route(authorization: str | None = Header(default=None)):
    return {'message': 'Hello Admin'}


@app.get('/user')
@auth.RolesAllowed(['admin', 'user'])
async def user_route(authorization: str | None = Header(default=None)):
    return {'message': 'Hello User'}
```

[See Full Code Example](https://github.com/SahasPunchihewa/fastapi-keycloak-rbac-poc)

---

### **3. Additional Features**

1. You can also use the `KeycloakAuth` instance to decode and validate JWT tokens manually.

    ```python
    from keycloak_auth.keycloak_auth import KeycloakAuth

    auth = KeycloakAuth()
   
    token = auth.current_token
    ```

2. You can use the `KeycloakAuth` instance to get the current user's profile.

    ```python
    from keycloak_auth.keycloak_auth import KeycloakAuth

    auth = KeycloakAuth()
   
    user = auth.get_user_info()
    ```

---

### **4. Custom Error Handling**

The library automatically raises HTTPException for errors such as:

* `401 Unauthorized`: When the token is missing or expired.
* `403 Forbidden`: When the user does not have sufficient permissions.
* For advanced scenarios, you can implement additional error handling logic in your application.

## **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
