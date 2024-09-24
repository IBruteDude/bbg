#!/usr/bin/env python
from itertools import chain
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
    "auth": {
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
                    OK: {},
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
                    NOT_FOUND: {"error": _expr("_('not_found', data=_('user'))")},
                },
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
                    },
                },
            }
        },
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
from flasgger import swag_from

from api.v1.routes import app_routes
from api.v1.schemas import json_validate
from api.v1.schemas.{section} import (
    {schemas}
)

{routes}
"""

schema_template = """\"\"\"JSON request validation schemas for the {section} endpoints
\"\"\"
from collections import OrderedDict

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
    from collections import OrderedDict

    if isinstance(value, dict):
        body = OrderedDict(
            {
                "type": "object",
                "properties": OrderedDict({}),
                "required": [],
            }
        )
        if not allow_additional:
            body["additionalProperties"] = False
        for k, v in value.items():
            if k.endswith("?"):
                body["properties"][k[:-1]] = generate_json_schema(v)
            else:
                body["properties"][k] = generate_json_schema(v)
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
    elif value == "str" or type(value) is _expr:
        # if type(value) is _expr:
        #     print(value)
        return {"type": "string"}
    else:
        PATTERNS = {
            "datetime": r"",
            "url": r"^(https?|ftp|file)://([-a-zA-Z0-9@:%._+~#=]{2,256})(:[0-9]+)?(/[-a-zA-Z0-9@:%._+~#=]*)*$",
        }
        return {"type": "string", "pattern": PATTERNS[value]}


def route_handler_name(path, method):
    method_er = {GET: "getter", POST: "poster", PUT: "putter", DELETE: "deleter"}

    route_handler = path[8:] if path.startswith("/api/v1") else path
    route_handler = re.sub(r"/<[^>]+>", "_one", route_handler).replace("/", "_")
    route_handler += f"_{method_er[method]}"

    return route_handler


def generate_route_function(
    path: str, section, route_handler, method, desc, request, responses, snippet=None
):
    """Generate route functions based on path, method, and response codes, with response stubs for each"""
    route_code = f"""@app_routes.route("{path}", methods=["{method}"], strict_slashes=False)
@swag_from('documentation/{section}.yml')\n"""

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

    route_code += f"    SCHEMA = {route_handler.upper()}_SCHEMA\n"
    route_code += "    error_response = json_validate(data, SCHEMA)\n"
    route_code += "    if error_response is not None: return error_response\n"

    if snippet is not None:
        route_code += "\n" + snippet

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


