
from utils.unquoted_string import _


def filter_empty(json):
    deleted = []
    if isinstance(json, dict):
        for k in json.keys():
            v = json[k]
            if isinstance(v, dict):
                v = json[k] = filter_empty(v)
            if len(v) == 0:
                deleted.append(k)
    for k in deleted:
        del json[k]
    return json    


def generate_json_schema(value, allow_additional=True):
    NON_BLANK_REGEX = r"^(?!\s*$).+"
    if isinstance(value, dict):
        body = {
            "type": "object",
            "properties": {},
            "required": [],
        }
        if not allow_additional:
            body["additionalProperties"] = False
        for k, v in value.items():
            if k.endswith("?"):
                schema = generate_json_schema(v)
                schema["type"] = [schema["type"], "null"]
                body["properties"][k[:-1]] = schema
            else:
                body["properties"][k] = generate_json_schema(v)
                if body["properties"][k]["type"] == "string":
                    body["properties"][k]["pattern"] = NON_BLANK_REGEX
                body["required"].append(k)
        return body
    elif isinstance(value, list):
        return {
            "type": "array",
            "items": generate_json_schema(value[0]) if value else {},
        }
    elif value == "int":
        return {"type": "integer"}
    elif value == "float":
        return {"type": "number"}
    elif value == "str" or type(value) is _:
        return {"type": "string"}
    elif value == "datetime":
        return {"type": "string", "format": "date-time"}
    elif value == "url":
        return {"type": "string", "format": "uri"}
    elif value == "email":
        return {"type": "string", "format": "email"}
    else:
        PATTERNS = {"uuid": r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"}
        return {"type": "string", "pattern": PATTERNS[value]}
