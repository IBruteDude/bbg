#!/usr/bin/env python
from itertools import chain
import sys
import os
import re
import shutil as su
import json
from typing import List, Optional

from werkzeug.routing import Rule, Map

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
status_code = {
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",
    103: "Checkpoint",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi-Status",
    208: "Already Reported",
    226: "IM Used",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    302: "Moved Temporarily",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Payload Too Large",
    413: "Request Entity Too Large",
    414: "URI Too Long",
    414: "Request-URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested range not satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",
    419: "Insufficient Space On Resource",
    420: "Method Failure",
    421: "Destination Locked",
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    425: "Too Early",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal Reasons",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version not supported",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    508: "Loop Detected",
    509: "Bandwidth Limit Exceeded",
    510: "Not Extended",
    511: "Network Authentication Required",
}


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
                "responses": {OK: [{"status": "str"}]},
                "snippet": '''
''',
            }
        },
        "/api/v1/stats": {
            GET: {
                "desc": "report statistics about api uptime and workload",
                "request": {},
                "responses": {
                    OK: [{"online_users": "int"}],
                    UNAUTHORIZED: [{"error": _expr("_('unauthorized')")}],
                },
                "snippet": '''
''',
            }
        },
    },
    "auth": {
        "/api/v1/auth/signup": {
            POST: {
                "desc": "create a new user account",
                "tags": ['User', 'UserSession'],
                "request": {
                    "email": "email",
                    "password": "str",
                    "first_name": "str",
                    "last_name": "str",
                    "user_name": "str",
                    "profile_picture?": "url",
                },
                "responses": {
                    # account created successfully
                    CREATED: [{"user_id": "int"}],
                    CONFLICT: [{"error": _expr("_('duplicate', data=_('email'))")},
                    {"error": _expr("_('duplicate', data=_('user_name'))")}],
                    BAD_REQUEST: [{
                        "error": _expr("_('incomplete', data=_('login details'))")
                    }],
                    UNPROCESSABLE_ENTITY: [{
                        "error": _expr("_('invalid', data=_('login details'))")
                    }],
                },
                "snippet": '''
    from bcrypt import gensalt, hashpw
    try:
        req["password"] = hashpw(req["password"].encode(), gensalt())
        from sqlalchemy import or_
        if storage.query(User).where(or_(User.email==req["email"], User.user_name==req["user_name"])).count() > 0:
            return jsonify({'error': _('duplicate', data=_('email or user name'))}), 409
        storage.new(User(**req))
        storage.save()
        return jsonify({}), 201
    except Exception as e:
        print(e)
        abort(500)
''',
            }
        },
        "/api/v1/auth/login": {
            POST: {
                "desc": "create a new session for the user and log in",
                "tags": ["User", "UserSession"],
                "request": {"email": "email", "password": "str"},
                "responses": {
                    OK: [{}],
                    UNAUTHORIZED: [{
                        "error": _expr("_('invalid', data=_('login details'))")
                    }],
                },
                "snippet": '''

    from bcrypt import checkpw
    from api.v1.auth import auth, SessionAuth
    from os import getenv
    try:
        user: User = storage.query(User).where(User.email==req["email"]).one_or_none()
        pass_bytes = req["password"].encode()
        if user is None or not checkpw(pass_bytes, user.password):
            return jsonify({'error': _('invalid', data=_('login details'))}), 401
        resp = jsonify({})
        if isinstance(auth, SessionAuth):
            session_id = auth.create_session(user.id)
            resp.set_cookie(getenv("SESSION_NAME"), session_id)
        return resp, 200
    except Exception as e:
        print(req)
        print(f'{e.__class__.__name__}: {e}')
        abort(500)
''',
            }
        },
        "/api/v1/auth/password/reset": {
            GET: {
                "desc": "send a password reset email",
                "tags": ['User', 'UserSession'],
                "request": {},
                "responses": {
                    OK: [{"reset_token": "str"}],
                    UNAUTHORIZED: [{"error": _expr("_('unauthorized')")}],
                },
                "snippet": '''
''',
            }
        },
        "/api/v1/auth/password/reset/confirm": {
            POST: {
                "desc": "confirm password reset",
                "tags": ['User', 'UserSession'],
                "request": {"reset_token": "str", "new_password": "str"},
                "responses": {
                    OK: [{}],
                    BAD_REQUEST: [{
                        "error": _expr("_('invalid', data=_('token or password'))")
                    }],
                },
                "snippet": '''
''',
            }
        },
        "/api/v1/auth/logout": {
            DELETE: {
                "desc": "remove user session and log out",
                "tags": ['User', 'UserSession'],
                "request": {},
                "responses": {
                    NO_CONTENT: [{}],
                    UNAUTHORIZED: [{"error": _expr("_('unauthorized')")}],
                },
                "snippet": '''
''',
            }
        },
        "/api/v1/auth/deactivate": {
            DELETE: {
                "desc": "delete user account",
                "tags": ['User', 'UserSession'],
                "request": {},
                "responses": {
                    NO_CONTENT: [{}],
                    UNAUTHORIZED: [{"error": _expr("_('unauthorized')")}],
                },
                "snippet": '''
''',
            }
        },
    },
    "user_profile": {
        "/api/v1/user/profile": {
            GET: {
                "desc": "respond with user profile details",
                "tags": ['User'],
                "request": {},
                "responses": {
                    OK: [{
                        "user": {
                            "email": "email",
                            "first_name": "str",
                            "last_name": "str",
                            "user_name": "str",
                            "profile_picture": "url",
                        }
                    }],
                    UNAUTHORIZED: [{"error": _expr("_('unauthorized')")}],
                },
                "snippet": '''
    user: User = getattr(g, "user", None)
    if user is None:
        return jsonify({"error": _("unauthorized")}), 401

    try:
        return jsonify({"user": {"email": user.email, "first_name": user.first_name, "last_name": user.last_name, "user_name": user.user_name, "profile_picture": user.profile_picture}}), 200
    except Exception as e:
        print(f"[{e.__class__.__name__}]: {e}")
        abort(500)
''',
            },
            PUT: {
                "desc": "change user profile details",
                "tags": ['User'],
                "request": {
                    "first_name?": "str",
                    "last_name?": "str",
                    "user_name?": "str",
                    "profile_picture?": "url",
                },
                "responses": {
                    OK: [{}],
                    BAD_REQUEST: [{"error": _expr("_('invalid', data=_('profile'))")}],
                    CONFLICT: [{"error": _expr("_('duplicate', data=_('user_name'))")}],
                    UNAUTHORIZED: [{"error": _expr("_('unauthorized')")}],
                },
                "snippet": '''
    user: User = getattr(g, "user", None)
    if user is None:
        return jsonify({"error": _("unauthorized")}), 401
    first_name = req["first_name"] if req.get("first_name", None) else None
    last_name = req["last_name"] if req.get("last_name", None) else None
    user_name = req["user_name"] if req.get("user_name", None) else None
    profile_picture = (
        req["profile_picture"] if req.get("profile_picture", None) else None
    )

    try:
        if user_name:
            if storage.query(User).where(User.user_name==user_name).count() > 0:
                return jsonify({"error": _("duplicate", data=_("user_name"))}), 409
            user.user_name = user_name
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if profile_picture:
            user.profile_picture = profile_picture
        user.save()
        return jsonify({}), 200
    except Exception as e:
        print(f"[{e.__class__.__name__}]: {e}")
        abort(500)
''',
            },
        },
        #################################
        "/api/v1/user/profile/quiz/<int:quiz_id>/attempts": {
            GET: {
                "desc": "respond with all user's quiz attempts",
                "pagination": "attempts",
                "tags": ['User', 'Quiz'],
                "request": {},
                "responses": {
                    OK: [{"attempt_id": "int", "time": "datetime", "score": "int"}],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('quiz'))")}],
                    GONE: [{"error": _expr("_('deleted', data=_('quiz'))")}],
                    FORBIDDEN: [{"error": _expr("_('quiz time has ended')")}],
                    UNAUTHORIZED: [{"error": _expr("_('unauthorized')")}],
                },
                "snippet": '''
    user: User = getattr(g, "user", None)
    if user is None:
        return jsonify({"error": _("unauthorized")}), 401
    page = int(req["page"]) if req.get("page", None) else None
    page_size = int(req["page_size"]) if req.get("page_size", None) else None
    quiz_query = req["query"] if req.get("query", None) else None

    from sqlalchemy import and_

    try:
        if storage.query(Quiz).join(QuizAttempt, QuizAttempt.quiz_id==Quiz.id).where(and_(QuizAttempt.user_id==user.id, Quiz.id==quiz_id)).one_or_none() is None:
            return jsonify({"error": _("not_found", data=_("quiz"))}), 404

        if storage.query(Quiz).get(quiz_id).end < datetime.now():
            return jsonify({"error": _("quiz time has ended")}), 403

        query = storage.query(QuizAttempt).filter_by(quiz_id=quiz_id, user_id=user.id)

        if quiz_query:
            query = query.join(Quiz, QuizAttempt.quiz_id==Quiz.id).where(Quiz.title.like(f"%{quiz_query}%"))

        try:
            return (
                paginate(
                    "attempts", query, page, page_size, lambda a: {"attempt_id": a.id, "time": datetime.strftime(a.created_at, time_fmt), "score": a.score}
                ),
                200,
            )
        except ValueError as e:
            data = (
                e.args[0]
                if e.args and e.args[0] in ("page", "page_size")
                else "request"
            )
            return jsonify({"error": _("invalid", data=_(data))}), 422
    except Exception as e:
        print(f"[{e.__class__.__name__}]: {e}")
        abort(500)
''',
            },
            POST: {
                "desc": "submit user answers for the quiz's questions",
                "tags": ['User', 'Quiz'],
                "request": {"answers": [{"options": ["int"]}]},
                "responses": {
                    OK: [{
                        "attempt_id": "int",
                        "time": "datetime",
                        "total_score": "int",
                        "correct_answers": [{"answer": ["int"]}]
                    }],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('quiz'))")}],
                    UNAUTHORIZED: [{"error": _expr("_('unauthorized')")}],
                },
                "snippet": '''
    user: User = getattr(g, "user", None)
    if user is None:
        return jsonify({"error": _("unauthorized")}), 401
    answers = req["answers"]

    try:
        quiz = storage.query(Quiz).get(quiz_id)

        if quiz is None:
            return jsonify({"error": _("not_found", data=_("quiz"))}), 404


        if len(answers) != len(quiz.questions):
            return jsonify({"error": _("invalid", data=_("answer option"))}), 404

        attempt = storage.new(QuizAttempt(score=0, quiz_id=quiz_id, user_id=user.id))


        total_score = 0
        full_score = True
        correct_answers = []
        for ans, q in zip(answers, quiz.questions):
            for a in ans['options']:
                storage.new(UserAnswer(attempt_id=attempt.id, answer=a, question_id=q.id)).save()
            correct_answer = set(a.order for a in q.answers if a.correct)
            if correct_answer == set(ans['options']):
                total_score += q.points
            else:
                full_score = False
            correct_answers.append({'options': list(correct_answer)})

        attempt.score = total_score
        attempt.full_score = full_score
        attempt.save()

        return (
            jsonify({"score": total_score, "correct_answers": correct_answers}),
            200,
        )
    except Exception as e:
        print(f"[{e.__class__.__name__}]: {e}")
        abort(500)
''',
            },
        },
        "/api/v1/user/profile/group": {
            GET: {
                "desc": "respond with all the user's subscribed groups",
                "tags": ['User', 'Group'],
                "pagination": "groups",
                "request": {},
                "responses": {
                    OK: [{"group_id": "int", "group_title": "str"}],
                    UNAUTHORIZED: [{"error": _expr("_('unauthorized')")}],
                },
                "snippet": '''
    user: User = getattr(g, "user", None)
    if user is None:
        return jsonify({"error": _("unauthorized")}), 401
    page = int(req["page"]) if req.get("page", None) else None
    page_size = int(req["page_size"]) if req.get("page_size", None) else None
    query = req["query"] if req.get("query", None) else None

    try:
        try:
            return paginate("groups", query, page, page_size, None, apply=lambda g: {"group_id": g.id, "group_title": g.title}), 200
        except ValueError as e:
            data = (e.args[0]if e.args and e.args[0] in ("page", "page_size") else "request")
            return jsonify({"error": _("invalid", data=_(data))}), 422
    except Exception as e:
        print(f"[{e.__class__.__name__}]: {e}")
        abort(500)
''',
            },
            POST: {
                "desc": "subscribe the user to the group",
                "tags": ['User', 'Group'],
                "request": {"group_id": "int"},
                "responses": {
                    OK: [{}],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('group'))")}],
                    CONFLICT: [{"error": _expr("_('already subscribed to group')")}],
                    GONE: [{"error": _expr("_('deleted', data=_('group'))")}],
                    UNAUTHORIZED: [{"error": _expr("_('unauthorized')")}],
                },
                "snippet": '''
    user: User = getattr(g, "user", None)
    if user is None:
        return jsonify({"error": _("unauthorized")}), 401
    group_id = int(req["group_id"])

    try:
        group: Group = storage.query(Group).get(group_id)
        if group is None:
            return jsonify({"error": _("not_found", data=_("group"))}), 404
        if user in group.users:
            return jsonify({"error": _("already subscribed to group")}), 409
        group.users.append(user)
        storage.save()
        return jsonify({}), 200
        # return jsonify({"error": _("deleted", data=_("group"))}), 410
    except Exception as e:
        print(f"[{e.__class__.__name__}]: {e}")
        abort(500)
''',
            },
        },
        "/api/v1/user/profile/group/<int:group_id>": {
            DELETE: {
                "desc": "unsubscribe user from a group",
                "tags": ['User', 'Group'],
                "request": {},
                "responses": {
                    NO_CONTENT: [{}],
                    NOT_FOUND: [
                        {"error": _expr("_('not_found', data=_('group'))")},
                        {"error": _expr("_('user not subscribed to group')")}
                    ],
                    UNAUTHORIZED: [{"error": _expr("_('unauthorized')")}],
                },
                "snippet": '''
''',
            },
        }
    },
    "user_groups": {
        "/api/v1/user/group": {
            GET: {
                "desc": "respond with all the user's own groups",
                "tags": ['User', 'Group', 'Ownership'],
                "pagination": "groups",
                "request": {},
                "responses": {
                    OK: [{"group_id": "int", "title": "str"}],
                    UNAUTHORIZED: [{"error": _expr("_('unauthorized')")}],
                },
                "snippet": '''
    user = getattr(g, "user", None)
    if user is None:
        return jsonify({"error": _("unauthorized")}), 401
    from sqlalchemy import and_

    try:
        query = storage.query(Group).where(
            and_(Group.ownership_id == Ownership.id, Ownership.user_id == user.id)
        )
        try:
            return (
                paginate(
                    "groups",
                    query,
                    req.get("page", None),
                    req.get("page_size", None),
                    apply=lambda group: {"group_id": group.id, "title": group.title},
                ),
                200,
            )
        except ValueError as e:
            data = (
                e.args[0]
                if e.args and e.args[0] in ("page", "page_size")
                else "request"
            )
            return (
                jsonify(
                    {
                        "error": _(
                            "invalid",
                            data=_(data),
                        )
                    }
                ),
                422,
            )
    except Exception as e:
        print(f"[{e.__class__.__name__}]: {e}")
        abort(500)
''',
            },
            POST: {
                "desc": "create a user group",
                "tags": ['User', 'Group', 'Ownership'],
                "request": {"title": "str"},
                "responses": {
                    CREATED: [{"group_id": "int"}],
                    CONFLICT: [{"error": _expr("_('duplicate', data=_('group'))")}],
                },
                "snippet": '''
    user = getattr(g, "user", None)
    if user is None:
        return jsonify({"error": _("unauthorized")}), 401

    try:

        title = req["title"]

        if storage.query(Group).filter_by(title=title).count() > 0:
            return jsonify({"error": _("duplicate", data=_("group"))}), 409
        storage.new(
            Group(
                title=title,
                ownership_id=storage.new(Ownership(user_id=user.id)).save().id,
            )
        )
        storage.save()
        return jsonify({}), 201
    except Exception as e:
        print(f"[{e.__class__.__name__}]: {e}")
        abort(500)
''',
            },
        },
        "/api/v1/user/group/<int:group_id>": {
            GET: {
                "desc": "respond with user group details",
                "tags": ['User', 'Group', 'Ownership'],
                "request": {},
                "responses": {
                    OK: [{"group": {"title": "str"}}],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('group'))")}],
                },
            },
            PUT: {
                "desc": "update user group details",
                "tags": ['User', 'Group', 'Ownership'],
                "request": {"title": "str"},
                "responses": {
                    OK: [{}],
                    CONFLICT: [{"error": _expr("_('duplicate', data=_('title'))")}],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('group'))")}],
                },
                "snippet": '''
    user = getattr(g, "user", None)
    if user is None:
        return jsonify({"error": _("unauthorized")}), 401
    from sqlalchemy import and_
    try:
        group:Group = storage.query(Group).where(and_(Group.id==group_id, Group.ownership_id==Ownership.id, Ownership.user_id==user.id)).one_or_none()
        if group is None:
            return jsonify({"error": _("not_found", data=_("group"))}), 404
            
        title = req['title']
        if storage.query(Group).where(Group.title==title).count() > 0:
            return jsonify({"error": _("duplicate", data=_("title"))}), 409
            
        group.update(title=title)
        return jsonify({}), 200
    except Exception as e:
        print(f"[{e.__class__.__name__}]: {e}")
        abort(500)
                ''',
            },
            DELETE: {
                "desc": "delete a user group",
                "tags": ['User', 'Group', 'Ownership'],
                "request": {},
                "responses": {
                    NO_CONTENT: [{}],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('group'))")}],
                },
                "snippet": '''
    user = getattr(g, "user", None)
    if user is None:
        return jsonify({"error": _("unauthorized")}), 401

    from sqlalchemy import and_
    try:
        group:Group = storage.query(Group).where(and_(Group.id==group_id, Group.ownership_id==Ownership.id, Ownership.user_id==user.id)).one_or_none()
        if group is None:
            return jsonify({"error": _("not_found", data=_("group"))}), 404
        group.delete()
        return jsonify({}), 204
    except Exception as e:
        print(f"[{e.__class__.__name__}]: {e}")
        abort(500)
''',
            },
        },
        "/api/v1/user/group/<int:group_id>/users": {
            GET: {
                "desc": "get all the group subscribed users",
                "pagination": "users",
                "tags": ['User', 'Group', 'Ownership', 'QuizAttempt'],
                "request": {},
                "responses": {
                    OK: [{
                        "user_id": "int",
                        "user_name": "int",
                        "total_score": "int",
                        "attempted_quizzes": "int",
                        # "attempted_quizzes": [{"quiz_id": "int"}],
                    }],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('group'))")}],
                },
                "snippet": '''
    user: User = getattr(g, 'user', None)
    if user is None:
        return jsonify({'error': _('unauthorized')}), 401
    page = int(req['page']) if req.get('page', None) else None
    page_size = int(req['page_size']) if req.get('page_size', None) else None
    query = req['query'] if req.get('query', None) else None

    from sqlalchemy import and_, func, distinct
    try:
        group = storage.query(Group).where(Group.ownership.user_id==user.id).filter_by(id=group_id).one_or_none()
        if group is None:
            return jsonify({'error': _('not_found', data=_('group'))}), 404

        query = (
            storage.query(
                User,
                func.sum(QuizAttempt.score).label("total_score"),
                func.count(distinct(QuizAttempt.quiz_id)).label("attempt_count")
            )
            .outerjoin(QuizAttempt, Quiz.id == QuizAttempt.quiz_id)
            .join(Quiz, Quiz.id == QuizAttempt.quiz_id)
            .where(Quiz.group_id == group_id)
            .group_by(User.id)
        )

        try:
            return paginate("users", query, page, page_size, lambda u: {'user_id': u[0].id, 'user_name': u[0].user_name, 'total_score': u[1], 'attempted_quizzes': u[2]}), 200
        except ValueError as e:
            data = e.args[0] if e.args and e.args[0] in ("page", "page_size") else "request"
            return jsonify({"error": _("invalid", data=_(data))}), 422
    except Exception as e:
        print(f'[{e.__class__.__name__}]: {e}')
        abort(500)
''',
            },
            POST: {
                "desc": "add users to a group",
                "tags": ['User', 'Group', 'Ownership'],
                "request": {"users": [{"user_id": "int"}]},
                "responses": {
                    OK: [{}],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('group'))")}],
                    CONFLICT: [{"error": _expr("_('duplicate', data=_('user'))")}],
                },
                "snippet": '''
''',
            },
            DELETE: {
                "desc": "remove users from group",
                "tags": ['User', 'Group', 'Ownership'],
                "request": {"users": [{"user_id": "int"}]},
                "responses": {
                    NO_CONTENT: [{}],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('group'))")}],
                    CONFLICT: [{"error": _expr("_('duplicate', data=_('user'))")}],
                },
                "snippet": '''
''',
            },
        },
    },
    "user_quizzes": {
        "/api/v1/user/quiz": {
            GET: {
                "desc": "respond with the user's created quizzes",
                "pagination": "quizzes",
                "tags": ['User', 'Quiz'],
                "request": {
                    "category?": "str",
                    "sort_by?": "str",
                    "difficulty?": "int",
                },
                "responses": {
                    OK: [{
                        "quiz_id": "int",
                        "title": "str",
                        "category": "str",
                        "difficulty": "int",
                        "points": "int",
                        "duration": "int",
                    }],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('category'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _expr("_('invalid', data=_('sort key'))")},
                        {"error": _expr("_('invalid', data=_('difficulty'))")}
                    ],
                },
                "snippet": '''
    user = getattr(g, "user", None)
    if user is None:
        return jsonify({"error": _("unauthorized")}), 401
    sort_by = req.get("sort_by", None)
    try:
        query = storage.query(Quiz).where(Quiz.user_id == user.id)
        if sort_by in (
            "title",
            "category",
            "difficulty",
            "points",
            "duration",
            "start",
            "end",
        ):
            query = query.order_by(getattr(Quiz, sort_by))
        for k in ("category", "difficulty"):
            if req.get(k, None):
                query = query.where(getattr(Quiz, k) == req[k])
        try:
            return (
                paginate(
                    "quizzes", query, req.get("page", None), req.get("page_size", None)
                ),
                200,
            )
        except ValueError as e:
            data = (
                e.args[0]
                if e.args and e.args[0] in ("page", "page_size")
                else "request"
            )
            return (
                jsonify(
                    {
                        "error": _(
                            "invalid",
                            data=_(data),
                        )
                    }
                ),
                422,
            )
            # return jsonify({"error": _("not_found", data=_("category"))}), 404
    except Exception as e:
        print(f"[{e.__class__.__name__}]: {e}")
        abort(500)
''',
            },
            POST: {
                "desc": "create a new quiz for user",
                "tags": ['User', 'Quiz'],
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
                    CREATED: [{"quiz_id": "int"}],
                    BAD_REQUEST: [{"error": _expr("_('incomplete', data=_('quiz'))")}],
                    NOT_FOUND: [
                        {"error": _expr("_('not_found', data=_('category'))")},
                        {"error": _expr("_('not_found', data=_('group'))")}
                    ],
                    CONFLICT: [{"error": _expr("_('duplicate', data=_('title'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _expr("_('invalid', data=_('duration'))")},
                        {"error": _expr("_('invalid', data=_('points'))")},
                        {"error": _expr("_('invalid', data=_('quiz schedule'))")}
                    ],
                },
                "snippet": '''
    user = getattr(g, "user", None)
    if user is None:
        return jsonify({"error": _("unauthorized")}), 401

    title = req.get("title")
    category = req.get("category")
    difficulty = int(req["difficulty"])
    points = int(req["points"])
    duration = int(req["duration"]) if req.get("duration", None) else None
    start = (
        datetime.strptime(req["start"], time_fmt) if req.get("start", None) else None
    )
    end = datetime.strptime(req["end"], time_fmt) if req.get("end", None) else None
    group_id = int(req["group_id"]) if req.get("group_id", None) else None

    try:
        if storage.query(Quiz).where(Quiz.title == req.get("title")).count() > 0:
            return jsonify({"error": _("duplicate", data=_("title"))}), 409

        if len({type(start), type(end)}) > 1 or start > end or start < datetime.now():
            return jsonify({"error": _("invalid", data=_("quiz schedule"))}), 422
        if group_id:
            if storage.query(Group).get(int(group_id)) is None:
                return jsonify({"error": _("not_found", data=_("group"))}), 404

        quiz = Quiz(
            title=title,
            category=category,
            difficulty=difficulty,
            points=points,
            duration=duration,
            start=start,
            end=end,
            user_id=user.id,
            group_id=group_id,
        )
        storage.new(quiz)
        storage.save()
        return jsonify({}), 201
    except Exception as e:
        print(f"[{e.__class__.__name__}]: {e}")
        abort(500)''',
            },
        },
        "/api/v1/user/quiz/<int:quiz_id>": {
            GET: {
                "desc": "respond with quiz details",
                "tags": ['User', 'Quiz'],
                "request": {},
                "responses": {
                    OK: [{
                        "title": "str",
                        "category": "str",
                        "difficulty": "int",
                        "points": "int",
                        "duration": "int",
                        "start": "datetime",
                        "end": "datetime",
                        "group_id": "int",
                    }],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('quiz'))")}],
                    UNAUTHORIZED: [{"error": _expr("_('unauthorized')")}],
                },
            },
            PUT: {
                "desc": "modify the quiz details",
                "tags": ['User', 'Group', 'Quiz', 'Ownership'],
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
                    OK: [{}],
                    NOT_FOUND: [
                        {"error": _expr("_('not_found', data=_('category'))")},
                        {"error": _expr("_('not_found', data=_('group'))")},
                        {"error": _expr("_('not_found', data=_('quiz'))")},
                    ],
                    CONFLICT: [{"error": _expr("_('duplicate', data=_('title'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _expr("_('invalid', data=_('duration'))")},
                        {"error": _expr("_('invalid', data=_('points'))")},
                        {"error": _expr("_('invalid', data=_('quiz schedule'))")}
                    ],
                },
                "snippet": '''
    user: User = getattr(g, 'user', None)
    if user is None:
        return jsonify({'error': _('unauthorized')}), 401
    
    category = req['category'] if req.get('category', None) else None
    difficulty = int(req['difficulty']) if req.get('difficulty', None) else None
    points = int(req['points']) if req.get('points', None) else None
    duration = int(req['duration']) if req.get('duration', None) else None
    start = datetime.strptime(req['start'], time_fmt) if req.get('start', None) else None
    end = datetime.strptime(req['end'], time_fmt) if req.get('end', None) else None
    title = req['title'] if req.get('title', None) else None
    group_id = int(req['group_id']) if req.get('group_id', None) else None


    try:
        from sqlalchemy import and_
        quiz: Quiz = storage.query(Quiz).where(and_(Quiz.user_id==user.id, Quiz.id==quiz_id))
        if quiz is None:
            return jsonify({'error': _('not_found', data=_('quiz'))}), 404

        if category:
            quiz.category = category
        if difficulty:
            if difficulty < 0:
                return jsonify({'error': _('invalid', data=_('difficulty'))}), 422
            quiz.difficulty = difficulty
        if points:
            if points < 0:
                return jsonify({'error': _('invalid', data=_('points'))}), 422
            quiz.points = points
        if duration:
            if duration < 0:
                return jsonify({'error': _('invalid', data=_('duration'))}), 422
            quiz.duration = duration
        if start or end:
            if len({type(start), type(end)}) > 1 or start > end or start < datetime.now():
                return jsonify({"error": _("invalid", data=_("quiz schedule"))}), 422

        if title:
            if storage.query(Quiz).filter_by(title=title).count() > 0:
                return jsonify({'error': _('duplicate', data=_('title'))}), 409
            quiz.title = title
        if group_id:
            if storage.query(Group).where(and_(Group.id==group_id, Group.ownership_id==Ownership.id, Ownership.user_id==user.id)).one_or_none():
                return jsonify({'error': _('not_found', data=_('group'))}), 404
            quiz.group_id = group_id
        return jsonify({}), 200
    except Exception as e:
        print(f'[{e.__class__.__name__}]: {e}')
        abort(500)
''',
            },
            DELETE: {
                "desc": "delete the user's quiz",
                "tags": ['User', 'Group', 'Quiz', 'Ownership'],
                "request": {},
                "responses": {
                    NO_CONTENT: [{}],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('quiz'))")}],
                },
                "snippet": '''
''',
            },
        },
        "/api/v1/user/quiz/<int:quiz_id>/question": {
            GET: {
                "desc": "respond with the quiz's list of questions",
                "tags": ['User', 'Question', 'Quiz'],
                "request": {},
                "responses": {
                    OK: [{
                        "questions": [
                            {
                                "statement": "str",
                                "points": "int",
                                "type": "str",
                                "options": ["str"],
                                "correct_answer": ["int"],
                            }
                        ]
                    }],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('quiz'))")}],
                },
                "snippet": '''
''',
            },
            POST: {
                "desc": "add questions to the quiz",
                "tags": ['User', 'Question', 'Quiz'],
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
                    CREATED: [{}],
                    BAD_REQUEST: [{"error": _expr("_('missing', data=_('answers'))")}],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('quiz'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _expr("_('invalid', data=_('question type'))")},
                        {"error": _expr("_('invalid', data=_('points'))")},
                        {"error": _expr("_('invalid', data=_('answer option'))")}
                    ],
                },
                "snippet": '''
''',
            },
            PUT: {
                "desc": "modify the quiz's questions",
                "tags": ['User', 'Question', 'Quiz'],
                "request": {
                    "questions": [
                        {
                            "question_id": "int",
                            "statement?": "str",
                            "points?": "int",
                            "type?": "str",
                            "options?": ["str"],
                            "correct_answer?": ["int"],
                        }
                    ]
                },
                "responses": {
                    OK: [{}],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('quiz'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _expr("_('invalid', data=_('question number'))")},
                        {"error": _expr("_('invalid', data=_('question type'))")},
                        {"error": _expr("_('invalid', data=_('points'))")},
                        {"error": _expr("_('invalid', data=_('answer option'))")}
                    ],
                },
                "snippet": '''
''',
            },
            DELETE: {
                "desc": "remove questions from the quiz",
                "tags": ['User', 'Question', 'Quiz'],
                "request": {"questions": [{"question_id": "int"}]},
                "responses": {
                    NO_CONTENT: [{}],
                    NOT_FOUND: [
                        {"error": _expr("_('invalid', data=_('question number'))")},
                        {"error": _expr("_('not_found', data=_('quiz'))")}
                    ],
                },
                "snippet": '''
''',
            },
        },
        "/api/v1/user/quiz/<int:quiz_id>/stats/attempts": {
            GET: {
                "desc": "respond with stats about the user attempts of the quiz",
                "pagination": "attempts",
                "tags": ['User', 'QuizAttempt', 'Quiz'],
                "request": {},
                "responses": {
                    OK: [{
                        "user_id": "int",
                        "user_name": "str",
                        "attempt_id": "int",
                        "time": "datetime",
                        "points": "int",
                    }],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('quiz'))")}],
                },
                "snippet": '''
    user: User = getattr(g, 'user', None)
    if user is None:
        return jsonify({'error': _('unauthorized')}), 401
    page = int(req['page']) if req.get('page', None) else None
    page_size = int(req['page_size']) if req.get('page_size', None) else None
    title_query = req['query'] if req.get('query', None) else None

    from sqlalchemy import and_
    try:
        quiz: Quiz = storage.query(Quiz).where(Quiz.user_id==user.id).filter_by(id=quiz_id).one_or_none()
        if quiz is None:
            return jsonify({'error': _('not_found', data=_('quiz'))}), 404
        query = storage.query(QuizAttempt).where(QuizAttempt.quiz_id==quiz_id)
        if title_query:
            query = query.where(and_(QuizAttempt.user_id==User.id, User.user_name.like(f'%{title_query}%')))
        try:
            return paginate("attempts", query, page, page_size, apply=lambda a: {'user_id': a.user.id, 'user_name': a.user.user_name, 'attempt_id': a.id, 'time': a.created_at, 'points': a.score}), 200
        except ValueError as e:
            data = e.args[0] if e.args and e.args[0] in ("page", "page_size") else "request"
            return jsonify({"error": _("invalid", data=_(data))}), 422
    except Exception as e:
        print(f'[{e.__class__.__name__}]: {e}')
        abort(500)
''',
            }
        },
        "/api/v1/user/quiz/<int:quiz_id>/stats/question/<int:question_id>": {
            GET: {
                "desc": "respond with stats about the user attempts of a quiz's question",
                "pagination": "question_answers",
                "tags": ['User', 'Question', 'Quiz'],
                "request": {},
                "responses": {
                    OK: [{
                        "correct_answers": "int",
                        "wrong_answers": ["int"],
                    }],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('quiz'))")}],
                },
                "snippet": '''
''',
            }
        },
    },
    "profiles": {
        "/api/v1/profile": {
            GET: {
                "desc": "respond with user profile info",
                "pagination": "users",
                "tags": ['User'],
                "request": {},
                "responses": {
                    OK: [{
                        "user_id": "int",
                        "user_name": "str",
                    }],
                },
                "snippet": '''
    page = int(req['page']) if req.get('page', None) else None
    page_size = int(req['page_size']) if req.get('page_size', None) else None
    username_query = req.get('query', None)

    try:
        query = storage.query(User.id, User.user_name)
        
        if username_query:
            query = query.where(User.user_name.like(f'%{username_query}%'))

        return paginate("users", query, page, page_size, lambda u: {'user_id': u[0], 'user_name': u[1]}), 200
    except ValueError as e:
        data = e.args[0] if e.args and e.args[0] in ("page", "page_size") else "request"
        return jsonify({"error": _("invalid", data=_(data))}), 422
    except Exception as e:
        print(f'[{e.__class__.__name__}]: {e}')
        abort(500)
''',
            },
        },
        "/api/v1/profile/<int:user_id>": {
            GET: {
                "desc": "respond with user profile info",
                "tags": ['User', 'Ownership', 'Group', 'Quiz', 'QuizAttempt'],
                "request": {},
                "responses": {
                    OK: [{
                        "user_name": "str",
                        "owned_groups": "int",
                        "created_quizzes": "int",
                        "subscribed_groups": "int",
                        "solved_quizzes": "int",
                    }],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('user'))")}],
                },
                "snippet": '''

''',
            },
        },
        "/api/v1/profile/<int:user_id>/quiz": {
            GET: {
                "desc": "respond with the user's created quizzes",
                "pagination": "quizzes",
                "tags": ['User', 'Quiz'],
                "request": {
                    "category?": "str",
                    "sort_by?": "str",
                    "difficulty?": "int",
                },
                "responses": {
                    OK: [{
                        "quiz_id": "int",
                        "title": "str",
                        "category": "str",
                        "difficulty": "int",
                        "points": "int",
                        "duration": "int",
                    }],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('category'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _expr("_('invalid', data=_('sort key'))")},
                        {"error": _expr("_('invalid', data=_('difficulty'))")}
                    ],
                },
                "snippet": '''
''',
            }
        },
    },
    "quizzes": {
        "/api/v1/quiz": {
            GET: {
                "desc": "respond with quizzes with different filters",
                "pagination": "quizzes",
                "tags": ['Quiz'],
                "request": {
                    "category?": "str",
                    "sort_by?": "str",
                    "difficulty?": "int",
                    "group_id?": "int",
                },
                "responses": {
                    OK: [{
                        "quiz_id": "int",
                        "title": "str",
                        "category": "str",
                        "difficulty": "int",
                        "points": "int",
                        "duration": "int",
                        "start": "datetime",
                        "end": "datetime",
                        "group_id": "int",
                    }],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('category'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _expr("_('invalid', data=_('sort key'))")},
                        {"error": _expr("_('invalid', data=_('difficulty'))")}
                    ],
                },
                "snippet": '''
    user: User = getattr(g, 'user', None)
    if user is None:
        return jsonify({'error': _('unauthorized')}), 401
    category = req['category'] if req.get('category', None) else None
    difficulty = int(req['difficulty']) if req.get('difficulty', None) else None
    sort_by = req['sort_by'] if req.get('sort_by', None) else None
    group_id = int(req['group_id']) if req.get('group_id', None) else None
    page = int(req['page']) if req.get('page', None) else None
    page_size = int(req['page_size']) if req.get('page_size', None) else None
    title_query = req['query'] if req.get('query', None) else None

    try:
        query = storage.query(Quiz)
        
        if group_id:
            query = query.where(Quiz.group_id == group_id)
        if title_query:
            query = query.where(Quiz.title.like(f'%{title_query}%'))
        if sort_by in (
            "title",
            "category",
            "difficulty",
            "points",
            "duration",
            "start",
            "end",
        ):
            query = query.order_by(getattr(Quiz, sort_by))
        if category:
            query = query.where(Quiz.category == category)
        if difficulty:
            query = query.where(Quiz.difficulty == difficulty)
        return paginate("quizzes", query, page, page_size), 200
'''
            },
        },
        "/api/v1/quiz/<int:quiz_id>": {
            GET: {
                "desc": "respond with the quiz's list of questions",
                "tags": ['Quiz', 'Question'],
                "request": {},
                "responses": {
                    OK: [{
                        "questions": [
                            {
                                "statement": "str",
                                "points": "int",
                                "type": "str",
                                "options": ["str"],
                            }
                        ]
                    }],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('quiz'))")}],
                    # GONE: [{"error": _expr("_('deleted', data=_('quiz'))")}],
                },
                "snippet": '''
    try:
        if storage.query(Quiz).where(Quiz.id==quiz_id).one_or_none() is None:
            return jsonify({'error': _('not_found', data=_('quiz'))}), 404

        questions = []
        for q in storage.query(Question).where(Question.quiz_id==quiz_id).order_by(Question.order).all():
            questions.append({
                "statement": q.statement,
                "points": q.points,
                "type": q.type,
                "options": [ans.text for ans in q.answers],
            })

        return jsonify({'questions': questions}), 200
        # return jsonify({'error': _('deleted', data=_('quiz'))}), 410
    except Exception as e:
        print(f'[{e.__class__.__name__}]: {e}')
        abort(500)
'''
            },
        },
        "/api/v1/quiz/<int:quiz_id>/stats": {
            GET: {
                "desc": "respond with stats about the user attempts of the quiz",
                "tags": ['Quiz', 'QuizAttempt'],
                "request": {},
                "responses": {
                    OK: [
                        {
                            "max_score": "float",
                            "min_score": "float",
                            "average_score": "float",
                            "attempts": "int",
                        }
                    ],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('quiz'))")}],
                },
                "snippet": '''
    from sqlalchemy import func, distinct
    try:
        if storage.query(Quiz).get(quiz_id) is None:
            return jsonify({'error': _('not_found', data=_('quiz'))}), 404
        stats = storage.query(func.max(QuizAttempt.score), func.min(QuizAttempt.score), func.avg(QuizAttempt.score), func.count(distinct(Quiz.user_id))).where(QuizAttempt.quiz_id==quiz_id)
        return jsonify({'max_score': stats[0], 'min_score': stats[1], 'average_score': stats[2], 'attempts': stats[3]}), 200
    except Exception as e:
        print(f'[{e.__class__.__name__}]: {e}')
        abort(500)
'''
            }
        },
    },
    "groups": {
        "/api/v1/group": {
            GET: {
                "desc": "respond with a list of available user groups",
                "pagination": "groups",
                "tags": ['User', 'Group', 'Ownership'],
                "request": {},
                "responses": {
                    OK: [{
                        "group_id": "int",
                        "title": "str",
                        "owner_id": "int",
                        "owner_name": "str",
                    }],
                },
                "snippet": '''
    page = int(req['page']) if req.get('page', None) else None
    page_size = int(req['page_size']) if req.get('page_size', None) else None
    title_query = req['query'] if req.get('query', None) else None

    try:
        query = storage.query(Group)
        if title_query:
            query = query.where(Group.title.like(f'%{title_query}%'))
        try:
            return paginate("groups", query, page, page_size, apply=lambda group: {
                'group_id': group.id, 'title': group.title, 'owner_id': group.ownership.user_id, 'owner_name': group.ownership.user.user_name}
                            ), 200
        except ValueError as e:
            data = e.args[0] if e.args and e.args[0] in ("page", "page_size") else "request"
            return jsonify({"error": _("invalid", data=_(data))}), 422
    except Exception as e:
        print(f'[{e.__class__.__name__}]: {e}')
        abort(500)
''',
            }
        },
        "/api/v1/group/<int:group_id>/users": {
            GET: {
                "desc": "respond with a list of the groups subscribed users",
                "pagination": "users",
                "tags": ['User', 'Group', 'QuizAttempt'],
                "request": {
                    "sort_by?": "str",
                    "status?": "str",
                    "max_score?": "int",
                    "min_score?": "int",
                },
                "responses": {
                    OK: [{
                        "user_id": "int",
                        "user_name": "str",
                        "status": "str",
                        "score": "int",
                    }],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('group'))")}],
                    FORBIDDEN: [{"error": _expr("_('unauthorized')")}],
                },
                "snippet": '''
    sort_by = req.get('sort_by', None)
    status = req.get('status', None)
    max_score = int(req['max_score']) if req.get('max_score', None) else None
    min_score = int(req['min_score']) if req.get('min_score', None) else None
    page = int(req['page']) if req.get('page', None) else None
    page_size = int(req['page_size']) if req.get('page_size', None) else None
    username_query = req.get('query', None)

    from sqlalchemy import func, and_
    try:
        group = storage.get(Group, group_id)
        if group is None:
            return jsonify({'error': _('not_found', data=_('group'))}), 404

        # return jsonify({'error': _('unauthorized')}), 403
        query = (
            storage.query(User, func.sum(QuizAttempt.score))
            .join(QuizAttempt, User.id == QuizAttempt.user_id)  # Join User with QuizAttempt
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id)  # Join QuizAttempt with Quiz
            .where(Quiz.group_id == group_id)  # Filter by the Quiz group ID
            .group_by(User.id)  # Group by User ID
        )
        filters = []
        if username_query:
            filters.append(User.user_name.like(f"%{username_query}%"))  # Filter users by username
        if min_score:
            filters.append(func.sum(QuizAttempt.score) >= min_score)
        if max_score:
            filters.append(func.sum(QuizAttempt.score) <= max_score)
        if status:
            filters.append(func.count(User.user_sessions) > 0)
        query = query.having(*filters)
        if sort_by:
            if sort_by == 'score':
                query = query.order_by(func.sum(QuizAttempt.score).desc())
            if sort_by == 'user_name':
                query = query.order_by(User.user_name.asc())
        try:
            return paginate("users", query, page, page_size, apply=lambda u: {'user_id': u[0].id, 'user_name': u[0].user_name, 'status': "active" if len(u[0].user_sessions) > 0 else "away", 'score': u[1]}), 200
        except ValueError as e:
            data = e.args[0] if e.args and e.args[0] in ("page", "page_size") else "request"
            return jsonify({"error": _("invalid", data=_(data))}), 422
    except Exception as e:
        print(f'[{e.__class__.__name__}]: {e}')
        abort(500)
''',
            },
        },
        "/api/v1/group/<int:group_id>/quizzes": {
            GET: {
                "desc": "respond with all the schedualed quizzes",
                "pagination": "quizzes",
                "tags": ['User', 'Group', 'Ownership', 'Quiz'],
                "request": {
                    "category?": "str",
                    "sort_by?": "str",
                    "difficulty?": "int",
                },
                "responses": {
                    OK: [{
                        "quiz_id": "int",
                        "title": "str",
                        "start": "datetime",
                        "end": "datetime",
                    }],
                    NOT_FOUND: [{"error": _expr("_('not_found', data=_('group'))")}],
                },
                "snippet": '''
    try:
        if storage.query(Group).get(group_id) is None:
            return jsonify({'error': _('not_found', data=_('group'))}), 404
        query = storage.query(Quiz).where(Quiz.group_id == group_id)

        sort_by = req.get("sort_by", None)
        if sort_by in (
            "title",
            "category",
            "difficulty",
            "points",
            "duration",
            "start",
            "end",
        ):
            query = query.order_by(getattr(Quiz, sort_by))
        for k in ("category", "difficulty"):
            if req.get(k, None):
                query = query.where(getattr(Quiz, k) == req[k])

        try:
            return (
                paginate(
                    "quizzes", query, req.get("page", None), req.get("page_size", None)
                ),
                200,
            )
        except ValueError as e:
            data = (
                e.args[0]
                if e.args and e.args[0] in ("page", "page_size")
                else "request"
            )
            return (
                jsonify(
                    {
                        "error": _(
                            "invalid",
                            data=_(data),
                        )
                    }
                ),
                422,
            )
    except Exception as e:
        print(f'[{e.__class__.__name__}]: {e}')
        abort(500)
''',
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

route_template = """from datetime import datetime
from flask import jsonify, request, g, abort
from flask_babel import _
from flasgger import swag_from

from api.v1.routes import app_routes
from api.v1.schemas import json_validate
from api.v1.schemas.{section} import (
    {schemas}
)
from models import storage, {tags}
from models.base import time_fmt
from models.engine.relational_storage import paginate

{routes}"""

schema_template = """\"\"\"JSON request validation schemas for the {section} endpoints
\"\"\"

{schemas}"""


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
    elif value == "str" or type(value) is _expr:
        # if type(value) is _expr:
        #     print(value)
        return {"type": "string"}
    elif value == "datetime":
        return {"type": "string", "format": "date-time"}
    elif value == "url":
        return {"type": "string", "format": "uri"}
    elif value == "email":
        return {"type": "string", "format": "email"}
    else:
        PATTERNS = {
            # "datetime": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+$",
            # "url": r"^(https?|ftp|file)://([A-Za-z0-9.-]+)(:[0-9]+)?(/[^?#]*)?(\?[^#]*)?(#.*)?$",
            "uuid": r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
        }
        return {"type": "string", "pattern": PATTERNS[value]}


def route_handler_name(path, method):
    method_er = {GET: "getter", POST: "poster", PUT: "putter", DELETE: "deleter"}

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
    route_code = f"""
@app_routes.route("{path[7:]}", methods=["{method}"], strict_slashes=False)
@swag_from('documentation/{section}/{route_handler}.yml')
def {route_handler}({params}):
    \"\"\"{method} {path}
    Return:
      - on success: {desc}
      - on error: respond with {', '.join(str(err) for err in sorted(responses) if str(err)[0] != '2')} error codes
    \"\"\"
    req = dict(request.args)
    if request.content_type == 'application/json':
        req.update(request.json)
    SCHEMA = {route_handler.upper()}_SCHEMA
    error_response = json_validate(req, SCHEMA)
    if error_response is not None:
        return error_response
"""
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
                                "error": _expr("_('invalid', data=_('page'))")
                            },
                            UNPROCESSABLE_ENTITY: {
                                "error": _expr("_('invalid', data=_('page_size'))")
                            },
                        }
                    )

                route_handler = route_handler_name(path, method)
                # routes += generate_route_function(
                #     path,
                #     section,
                #     route_handler,
                #     method,
                #     desc,
                #     request,
                #     responses,
                #     pagination,
                #     snippet,
                # )
                schemas[f"{route_handler.upper()}_SCHEMA"] = repr(
                    generate_json_schema(request)
                )

        # routes_file_path = os.path.join(
        #     base_path, "api", "v1", "routes", section + ".py"
        # )
        # create_file(
        #     routes_file_path,
        #     route_template.format(
        #         routes=routes, section=section, schemas=",\n    ".join(schemas.keys()), tags=', '.join(sorted(set(section_tags + ['User'])))
        #     ),
        # )

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
    # create_routes_init_file(project_name, list(endpoints.keys()))


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