def generate_routes(project_name, endpoints):
    """Generate all the routes from the endpoints"""
    base_path = os.path.join(os.getcwd(), project_name)
    for section, paths in endpoints.items():
        routes = ""
        schemas = {}
        for path, methods in paths.items():
            for method, details in methods.items():
                request = details.get("request", {})
                responses = details.get("responses", {})
                desc = details.get("desc", "")
                snippet = details.get("snippet", None)
                pagination = details.get("pagination", None)

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
                                "error": _expr("_('invalid', data=_('page'))")
                            },
                            UNPROCESSABLE_ENTITY: {
                                "error": _expr("_('invalid', data=_('page_size'))")
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
                    snippet,
                )
                schemas[f"{route_handler.upper()}_SCHEMA"] = repr(
                    generate_json_schema(request)
                )

                # if len(request) != 0:
                #     schemas += generate_schema_function(path, method, request)

        routes_file_path = os.path.join(
            base_path, "api", "v1", "routes", section + ".py"
        )
        create_file(
            routes_file_path,
            route_template.format(
                routes=routes, section=section, schemas=",\n    ".join(schemas.keys())
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
        if fd not in [
            project_name,
            sys.argv[0],
            f"{project_name}.erdplus",
            ".git",
            "rapidapi.key",
        ]:
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
        case ["int", ("" | None)]:
            return "Integer"
        case ["float", ("" | None)]:
            return "Float"
        case [("charn" | "varcharn"), size]:
            return f"String({size})"
        case ["date", ("" | None)]:
            return "Date"
        case ["custom", sqlType]:
            return sqlType
        case _:
            return None


def type_case(s: str):
    return "".join(w.capitalize() for w in s.split("_"))


def generate_class_code(table_id, attributes, relationships, tables_by_id, assoc=False):
    table = tables_by_id[table_id]
    table_name = table["name"]
    if assoc:
        attr_types = (
            sa_type(attr["dataType"], attr["dataTypeSize"]) for attr in attributes
        )
        attr_types = sorted(
            set(t[: t.find("(")] if "(" in t else t for t in attr_types)
        )

        table_name = table_name.replace("-", "_")
        other_name = lambda attr: tables_by_id[attr["references"][0]["tableId"]]["name"]
        return f"""
from sqlalchemy import Table, Column, ForeignKey, {', '.join(attr_types)}
from models.base import Base

{table_name} = Table('{table_name}', Base.metadata,
    {
',\n    '.join(f'''Column('{attr["names"][0]}', {
        sa_type(attr["dataType"], attr["dataTypeSize"])
    }, ForeignKey('{other_name(attr)}.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)''' for attr in attributes if attr["fk"])
}
)"""
    attr_types = set()
    columns = []
    foreign_keys = []
    assoc_tables = []
    deffered_rels = set()
    for attr in attributes:
        attr_name = attr["names"][0]
        if attr_name == "id":
            continue
        attr_type = sa_type(attr["dataType"], attr["dataTypeSize"])
        bracket_at = attr_type.find("(")
        attr_types.add(attr_type[:bracket_at] if bracket_at != -1 else attr_type)
        if attr["fk"]:
            foreign_keys.append(
                f"    {attr_name} = Column({attr_type}, ForeignKey('{tables_by_id[attr["references"][0]["tableId"]]["name"]}.id'), nullable={attr["optional"]})"
            )
        else:
            columns.append(
                f"""    {attr_name} = Column({attr_type}{
                ', primary_key=True' if attr['pkMember'] else ''}{
                f', nullable={attr["optional"]}'}{
                ', unique=True' if attr['soloUnique'] else ''})"""
            )

    columns.append("")
    columns.extend(foreign_keys)

    if relationships[table_id]:
        columns.append("")
    for rel in relationships[table_id]:
        from_table = tables_by_id[rel["from"]["tableId"]]["name"]
        to_table = tables_by_id[rel["to"]["tableId"]]["name"]
        match rel["type"]:
            case "oo":
                columns.append(
                    f"    {to_table} = relationship('{type_case(to_table)}', back_populates='{from_table}s', cascade='all, delete-orphan', unique=True)"
                )
            case "mo":
                columns.append(
                    f"    {to_table}s = relationship('{type_case(to_table)}', back_populates='{from_table}', cascade='all, delete-orphan')"
                )
                if rel["from"]["tableId"] == table_id:
                    to_name = rel["to"]["name"]
                    deffered_rels.add(
                        f"""from models.{to_name} import {type_case(to_name)}
{type_case(to_name)}.{table_name} = relationship('{type_case(table_name)}', back_populates='{to_name}s')"""
                    )
            case "om":
                if rel["to"]["tableId"] == table_id:
                    columns.append(
                        f"    {to_table} = relationship('{type_case(to_table)}', back_populates='{from_table}s')"
                    )
                else:
                    columns.append(f"    {to_table} = None")
            case "mm":
                assoc_tables.append((from_table, to_table))
                is_parent = from_table == table_name
                if rel["from"]["tableId"] == table_id:
                    columns.append(
                        f"""    {to_table if is_parent else from_table}s = relationship('{type_case(to_table if is_parent else from_table)}', viewonly=False, secondary={from_table}_{to_table}, back_populates='{from_table if is_parent else to_table}s')"""
                    )
                else:
                    columns.append(
                        f"""    {to_table if is_parent else from_table}s = None"""
                    )

    for rel in relationships[table_id]:
        if rel["type"] == "mm" and rel["from"]["tableId"] == table_id:
            to_name = rel["to"]["name"]

            deffered_rels.add(
                f"""from models.{to_name} import {type_case(to_name)}
{type_case(to_name)}.{table_name}s = relationship('{type_case(table_name)}', viewonly=False, secondary={table_name}_{to_name}, back_populates='{to_name}s')"""
            )
    required_attrs = [
        attr["names"][0]
        for attr in attributes
        if attr["names"][0] != "id" and not attr["optional"]
    ]
    optional_attrs = [attr["names"][0] for attr in attributes if attr["optional"]]

    ctor_args = f"{''.join(attr+', ' for attr in required_attrs)}{''.join(attr+'=None, ' for attr in optional_attrs)}"

    model_code = f"""from sqlalchemy import Column, ForeignKey, {', '.join(sorted(attr_types))}
from sqlalchemy.orm import relationship
from models.base import BaseModel, Base
{'\n'.join(f'from models.{ft}_{tt} import {ft}_{tt}' for ft, tt in assoc_tables)}

class {type_case(table_name)}(Base, BaseModel):
    \"\"\"{type_case(table_name)} DB model class
    \"\"\"
    __tablename__ = '{table_name}'

    def __init__(self, {ctor_args}**kwargs):
        \"\"\"initialize a {type_case(table_name)} instance
        \"\"\"
        kwargs.update({', '.join(f'{attr}={attr}' for attr in chain(required_attrs, optional_attrs))})
        super().__init__(**kwargs) 

{'\n'.join(columns)}
{'\n\n'.join(sorted(deffered_rels))}
"""
    return model_code


def generate_models(project_name, data):
    tables_by_id = {}
    relationships = {}
    for shape in data["shapes"]:
        if shape["type"] == "Table":
            table = shape["details"]
            tables_by_id[table["id"]] = table
            relationships[table["id"]] = []

    for shape in data["shapes"]:
        if shape["type"] == "Table":
            table = shape["details"]
            attributes = table["attributes"]

            if table["name"].count("-") == 2:
                parts = table["name"].split("-")
                table["name"] = "-".join(parts[:-1])
                attributes = [attr for attr in attributes if attr["fk"]]
                attr1, attr2 = attributes[0], attributes[1]
                assert attr1["fk"] and attr2["fk"]
                table_id1 = attr1["references"][0]["tableId"]
                table_id2 = attr2["references"][0]["tableId"]

                if parts[0] != tables_by_id[table_id1]["name"]:
                    table_id1, table_id2 = table_id2, table_id1

                rel = {
                    "type": parts[-1],
                    "from": {
                        "tableId": table_id1,
                        "name": tables_by_id[table_id1]["name"],
                        "attributeId": attr["id"],
                    },
                    "to": {
                        "tableId": table_id2,
                        "name": tables_by_id[table_id2]["name"],
                        "attributeId": attr["id"],
                    },
                }
                relationships[rel["from"]["tableId"]].append(rel)
                relationships[rel["to"]["tableId"]].append(rel)
                continue

            for attr in attributes:
                if table["name"].count("-") == 2:
                    secs = table["name"].split("-")
                    table["name"] = "-".join(secs[:-1])
                    rel_type = secs[:-1]
                else:
                    rel_type = "mo"
                if attr["fk"]:
                    table_id = attr["references"][0]["tableId"]
                    rel = {
                        "type": rel_type,
                        "from": attr["references"][0],
                        "to": {"tableId": table["id"], "attributeId": attr["id"]},
                    }
                    if rel_type == "mm":
                        if relationships.get(rel["to"]["tableId"], False):
                            relationships[rel["to"]["tableId"]] = []
                        relationships[rel["to"]["tableId"]].append(rel)
                    elif rel_type == "mo":
                        attr["references"][0]["name"] = tables_by_id[
                            attr["references"][0]["tableId"]
                        ]["name"]
                        relationships[table_id].append(
                            {
                                "type": "mo",
                                "from": attr["references"][0],
                                "to": {
                                    "tableId": table["id"],
                                    "name": tables_by_id[table["id"]]["name"],
                                    "attributeId": attr["id"],
                                },
                            }
                        )
                        relationships[table["id"]].append(
                            {
                                "type": "om",
                                "from": {
                                    "tableId": table["id"],
                                    "name": tables_by_id[table["id"]]["name"],
                                    "attributeId": attr["id"],
                                },
                                "to": attr["references"][0],
                            }
                        )

    for shape in data["shapes"]:
        if shape["type"] == "Table":
            table_id = shape["details"]["id"]
            table_name = shape["details"]["name"]
            attributes = shape["details"]["attributes"]
            class_code = generate_class_code(
                table_id, attributes, relationships, tables_by_id, "-" in table_name
            )
            create_model_file(project_name, table_name.replace("-", "_"), class_code)

    create_models_init_file(
        project_name,
        [
            shape["details"]["name"]
            for shape in data["shapes"]
            if shape["type"] == "Table"
        ],
    )


def create_models_init_file(project_name, table_names):
    classes = [name for name in table_names if "-" not in name]
    model_init_file = f"""from models.engine.relational_storage import RelationalStorage
{'\n'.join(f'from models.{name.replace('-', '_')} import {type_case(name) if '-' not in name else name.replace('-', '_')}' for name in table_names)}
from bcrypt import hashpw, gensalt

classes = {{{', '.join(f'"{cls}": {type_case(cls)}' for cls in classes)}}}

storage = RelationalStorage()
storage.reload()

storage.new(User(email='admin@quizquickie.com', password=hashpw('admin'.encode(), gensalt()), user_name='admin'))
"""

    create_file(
        os.path.join(os.getcwd(), project_name, "models", "__init__.py"),
        model_init_file,
    )


def create_routes_init_file(project_name, section_names):
    routes_init_file = f"""\"\"\" API Routes
\"\"\"
from flask import Blueprint

app_routes = Blueprint("app_views", __name__, url_prefix="/api/v1")

{'\n'.join(f'from api.v1.routes.{section} import *' for section in section_names)}
    """
    create_file(
        os.path.join(os.getcwd(), project_name, "api", "v1", "routes", "__init__.py"),
        routes_init_file,
    )


def generate_yaml_files(base_path, endpoints):
    import yaml
    from collections import OrderedDict

    base_dir = os.path.join(base_path, "api", "v1", "routes", "documentation")
    for resource, paths in endpoints.items():
        yaml_content = OrderedDict(
            {
                "swagger": "2.0",
                "info": {
                    "title": f'{resource.replace("_", " ").title()} API',
                    "description": f'API documentation for {resource.replace("_", " ").title()}',
                    "version": "1.0.0",
                },
                "host": "localhost:5000",
                "basePath": "/api/v1",
                "schemes": ["http", "https"],
                "paths": {},
            }
        )

        for path, methods in paths.items():
            for method, details in methods.items():
                method_info = OrderedDict(
                    {
                        "summary": details["desc"],
                        "parameters": [],
                        "responses": {},
                    }
                )

                # Convert request schema using your JSON Schema converter
                if "request" in details:
                    request_schema = generate_json_schema(details["request"])
                    method_info["parameters"].append(
                        OrderedDict(
                            {
                                "name": "body",
                                "in": "body",
                                "required": True,
                                "schema": request_schema,
                            }
                        )
                    )

                # Convert response schemas
                for response_code, response_details in details["responses"].items():
                    # print(response_code, end=' : ')
                    response_schema = generate_json_schema(response_details)
                    method_info["responses"][response_code] = OrderedDict(
                        {
                            "description": response_code,
                            "schema": response_schema,
                        }
                    )

                # Add method info to paths
                yaml_content["paths"].setdefault(path, {})[method.lower()] = method_info

        # Save the YAML content to a file
        yaml_filename = os.path.join(base_dir, f"{resource}.yml")
        with open(yaml_filename, "w") as yaml_file:
            yaml.dump(yaml_content, yaml_file, default_flow_style=False)


def generate_translations(project_name):
    import requests as rs

    os.chdir(os.path.join(os.getcwd(), project_name, "api", "v1"))
    os.system(f"pybabel extract -F babel.cfg -k _l -o messages.pot .")

    lines = []

    from config import Config

    for lang in Config.LANGUAGES:
        lang_po = os.path.join("translations", lang, "LC_MESSAGES", "messages.po")

        os.system(f"pybabel init -i messages.pot -d translations -l {lang}")
        from pprint import pp

        with open(lang_po) as f:
            lines = f.readlines()
            msgs = [
                (i, line[7:-2])
                for i, line in enumerate(lines)
                if line.startswith('msgid "')
            ]
            ids, texts = zip(*msgs)
        rapidapi_key = open("rapidapi.key").readline().strip()
        response = rs.post(
            "https://ai-translate.p.rapidapi.com/translate",
            headers={
                "Content-Type": "application/json",
                "x-rapidapi-host": "ai-translate.p.rapidapi.com",
                "x-rapidapi-key": rapidapi_key,
            },
            json={"sl": "en", "tl": lang, "texts": texts},
        )
        response = response.json()
        assert response["code"] == 200
        tls = response["texts"]
        for i, msgstr in enumerate(tls):
            lines[ids[i] + 1] = f'msgstr "{msgstr}"\n'

        with open(lang_po, "w", encoding="utf-8") as f:
            f.writelines(lines)

    os.system(f"pybabel compile -d translations")
    os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.getcwd()))))


# Main function to generate the project
def generate_flask_project(project_name):
    # Create project directories and files
    base_path = os.path.join(os.getcwd(), project_name)

    create_directories(base_path, project_structure)

    # create_test_directories(os.path.join(base_path, "tests"), "", project_structure)

    # Generate dynamic code for routes
    generate_routes(base_path, endpoints)

    relational_models = json.load(open(project_name + ".erdplus", "+br"))

    generate_models(project_name, relational_models)

    generate_yaml_files(base_path, endpoints)

    mirror_existing_files(project_name)

    generate_translations(project_name)

    os.system(f"black -q {project_name}")

    # su.copytree(base_path, os.path.dirname(os.getcwd()), dirs_exist_ok=True)


# Run the generator
generate_flask_project("QuizQuickie")
