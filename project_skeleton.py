import sys
import os
import re
import shutil as su
import json
from typing import List, Optional

from pydantic import Field


GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"

CONTINUE = 100  # Continue
SWITCHING_PROTOCOLS = 101  # Switching Protocols
PROCESSING = 102  # Processing
EARLY_HINTS = 103  # Early Hints
CHECKPOINT = 103  # Checkpoint
OK = 200  # OK
CREATED = 201  # Created
ACCEPTED = 202  # Accepted
NON_AUTHORITATIVE_INFORMATION = 203  # Non-Authoritative Information
NO_CONTENT = 204  # No Content
RESET_CONTENT = 205  # Reset Content
PARTIAL_CONTENT = 206  # Partial Content
MULTI_STATUS = 207  # Multi-Status
ALREADY_REPORTED = 208  # Already Reported
IM_USED = 226  # IM Used
MULTIPLE_CHOICES = 300  # Multiple Choices
MOVED_PERMANENTLY = 301  # Moved Permanently
FOUND = 302  # Found
MOVED_TEMPORARILY = 302  # Moved Temporarily
SEE_OTHER = 303  # See Other
NOT_MODIFIED = 304  # Not Modified
USE_PROXY = 305  # Use Proxy
TEMPORARY_REDIRECT = 307  # Temporary Redirect
PERMANENT_REDIRECT = 308  # Permanent Redirect
BAD_REQUEST = 400  # Bad Request
UNAUTHORIZED = 401  # Unauthorized
PAYMENT_REQUIRED = 402  # Payment Required
FORBIDDEN = 403  # Forbidden
NOT_FOUND = 404  # Not Found
METHOD_NOT_ALLOWED = 405  # Method Not Allowed
NOT_ACCEPTABLE = 406  # Not Acceptable
PROXY_AUTHENTICATION_REQUIRED = 407  # Proxy Authentication Required
REQUEST_TIMEOUT = 408  # Request Timeout
CONFLICT = 409  # Conflict
GONE = 410  # Gone
LENGTH_REQUIRED = 411  # Length Required
PRECONDITION_FAILED = 412  # Precondition Failed
PAYLOAD_TOO_LARGE = 413  # Payload Too Large
REQUEST_ENTITY_TOO_LARGE = 413  # Request Entity Too Large
URI_TOO_LONG = 414  # URI Too Long
REQUEST_URI_TOO_LONG = 414  # Request-URI Too Long
UNSUPPORTED_MEDIA_TYPE = 415  # Unsupported Media Type
REQUESTED_RANGE_NOT_SATISFIABLE = 416  # Requested range not satisfiable
EXPECTATION_FAILED = 417  # Expectation Failed
I_AM_A_TEAPOT = 418  # I'm a teapot
INSUFFICIENT_SPACE_ON_RESOURCE = 419  # Insufficient Space On Resource
METHOD_FAILURE = 420  # Method Failure
DESTINATION_LOCKED = 421  # Destination Locked
UNPROCESSABLE_ENTITY = 422  # Unprocessable Entity
LOCKED = 423  # Locked
FAILED_DEPENDENCY = 424  # Failed Dependency
TOO_EARLY = 425  # Too Early
UPGRADE_REQUIRED = 426  # Upgrade Required
PRECONDITION_REQUIRED = 428  # Precondition Required
TOO_MANY_REQUESTS = 429  # Too Many Requests
REQUEST_HEADER_FIELDS_TOO_LARGE = 431  # Request Header Fields Too Large
UNAVAILABLE_FOR_LEGAL_REASONS = 451  # Unavailable For Legal Reasons
INTERNAL_SERVER_ERROR = 500  # Internal Server Error
NOT_IMPLEMENTED = 501  # Not Implemented
BAD_GATEWAY = 502  # Bad Gateway
SERVICE_UNAVAILABLE = 503  # Service Unavailable
GATEWAY_TIMEOUT = 504  # Gateway Timeout
HTTP_VERSION_NOT_SUPPORTED = 505  # HTTP Version not supported
VARIANT_ALSO_NEGOTIATES = 506  # Variant Also Negotiates
INSUFFICIENT_STORAGE = 507  # Insufficient Storage
LOOP_DETECTED = 508  # Loop Detected
BANDWIDTH_LIMIT_EXCEEDED = 509  # Bandwidth Limit Exceeded
NOT_EXTENDED = 510  # Not Extended
NETWORK_AUTHENTICATION_REQUIRED = 511  # Network Authentication Required