if storage.query(User).where(User.user_name == 'admin').one_or_none() is None:
	admin = storage.new(User(email='admin@quizquickie.com', password=hashpw('admin'.encode(), gensalt()), user_name='admin')).save()
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

def generate_yaml_files(base_path, endpoints):
    import yaml

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
                    # print(response_code, end=' : ')
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


def generate_translations(project_name):
    import requests as rs

    os.chdir(os.path.join(os.getcwd(), project_name, "api", "v1"))
    os.system(f"pybabel extract -F babel.cfg -k _l -o messages.pot .")

    lines = []

    from config import Config

    for lang in Config.LANGUAGES:
        lang_po = os.path.join("translations", lang, "LC_MESSAGES", "messages.po")

        os.system(f"pybabel init -i messages.pot -d translations -l {lang}")


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

    # create_directories(base_path, project_structure)

    # # create_test_directories(os.path.join(base_path, "tests"), "", project_structure)

    # # Generate dynamic code for routes
    generate_routes(base_path, endpoints)

    # relational_models = json.load(open(project_name + ".erdplus", "+br"))

    # generate_models(project_name, relational_models)

    generate_yaml_files(base_path, endpoints)

    # mirror_existing_files(project_name)

    # # generate_translations(project_name)

    # os.system(f"black -q {project_name}")
    
    # generate_postman_collection(project_name, endpoints)
    
    # tests = json.load(open(project_name + "_tests.json", "+br"))

    # generate_postman_test_collection(project_name, tests)

    # su.copytree(base_path, os.path.dirname(os.getcwd()), dirs_exist_ok=True)


import json
import requests

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
        response = requests.post(
            "https://api.getpostman.com/collections",
            headers={"X-Api-Key": postman_api_key, "Content-Type": "application/json"},
            json={'collection': collection}
        )
        print(response.status_code, response.json())
    else:
        with open(f'{project_name}.postman_collection.json', 'w') as f:
            json.dump(collection, f)






tests = [
    {"name": ""},
]



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
        var expected = {json.dumps(json.loads(repr(response)), indent=4)};
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
        response = requests.post(
            "https://api.getpostman.com/collections",
            headers={"X-Api-Key": postman_api_key, "Content-Type": "application/json"},
            json={'collection': collection}
        )
        print(response.status_code, response.json())
    else:
        with open(f'{project_name}_test.postman_collection.json', 'w') as f:
            json.dump(collection, f)

# Run the generator
generate_flask_project("QuizQuickie")


# for section, routes in endpoints.items():
#     for route, methods in sorted(routes.items()):
#         for method, details in methods.items():
#             if method == 'POST':
#                 # print(f"rs.{method.lower()}(url=\"{route}\", json={repr(details['request'])})")
#                 print(f"{route}:\n\t{method}: {repr(details['request'])}")
