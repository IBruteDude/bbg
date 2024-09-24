from typing import List
from api.v1.auth.basic_auth import BasicAuth
from api.v1.auth.session_auth import SessionAuth
from os import getenv


def require_auth(self, path: str, excluded_paths: List[str]) -> bool:
    """Check if a path requires authentication"""
    if path is None or excluded_paths is None:
        return True
    if path in excluded_paths or path + "/" in excluded_paths:
        return False
    for expath in excluded_paths:
        if expath.endswith("*") and path.find(expath.strip("*")) != 0:
            return False
    return True


match getenv("AUTH", None):
    case "BASIC_AUTH":
        auth = BasicAuth()
    case "SESSION_AUTH":
        auth = SessionAuth()
    case None:
        auth = None