class _expr:
    def __init__(self, s):
        self.s = str(s)

    def __repr__(self):
        return self.s


endpoints = {
    "index": {
        "/api/v1/status": {
            GET: {
                "desc": "report the api status",
                "request": {},
                "responses": {OK: {"status": "str"}},
            }
        },
        "/api/v1/stats": {
            GET: {
                "desc": "report statistics about api uptime and workload",
                "request": {},
                "responses": {
                    OK: {"online_users": "int"},
                    UNAUTHORIZED: {},
                },
            }
        },
    },
    "user_auth": {
        "/api/v1/auth/signup": {
            POST: {
                "desc": "create a new user account",
                "request": {
                    "email": "str",
                    "password": "str",
                    "first_name": "str",
                    "last_name": "str",
                    "user_name": "str",
                    "profile_picture?": "url",
                },
                "responses": {
                    # account created successfully
                    CREATED: {},
                    CONFLICT: {"error": _expr("_('duplicate', data=_('email'))")},
                    CONFLICT: {"error": _expr("_('duplicate', data=_('user_name'))")},
                    BAD_REQUEST: {
                        "error": _expr("_('incomplete', data=_('login details'))")
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('login details'))")
                    },
                },
            }
        },
        "/api/v1/auth/login": {
            POST: {
                "desc": "create a new session for the user and log in",
                "request": {"email": "str", "password": "str"},
                "responses": {
                    OK: {},
                    UNAUTHORIZED: {
                        "error": _expr("_('invalid', data=_('login details'))")
                    },
                },
            }
        },
        "/api/v1/auth/password/reset": {
            GET: {
                "desc": "send a password reset email",
                "request": {},
                "responses": {
                    OK: {},
                    UNAUTHORIZED: {"error": _expr("_('unauthorized')")},
                },
            }
        },
        "/api/v1/auth/password/reset/confirm": {
            POST: {
                "desc": "confirm password reset",
                "request": {"reset_token": "str", "new_password": "str"},
                "responses": {
                    OK: {},
                    BAD_REQUEST: {
                        "error": _expr("_('invalid', data=_('token or password'))")
                    },
                },
            }
        },
        "/api/v1/auth/logout": {
            DELETE: {
                "desc": "remove user session and log out",
                "request": {},
                "responses": {
                    NO_CONTENT: {},
                    UNAUTHORIZED: {"error": _expr("_('unauthorized')")},
                },
            }
        },
        "/api/v1/auth/deactivate": {
            DELETE: {
                "desc": "delete user account",
                "request": {},
                "responses": {
                    NO_CONTENT: {},
                    UNAUTHORIZED: {"error": _expr("_('unauthorized')")},
                },
            }
        },
    },
    "user_profile": {
        "/api/v1/user/profile": {
            GET: {
                "desc": "respond with user profile details",
                "request": {},
                "responses": {
                    OK: {
                        "user": {
                            "email": "str",
                            "first_name": "str",
                            "last_name": "str",
                            "user_name": "str",
                            "profile_picture": "url",
                        }
                    },
                },
            },
            PUT: {
                "desc": "change user profile details",
                "request": {
                    "first_name?": "str",
                    "last_name?": "str",
                    "user_name?": "str",
                    "profile_picture?": "url",
                },
                "responses": {
                    OK: {},
                    BAD_REQUEST: {"error": _expr("_('invalid', data=_('profile'))")},
                    CONFLICT: {"error": _expr("_('duplicate', data=_('user_name'))")},
                },
            },
        },
        "/api/v1/user/profile/quiz/<quiz_id>": {
            GET: {
                "desc": "respond with all user's quiz attempts",
                "pagination": "attempts",
                "request": {},
                "responses": {
                    OK: {"attempt_id": "int", "time": "datetime", "score": "int"},
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('quiz'))")},
                    GONE: {"error": _expr("_('deleted', data=_('quiz'))")},
                    FORBIDDEN: {"error": _expr("_('quiz time has ended')")},
                },
            },
            POST: {
                "desc": "submit user answers for the quiz's questions",
                "request": {"answers": [{"options": ["int"]}]},
                "responses": {
                    OK: {
                        "correct_answers": [
                            {
                                "score": "int",
                                "answers": [{"options": ["int"]}],
                            }
                        ]
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('quiz'))")},
                },
            },
        },
        "/api/v1/user/profile/group": {
            GET: {
                "desc": "respond with all the user's subscribed groups",
                "pagination": "groups",
                "request": {},
                "responses": {
                    OK: {"group_id": "int", "group_title": "str"},
                },
            },
            POST: {
                "desc": "subscribe the user to the group",
                "request": {"group_id": "int"},
                "responses": {
                    OK: {"groups": [{"group_id": "int", "group_title": "str"}]},
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('group'))")},
                    CONFLICT: {"error": _expr("_('already subscribed to group')")},
                    GONE: {"error": _expr("_('deleted', data=_('group'))")},
                },
            },
        },
    },
    "user_groups": {
        "/api/v1/user/group": {
            GET: {
                "desc": "respond with all the user's own groups",
                "pagination": "groups",
                "request": {},
                "responses": {
                    OK: {"group_id": "int", "group_title": "str"},
                },
            },
            POST: {
                "desc": "create a user group",
                "request": {"title": "str"},
                "responses": {
                    CREATED: {},
                    CONFLICT: {"error": _expr("_('duplicate', data=_('title'))")},
                },
            },
        },
        "/api/v1/user/group/<group_id>": {
            PUT: {
                "desc": "update user group details",
                "request": {"title": "str"},
                "responses": {
                    OK: {},
                    CONFLICT: {"error": _expr("_('duplicate', data=_('title'))")},
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('group'))")},
                },
            },
            DELETE: {
                "desc": "delete a user group",
                "request": {},
                "responses": {
                    NO_CONTENT: {},
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('group'))")},
                },
            },
        },
        "/api/v1/user/group/<group_id>/users": {
            GET: {
                "desc": "get all the group subscribed users",
                "pagination": "users",
                "request": {},
                "responses": {
                    OK: {
                        "user_id": "int",
                        "user_name": "int",
                        "total_score": "int",
                        "attempted_quizzes": [{"quiz_id": "int"}],
                    },
                    # group not found
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('group'))")},
                },
            },
            POST: {
                "desc": "add users to a group",
                "request": {"users": [{"user_id": "int"}]},
                "responses": {
                    # user added successfully
                    CREATED: {},
                    # group not found
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('group'))")},
                    # user already in group
                    CONFLICT: {"error": _expr("_('duplicate', data=_('user'))")},
                },
            },
            DELETE: {
                "desc": "remove users from group",
                "request": {"users": [{"user_id": "int"}]},
                "responses": {
                    NO_CONTENT: {},
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('group'))")},
                    CONFLICT: {"error": _expr("_('duplicate', data=_('user'))")},
                },
            },
        },
    },
    "user_quizzes": {
        "/api/v1/user/quiz": {
            GET: {
                "desc": "respond with the user's created quizzes",
                "pagination": "quizzes",
                "request": {
                    "category?": "str",
                    "sort_by?": "str",
                    "difficulty?": "int",
                },
                "responses": {
                    OK: {
                        "quiz_id": "int",
                        "title": "str",
                        "category": "str",
                        "difficulty": "int",
                        "points": "int",
                        "duration": "int",
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('category'))")},
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('sort key'))")
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('difficulty'))")
                    },
                },
            },
            POST: {
                "desc": "create a new quiz for user",
                "request": {
                    "title": "str",
                    "category": "str",
                    "difficulty": "int",
                    "points": "int",
                    "duration?": "int",
                    "start?": "datetime",
                    "end?": "datetime",
                    "group_id?": "int",
                },
                "responses": {
                    CREATED: {},
                    BAD_REQUEST: {"error": _expr("_('incomplete', data=_('quiz'))")},
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('category'))")},
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('group'))")},
                    CONFLICT: {"error": _expr("_('duplicate', data=_('title'))")},
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('duration'))")
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('points'))")
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('quiz schedule'))")
                    },
                },
            },
        },
        "/api/v1/user/quiz/<quiz_id>": {
            PUT: {
                "desc": "modify the quiz details",
                "request": {
                    "title?": "str",
                    "category?": "str",
                    "difficulty?": "int",
                    "points?": "int",
                    "duration?": "int",
                    "start?": "datetime",
                    "end?": "datetime",
                    "group_id?": "int",
                },
                "responses": {
                    OK: {},
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('category'))")},
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('group'))")},
                    CONFLICT: {"error": _expr("_('duplicate', data=_('title'))")},
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('duration'))")
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('points'))")
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('quiz schedule'))")
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('quiz'))")},
                },
            },
            DELETE: {
                "desc": "delete the user's quiz",
                "request": {},
                "responses": {
                    NO_CONTENT: {},
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('quiz'))")},
                },
            },
        },
        "/api/v1/user/quiz/<quiz_id>/question": {
            GET: {
                "desc": "respond with the quiz's list of questions",
                "request": {},
                "responses": {
                    OK: {
                        "questions": [
                            {
                                "statement": "str",
                                "points": "int",
                                "type": "str",
                                "options": ["str"],
                                "correct_answer": ["int"],
                            }
                        ]
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('quiz'))")},
                },
            },
            POST: {
                "desc": "add questions to the quiz",
                "request": {
                    "questions": [
                        {
                            "statement": "str",
                            "points": "int",
                            "type": "str",
                            "options": ["str"],
                            "correct_answer": ["int"],
                        }
                    ]
                },
                "responses": {
                    CREATED: {},
                    BAD_REQUEST: {"error": _expr("_('missing', data=_('answers'))")},
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('question type'))")
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('points'))")
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('answer option'))")
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('quiz'))")},
                },
            },
            PUT: {
                "desc": "modify the quiz's questions",
                "request": {
                    "questions": [
                        {
                            "number": "int",
                            "statement?": "str",
                            "points?": "int",
                            "type?": "str",
                            "options?": ["str"],
                            "correct_answer?": ["int"],
                        }
                    ]
                },
                "responses": {
                    OK: {
                        "success": _expr(
                            "_('success', action=_('update'), data=_('question'))"
                        )
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('question number'))")
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('question type'))")
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('points'))")
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('answer option'))")
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('quiz'))")},
                },
            },
            DELETE: {
                "desc": "remove questions from the quiz",
                "request": {"question": [{"number": "int"}]},
                "responses": {
                    NO_CONTENT: {},
                    NOT_FOUND: {
                        "error": _expr("_('invalid', data=_('question number'))")
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('quiz'))")},
                },
            },
        },
        "/api/v1/user/quiz/<quiz_id>/stats/attempts": {
            GET: {
                "desc": "respond with stats about the user attempts of the quiz",
                "pagination": "attempts",
                "request": {},
                "responses": {
                    OK: {
                        "user_id": "int",
                        "user_name": "str",
                        "attempt_id": "int",
                        "time": "datetime",
                        "points": "int",
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('quiz'))")},
                },
            }
        },
        "/api/v1/user/quiz/<quiz_id>/stats/question/<question_id>": {
            GET: {
                "desc": "respond with stats about the user attempts of a quiz's question",
                "pagination": "question_answers",
                "request": {},
                "responses": {
                    OK: {
                        "correct_answers": "int",
                        "wrong_answers": ["int"],
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('quiz'))")},
                },
            }
        },
    },
    "profiles": {
        "/api/v1/profile": {
            GET: {
                "desc": "respond with quizzes with different filters",
                "pagination": "users",
                "request": {},
                "responses": {
                    OK: {
                        "user_id": "int",
                        "user_name": "str",
                    },
                },
            },
        },
        "/api/v1/profile/<user_id>": {
            GET: {
                "desc": "respond with user profile info",
                "request": {},
                "responses": {
                    OK: {
                        "user_name": "str",
                        "owned_groups": "int",
                        "created_quizzes": "int",
                        "subscribed_groups": "int",
                        "solved_quizzes": "int",
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('user'))")}
                }
            },
        },
        "/api/v1/profile/<user_id>/quiz": {
            GET: {
                "desc": "respond with the user's created quizzes",
                "pagination": "quizzes",
                "request": {
                    "category?": "str",
                    "sort_by?": "str",
                    "difficulty?": "int",
                },
                "responses": {
                    OK: {
                        "quiz_id": "int",
                        "title": "str",
                        "category": "str",
                        "difficulty": "int",
                        "points": "int",
                        "duration": "int",
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('category'))")},
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('sort key'))")
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('difficulty'))")
                    }
                },
            }
        }
    },
    "quizzes": {
        "/api/v1/quiz": {
            GET: {
                "desc": "respond with quizzes with different filters",
                "pagination": "quizzes",
                "request": {
                    "category?": "str",
                    "sort_by?": "str",
                    "difficulty?": "int",
                },
                "responses": {
                    OK: {
                        "quiz_id": "int",
                        "title": "str",
                        "category": "str",
                        "difficulty": "int",
                        "points": "int",
                        "duration?": "int",
                        "start?": "datetime",
                        "end?": "datetime",
                        "group_id?": "int",
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('category'))")},
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('sort key'))")
                    },
                    UNPROCESSABLE_ENTITY: {
                        "error": _expr("_('invalid', data=_('difficulty'))")
                    },
                },
            },
        },
        "/api/v1/quiz/<quiz_id>": {
            GET: {
                "desc": "respond with the quiz's list of questions",
                "request": {},
                "responses": {
                    OK: {
                        "questions": [
                            {
                                "statement": "str",
                                "points": "int",
                                "type": "str",
                                "options": ["str"],
                            }
                        ]
                    },
                    GONE: {"error": _expr("_('deleted', data=_('quiz'))")},
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('quiz'))")},
                },
            },
        },
        "/api/v1/quiz/<quiz_id>/stats": {
            GET: {
                "desc": "respond with stats about the user attempts of the quiz",
                "request": {},
                "responses": {
                    OK: {
                        "max_score": "float",
                        "min_score": "float",
                        "average_score": "float",
                        "attempts": "int",
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('quiz'))")},
                },
            }
        },
    },
    "groups": {
        "/api/v1/group": {
            GET: {
                "desc": "respond with a list of available user groups",
                "pagination": "groups",
                "request": {},
                "responses": {
                    OK: {
                        "group_id": "int",
                        "title": "str",
                        "owner_id": "int",
                        "owner_name": "str",
                    },
                },
            }
        },
        "/api/v1/group/<group_id>/users": {
            GET: {
                "desc": "respond with a list of the groups subscribed users",
                "pagination": "users",
                "request": {
                    "sort_by?": "str",
                    "status?": "str",
                    "max_score?": "int",
                    "min_score?": "int",
                },
                "responses": {
                    OK: {
                        "user_id": "int",
                        "user_name": "str",
                        "status": "str",
                        "score": "int",
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('group'))")},
                    FORBIDDEN: {"error": _expr("_('unauthorized')")},
                },
            },
        },
        "/api/v1/group/<group_id>/quizzes": {
            GET: {
                "desc": "respond with all the schedualed quizzes",
                "pagination": "quizzes",
                "request": {},
                "responses": {
                    OK: {
                        "quiz_id": "int",
                        "title": "str",
                        "start": "datetime",
                        "end": "datetime",
                    },
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('group'))")},
                },
            }
        },
    },
}


