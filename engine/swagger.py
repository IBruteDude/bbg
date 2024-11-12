import os
import yaml
from werkzeug.routing import Rule, Map

from engine.jsonschemas import filter_empty, generate_json_schema
from engine.routes import route_handler_name
from utils.http_constants import status_code

def generate_yaml_files(base_path, endpoints):

    base_dir = os.path.join(base_path, "api", "v1", "routes", "documentation")
    for resource, paths in endpoints.items():
        for path, methods in paths.items():
            for method, details in methods.items():
                method_info = {
                    "responses": {},
                }
                tags = details.get("tags", None)
                parameters = []
                
                rule_matcher = Rule(path)
                rule_matcher.bind(Map())
                url_params = ({'name': param, 'in': 'path', 'type': 'string', 'required': True} for param in  rule_matcher.arguments)

                parameters.extend(url_params)

                # Convert request schema using your JSON Schema converter
                if "request" in details:
                    request_schema = generate_json_schema(details["request"])
                    parameters.append(
                        {
                            "name": "body",
                            "in": "query",
                            "required": True,
                            "schema": request_schema,
                        }
                    )
                
                if parameters:
                    method_info["parameters"] = parameters

                # Convert response schemas
                for response_code, response_details in details["responses"].items():
                    response_schema = generate_json_schema(response_details)
                    method_info["responses"][response_code] = {
                        "description": status_code[response_code],
                        "schema": response_schema,
                    }

                # Add method info to paths
                yaml_filename = os.path.join(base_dir, resource, f"{route_handler_name(path, method)}.yml")
                os.makedirs(os.path.dirname(yaml_filename), exist_ok=True)


                # Save the YAML content to a file
                with open(yaml_filename, "w") as yaml_file:
                    yaml_file.write(f"""{details["desc"].capitalize()}
---
path: {path}
{"tags:\n"+ '\n'.join(f'- {tag}' for tag in tags) if tags else ""}
""")
                    yaml.dump(filter_empty(method_info), yaml_file, default_flow_style=False)

