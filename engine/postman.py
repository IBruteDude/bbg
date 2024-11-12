import json
import requests as rs

# Helper function to create a Postman request
def create_request(method, path, desc, request_body=None, response_schema=None):
    request = {
        "name": f"{method} {path}",
        "request": {
            "method": method,
            "header": [],
            "url": {
                "raw": f"{{base_url}}{path}",
                "host": ["{{base_url}}"],
                "path": path.strip("/").split("/"),
            },
            "description": desc,
        },
        "response": [],
    }
    
    if request_body:
        request["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(request_body, indent=2),
            "options": {
                "raw": {
                    "language": "json"
                }
            }
        }

    if response_schema:
        request["response"].append({
            "name": "Example Response",
            "originalRequest": request["request"],
            "status": "OK",
            "code": 200,
            "body": json.dumps(response_schema, indent=4),
        })
    return request

def generate_postman_collection(project_name, endpoints, save_to_account=True):
    # Initialize an empty Postman collection
    collection = {
        "info": {
            "name": f"{project_name} API",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    # Loop through the spec to add each path/method to the collection
    for category, paths in endpoints.items():
        category_folder = {
            "name": category,
            "item": []
        }
        for path, methods in paths.items():
            folder = {
                "name": path[8:],
                "item": []
            }

            for method, details in methods.items():
                request_body = details.get("request", {})
                response_schema = details.get("responses", {}).get("OK", {})

                # Add request to the folder
                folder["item"].append(create_request(method, path, details["desc"], request_body, response_schema))

            # Add folder to the collection
            category_folder["item"].append(folder)
        
        collection["item"].append(category_folder)
        
    if save_to_account:
        postman_api_key = open('postman_api.key').readline()[:-1]
        response = rs.post(
            "https://api.getpostman.com/collections",
            headers={"X-Api-Key": postman_api_key, "Content-Type": "application/json"},
            json={'collection': collection}
        )
        print(response.status_code, response.json())
    else:
        with open(f'{project_name}.postman_collection.json', 'w') as f:
            json.dump(collection, f)

def create_test_request(name, path, method, request, status, response):
    # Postman request item structure
    item = {
        "name": name,
        "request": {
            "method": method,
            "header": [],
            "body": {
                "mode": "raw",
                "raw": json.dumps(request, indent=4),
                "options": {
                    "raw": {
                        "language": "json"
                    }
                }
            },
            "url": {
                "raw": path,
                "host": ["{{base_url}}"],  # Placeholder for base URL
                "path": path.strip("/").split("/")
            }
        },
        "response": []
    }
    # Add test cases in the form of scripts in Postman
    test_script = f"""
    pm.test("Status code is {status}", function () {{
        pm.response.to.have.status(200);
    }});
    pm.test("Response body matches expected", function () {{
        var expected = {json.dumps(response, indent=4)};
        pm.expect(pm.response.json()).to.deep.equal(expected);
    }});
    """
    item["event"] = [{
        "listen": "test",
        "script": {
            "type": "text/javascript",
            "exec": [test_script]
        }
    }]
    return item

def generate_postman_test_collection(project_name, tests, save_to_account=True):
    # Initialize an empty Postman collection
    collection = {
        "info": {
            "name": f"{project_name} API Test",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    # Loop through the spec to add each path/method to the collection
    for test in tests:
        name = test['name']
        path = test['path']
        method = test['method']
        request = test['request']
        status = test['status']
        response = test['response']
        
        pm_test = create_test_request(name, path, method, request, status, response)
        
        collection["item"].append(pm_test)

    if save_to_account:
        postman_api_key = open('postman_api.key').readline()[:-1]
        response = rs.post(
            "https://api.getpostman.com/collections",
            headers={"X-Api-Key": postman_api_key, "Content-Type": "application/json"},
            json={'collection': collection}
        )
        print(response.status_code, response.json())
    else:
        with open(f'{project_name}_test.postman_collection.json', 'w') as f:
            json.dump(collection, f)