# Define base project structure
project_structure = {
    "api": {
        "v1": {
            "templates": {},
            "static": {},
            "translations": {},
            "routes": {"documentation": {}, "__init__.py": "", "index.py": ""},
            "schemas": {"__init__.py": ""},
            "auth": {"__init__.py": "", "auth.py": ""},
            "utils": {"__init__.py": ""},
            "app.py": "",
            "babel.cfg": "[python: **.py]\n[jinja2: **/templates/**.html]\n",
        }
    },
    "models": {
        "__init__.py": "",
        "engine": {"__init__.py": ""},
    },
    "tests": {
        "__init__.py": "",
        "test_api": {
            "v1": {
                "test_routes": {"__init__.py": "", "test_index.py": ""},
                "test_auth": {"__init__.py": "", "test_auth.py": ""},
                "test_utils": {"__init__.py": ""},
                "test_app.py": "",
            }
        },
        "test_models": {
            "test_engine": {
                "test_db_storage.py": "",
                "test_cache_storage.py": "",
            }
        },
    },
    "config.py": "",
    "requirements.txt": "",
}

for k in project_structure["models"]:
    if k not in {"__init__.py", "engine"}:
        project_structure["api"]["v1"]["routes"]["documentation"][k[:-3]] = {
            "__init__.py"
        }

