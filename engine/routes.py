import os
import re

from werkzeug.routing import Rule, Map

from engine.jsonschemas import generate_json_schema
from utils.http_constants import *
from config.templates import route_template, routes_file_template, routes_import_template, schema_template
from engine.structure import create_file
from utils.unquoted_string import _


def route_handler_name(path, method):
    method_er = {GET: "getter", POST: "poster", PUT: "putter", PATCH: "patcher", DELETE: "deleter"}

    route_handler = path[8:] if path.startswith("/api/v1") else path
    route_handler = re.sub(r"/<[^>]+>", "_one", route_handler).replace("/", "_")
    route_handler += f"_{method_er[method]}"

    return route_handler


def generate_route_function(
    path: str, section, route_handler, method, desc, request, responses, pagination=None, snippet=None
):
    """Generate route functions based on path, method, and response codes, with response stubs for each"""
    rule_matcher = Rule(path, endpoint=route_handler)
    rule_matcher.bind(Map())
    params = ", ".join(rule_matcher.arguments)
    route_code = route_template.format(path=path, desc=desc, route_path=path[7:], method=method, section=section, route_handler=route_handler, route_handler_upper=route_handler.upper(), params=params, errors=', '.join(str(err) for err in sorted(responses) if str(err)[0] != '2'))
    if snippet is not None:
        route_code += "\n" + snippet + '\n\n'
        return route_code

    route_code += """
    user: User = getattr(g, 'user', None)
    if user is None:
        return jsonify({'error': _('unauthorized')}), 401
"""
    type_interpreter = {
        "int": lambda e: f'int({e})',
        "float": lambda e: f'float({e})',
        "str": lambda e: e,
        "url": lambda e: e,
        "datetime": lambda e: f'datetime.strptime({e}, time_fmt)'
    }
    for k, v in request.items():
        if k.endswith("?"):
            k = k.strip("?")
            route_code += f"    {k} = {type_interpreter[v](f"req['{k}']") if isinstance(v, str) else f'req.get(\'{k}\', None)'} if req.get('{k}', None) else None\n"
        else:
            route_code += f"    {k} = {type_interpreter[v](f"req['{k}']") if isinstance(v, str) else f'req[\'{k}\']'}\n"


    # Generate response stubs for each status code
    route_code += "\n    try:\n"
    for status, status_responses in responses.items():
        status_code = int(status)  # Default to the status as is (if numeric)

        # Add the responses for this status code
        for response in status_responses:
            route_code += f"        if False:  # Stub for {status_code} response\n"
            route_code += f"            return jsonify({response}), {status_code}\n"

    if pagination:
        route_code += f"""
        query = storage.query()
        return paginate("{pagination}", query, page, page_size, lambda u: u), 200
    except ValueError as e:
        data = e.args[0] if e.args and e.args[0] in ("page", "page_size") else "request"
        return jsonify({{"error": _("invalid", data=_(data))}}), 422
"""
    route_code += """    except Exception as e:
        print(f'[{e.__class__.__name__}]: {e}')
        abort(500)

"""
    return route_code


def generate_routes(project_name, endpoints):
    """Generate all the routes from the endpoints"""
    base_path = os.path.join(os.getcwd(), project_name)
    for section, paths in endpoints.items():
        routes = ""
        schemas = {}
        section_tags = []
        for path, methods in paths.items():
            for method, details in methods.items():
                request = details.get("request", {})
                responses = details.get("responses", {})
                desc = details.get("desc", "")
                snippet = details.get("snippet", None)
                pagination = details.get("pagination", None)
                tags = details.get('tags', [])
                section_tags.extend(tags)

                if pagination:
                    request.update(
                        {"page?": "int", "page_size?": "int", "query?": "str"}
                    )
                    responses[OK] = {
                        "total_pages": "int",
                        f"total_{pagination}": "int",
                        "next": "int",
                        "prev": "int",
                        pagination: [responses[OK]],
                    }
                    responses.update(
                        {
                            UNPROCESSABLE_ENTITY: {
                                "error": _("_('invalid', data=_('page'))")
                            },
                            UNPROCESSABLE_ENTITY: {
                                "error": _("_('invalid', data=_('page_size'))")
                            },
                        }
                    )

                route_handler = route_handler_name(path, method)
                routes += generate_route_function(
                    path,
                    section,
                    route_handler,
                    method,
                    desc,
                    request,
                    responses,
                    pagination,
                    snippet,
                )
                schemas[f"{route_handler.upper()}_SCHEMA"] = repr(
                    generate_json_schema(request)
                )

        routes_file_path = os.path.join(
            base_path, "api", "v1", "routes", section + ".py"
        )
        create_file(
            routes_file_path,
            routes_file_template.format(
                routes=routes, section=section, schemas=",\n    ".join(schemas.keys()), tags=', '.join(sorted(set(section_tags + ['User'])))
            ),
        )

        schemas_file_path = os.path.join(
            base_path, "api", "v1", "schemas", section + ".py"
        )
        create_file(
            schemas_file_path,
            schema_template.format(
                section=section,
                schemas="\n".join(f"{k} = {v}" for k, v in schemas.items()),
            ),
        )
    create_routes_init_file(project_name, list(endpoints.keys()))


def create_routes_init_file(project_name, section_names):
    routes_init_file = routes_import_template.format(routes_import='\n'.join(f'from api.v1.routes.{section} import *' for section in section_names))
    create_file(
        os.path.join(os.getcwd(), project_name, "api", "v1", "routes", "__init__.py"),
        routes_init_file,
    )