route_template = """from flask import jsonify, request
from flask_babel import _

from api.v1.routes import app_routes
from api.v1.schemas import json_validate
from api.v1.schemas.{section} import (
    {schemas}
)

{routes}
"""

schema_template = """\"\"\"JSON request validation schemas for the {section} endpoints
\"\"\"

{schemas}
"""


# Helper function to create directories and files
def create_file(path, content=""):
    """Create a file and write content to it"""
    with open(path, "w") as f:
        f.write(content)


def create_directories(base_path, structure):
    """Recursively create directories and files based on the structure"""
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):  # it's a directory
            os.makedirs(path, exist_ok=True)
            create_directories(path, content)
        else:  # it's a file
            create_file(path, content)


def create_test_directories(root, rel_path, structure):
    """Recursively creates directories and files based on the structure."""
    for name, content in structure.items():
        path = os.path.join(rel_path, "test_" + name)
        abs_path = os.path.join(root, path)
        if (
            isinstance(content, dict)
            and not any(abs_path.endswith(name) for name in ["tests"])
            and len(content.keys()) > 0
        ):  # it's a directory
            os.makedirs(abs_path, exist_ok=True)
            create_test_directories(root, path, content)
        elif isinstance(content, str) and not abs_path.endswith("__init__.py"):
            create_file(abs_path, content)


def generate_json_schema(value, allow_additional=True):
    if isinstance(value, dict):
        body = {
            "type": "object",
            "properties": {},
            "required": [],
        }
        if not allow_additional:
            body["additionalProperties"] = False
        for k, v in value.items():
            if k.endswith('?'):
                body["properties"][k[:-1]] = generate_json_schema(v)
            else:
                body["properties"][k] = generate_json_schema(v) 
                body["required"].append(k)
        return body
    elif isinstance(value, list):
        return {
            "type": "array",
            "items": generate_json_schema(value[0]) if value else {}
        }
    elif value == "int":
        return {"type": "integer"}
    elif value == "float":
        return {"type": "integer"}
    elif value == "str":
        return {"type": "string"}
    else:
        PATTERNS = {'datetime': r"", 'url': r"^(https?|ftp|file)://([-a-zA-Z0-9@:%._+~#=]{2,256})(:[0-9]+)?(/[-a-zA-Z0-9@:%._+~#=]*)*$"}
        return {"type": "string", "pattern": PATTERNS[value]}


def route_handler_name(path, method):
    method_er = {GET: "getter", POST: "poster", PUT: "putter", DELETE: "deleter"}

    route_handler = path[8:] if path.startswith("/api/v1") else path
    route_handler = re.sub(r"/<[^>]+>", "", route_handler).replace('/', '_')
    route_handler += f'_{method_er[method]}'

    return route_handler
    


def generate_route_function(path: str, route_handler, method, desc, request, responses, snippet=None):
    """Generate route functions based on path, method, and response codes, with response stubs for each"""
    route_code = (
        f'@app_routes.route("{path}", methods=["{method}"], strict_slashes=False)\n'
    )

    from werkzeug.routing import Rule, Map

    rule_matcher = Rule(path, endpoint=route_handler)
    rule_matcher.bind(Map())
    params = ", ".join(rule_matcher.arguments)
    route_code += f"""def {route_handler}({params}):\n"""
    route_code += f"""    \"\"\"{method} {path}
    Return:
      - on success: {desc}
      - on error: respond with {', '.join(str(err) for err in sorted(responses) if str(err)[0] != '2')} error codes
    \"\"\"
"""
    route_code += "    data = request.args\n"
    route_code += (
        "    if request.content_type == 'application/json': data.update(request.json)\n"
    )
    route_code += "    status, err = 0, None\n\n"

    # for k, v in request.items():
    #     route_code += f"    {k.strip('?')} = data.get('{k.strip('?')}', None)\n"
    #     if not k.endswith("?"):
    #         route_code += f"    if {k} is None: return jsonify({{'error': _('missing', data=_('{k}'))}}), 400\n"

    route_code += f'    SCHEMA = {route_handler.upper()}_SCHEMA\n'
    route_code += "    error_response = json_validate(data, SCHEMA)\n"
    route_code += "    if error_response is not None: return error_response\n"

    if snippet is not None:
        route_code += '\n' + snippet

    # Generate response stubs for each status code
    route_code += "\n    match [status, err]:\n"
    for status, response_body in responses.items():
        status_code = int(status)  # Default to the status as is (if numeric)

        # Add the response for this status code
        route_code += (
            f"        case [{status_code}, err]:  # Stub for {status_code} response\n"
        )
        route_code += f"            return jsonify({response_body}), {status_code}\n"

    route_code += "        case _:\n"
    route_code += "            return jsonify({'error': _('unexpected')}), 500\n\n"
    return route_code

def generate_routes(base_path):
    """Generate all the routes from the endpoints"""
    for section, paths in endpoints.items():
        routes = ""
        schemas = {}
        for path, methods in paths.items():
            for method, details in methods.items():
                request = details.get("request", {})
                responses = details.get("responses", {})
                desc = details.get("desc", '')
                snippet = details.get('snippet', None)
                pagination = details.get('pagination', None)

                
                if pagination:
                    request.update({"page?": "int", "page_size?": "int", "query?": "str"})
                    responses[OK] = {
                        "next_pages": "int",
                        "count": "int",
                        pagination: [
                            responses[OK]
                        ],
                    }
                    responses.update({
                        UNPROCESSABLE_ENTITY: {
                            "error": _expr("_('invalid', data=_('page'))")
                        },
                        UNPROCESSABLE_ENTITY: {
                            "error": _expr("_('invalid', data=_('page_size'))")
                        },
                    })
                
                route_handler = route_handler_name(path, method)
                routes += generate_route_function(path, route_handler, method, desc, request, responses, snippet)
                schemas[f"{route_handler.upper()}_SCHEMA"] = repr(generate_json_schema(request))
                
                # if len(request) != 0:
                #     schemas += generate_schema_function(path, method, request)
                    
        routes_file_path = os.path.join(base_path, "api", "v1", "routes", section + ".py")
        create_file(routes_file_path, route_template.format(routes=routes, section=section, schemas=',\n    '.join(schemas.keys())))
                    
        schemas_file_path = os.path.join(base_path, "api", "v1", "schemas", section + ".py")
        create_file(schemas_file_path, schema_template.format(section=section, schemas='\n'.join(f'{k} = {v}' for k, v in schemas.items())))


def mirror_existing_files(project_name):
    pjoin = os.path.join
    pwd = os.getcwd()

    # Ensure the destination directory exists
    project_dir = pjoin(pwd, project_name)
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)

    # Iterate over files and directories in the current working directory
    for fd in os.listdir(pwd):
        # Skip the project_name directory and the script itself
        if fd not in [project_name, sys.argv[0], f'{project_name}.erdplus']:
            src_path = pjoin(pwd, fd)
            dest_path = pjoin(project_dir, fd)

            # Check if it's a file or a directory and copy accordingly
            if os.path.isfile(src_path):
                su.copyfile(src_path, dest_path)
            elif os.path.isdir(src_path):
                su.copytree(src_path, dest_path, dirs_exist_ok=True)


def create_model_file(project_name, class_name, class_code, output_dir="models"):
    model_dir = os.path.join(os.getcwd(), project_name, output_dir)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)
    file_path = os.path.join(model_dir, f"{class_name.lower()}.py")
    with open(file_path, "w") as f:
        f.write(class_code)


def sa_type(dataType, dataTypeSize):
    match [dataType, dataTypeSize]:
        case ["int", (''|None)]:
            return "Integer"
        case ["float", (''|None)]:
            return "Float"
        case [("charn" | "varcharn"), size]:
            return f"String({size})"
        case ["date", (''|None)]:
            return "Date"
        case ["custom", sqlType]:
            return sqlType
        case _:
            return None


def type_case(s: str):
    return "".join(map(lambda s: s.capitalize(), s.split("_")))


def generate_class_code(table_id, attributes, relationships, tables_by_id):
    table = tables_by_id[table_id]
    table_name = table["name"]
    attr_types = set()
    columns = []
    foreign_keys = []
    for attr in attributes:
        attr_name = attr["names"][0]
        if attr_name == 'id':
            continue
        attr_type = sa_type(attr["dataType"], attr["dataTypeSize"])
        ###############
        if attr_type is None:
            print(attr)
            assert False
        bracket_at = attr_type.find("(")
        attr_types.add(attr_type[:bracket_at] if bracket_at != -1 else attr_type)
        if attr["fk"]:
            foreign_keys.append(f"    {attr_name} = Column({attr_type}, ForeignKey('{tables_by_id[attr["references"][0]["tableId"]]["name"]}.id'), nullable={attr["optional"]})")
        else:
            columns.append(
                f"""    {attr_name} = Column({attr_type}{
                ', primary_key=True' if attr['pkMember'] else ''}{
                f', nullable={attr["optional"]}'}{
                ', unique=True' if attr['soloUnique'] else ''})"""
            )

    columns.append('')
    columns.extend(foreign_keys)

    if relationships[table_id]:
        columns.append('')
    for rel in relationships[table_id]:
        if table_id == rel["from"]['tableId']:
            from_table = tables_by_id[rel["from"]['tableId']]["name"]
            to_table = tables_by_id[rel["to"]['tableId']]["name"]
            match rel["type"]:
                case "mo":
                    if to_table.find('-') == -1:
                        columns.append(
                            f"    {to_table}s = relationship('{type_case(to_table)}', backref='{from_table}', cascade='all, delete-orphan')"
                        )
                case "mm":
                    (from_table, to_table) = (to_table.split('-'))
                    columns.append(
                        f"""    {to_table}s = relationship('{type_case(to_table)}', viewonly=False,
                              secondary=Table('{from_table}_{to_table}', Base.metadata,
                                Column('{from_table}_id', String(60), ForeignKey('{from_table}.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True),
                                Column('{to_table}_id', String(60), ForeignKey('{to_table}.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)))"""
                    )

    model_code = f"""
from sqlalchemy import Table, Column, ForeignKey, {', '.join(attr_types)}
from sqlalchemy.orm import relationship
from models.base import BaseModel, Base

class {type_case(table_name)}(BaseModel, Base):
    \"\"\"{type_case(table_name)} DB model class
    \"\"\"
    __tablename__ = '{table_name}'

    def __init__(self, ):
        \"\"\"initialize a {type_case(table_name)} instance
        \"\"\"
        super.__init__(*args, **kwargs)

"""
    model_code += "\n".join(columns)
    return model_code


def generate_models(project_name, data):
    tables_by_id = {}
    relationships = {}
    for shape in data["shapes"]:
        if shape["type"] == "Table":
            table = shape["details"]
            tables_by_id[table["id"]] = table
            relationships[table["id"]] = []
            attributes = table["attributes"]

            for attr in attributes:
                if table["name"].count("-") == 2:
                    table["name"] = "-".join(table["name"].split("-")[:-1])
                    rel_type = "mm"
                else:
                    rel_type = "mo"
                if attr["fk"]:
                    table_id = attr["references"][0]["tableId"]
                    if relationships.get(table_id, False):
                        relationships[table_id].append({
                            "type": rel_type,
                            "from": attr["references"][0],
                            "to": {"tableId": table["id"], "attributeId": attr["id"]},
                        })
                    else:
                        relationships[table_id] = [{
                            "type": rel_type,
                            "from": attr["references"][0],
                            "to": {"tableId": table["id"], "attributeId": attr["id"]},
                        }]
                        

    for shape in data["shapes"]:
        if shape["type"] == "Table":
            table_id = shape["details"]["id"]
            table_name = shape["details"]["name"]
            attributes = shape["details"]["attributes"]
            if table_name.find('-') == -1:
                class_code = generate_class_code(
                    table_id, attributes, relationships, tables_by_id
                )
                create_model_file(project_name, table_name, class_code)


# Main function to generate the project
def generate_flask_project(project_name):
    # Create project directories and files
    base_path = os.path.join(os.getcwd(), project_name)

    create_directories(base_path, project_structure)

    # create_test_directories(os.path.join(base_path, "tests"), "", project_structure)

    # Generate dynamic code for routes
    generate_routes(base_path)

    json_data = json.load(open(project_name + ".erdplus", '+br'))

    generate_models(project_name, json_data)

    mirror_existing_files(project_name)
    
    # su.copytree(base_path, os.path.dirname(os.getcwd()), dirs_exist_ok=True)
    

# Run the generator
generate_flask_project("QuizQuickie")

# for end in endpoints:
#     for e in endpoints[end]:
#         print(e+':')
#         for method in endpoints[end][e]:
#             print('   ', method+':')
#     print()








def generate_pydantic_class(class_name: str, fields: dict) -> str:
    """Generates a Pydantic class string from the fields."""
    
    class_definition = f"class {class_name}(BaseModel):\n"
    
    if fields:
        for field_name, (field_type, field_default) in fields.items():
            class_definition += f"    {field_name}: {field_type} = {field_default}\n"
    else:
        class_definition += "    pass\n"
    
    return class_definition


def generate_schema_function(path: str, method, request):
    TYPE_MAPPING = {
        "str": str,
        "int": int,
        "float": float,
        "datetime": str,  # Use `datetime` for more complex implementations
        "bool": bool,
    }
    method_er = {GET: "getter", POST: "poster", PUT: "putter", DELETE: "deleter"}

    import re
    class_name = path[8:] if path.startswith("/api/v1") else path
    class_name = re.sub(r"/<[^>]+>", "", class_name).replace('/', '_')
    class_name += f"_{method_er[method]}_schema"

    schema_fields = {}
    
    for param, param_type in request.items():
        field_name = param.replace('?', '')
    
        if isinstance(param_type, list) and param_type:
            if param_type[0] in TYPE_MAPPING:
                param_type = TYPE_MAPPING[f'list[{param_type[0]}]']
            else:
                param_type = List[str]  # Default to List[str]
        elif isinstance(param_type, dict):
            param_type = TYPE_MAPPING["dict"]
        else:
            param_type = TYPE_MAPPING.get(param_type, str)  # Default to str if not found
            
        if '?' in param:
            schema_fields[field_name] = (f'Optional[{param_type}]', 'Field(None)')  # Mark as Optional
        else:
            schema_fields[field_name] = (param_type, 'Field(...)')  # Required field
    return generate_pydantic_class(type_case(class_name), schema_fields)
