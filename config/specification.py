from utils.http_constants import *
from utils.unquoted_string import _

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
                    UNAUTHORIZED: [{"error": _("_('unauthorized')")}],
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
                    CONFLICT: [{"error": _("_('duplicate', data=_('email'))")},
                    {"error": _("_('duplicate', data=_('user_name'))")}],
                    BAD_REQUEST: [{
                        "error": _("_('incomplete', data=_('login details'))")
                    }],
                    UNPROCESSABLE_ENTITY: [{
                        "error": _("_('invalid', data=_('login details'))")
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
                        "error": _("_('invalid', data=_('login details'))")
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
                    UNAUTHORIZED: [{"error": _("_('unauthorized')")}],
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
                        "error": _("_('invalid', data=_('token or password'))")
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
                    UNAUTHORIZED: [{"error": _("_('unauthorized')")}],
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
                    UNAUTHORIZED: [{"error": _("_('unauthorized')")}],
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
                    UNAUTHORIZED: [{"error": _("_('unauthorized')")}],
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
                    BAD_REQUEST: [{"error": _("_('invalid', data=_('profile'))")}],
                    CONFLICT: [{"error": _("_('duplicate', data=_('user_name'))")}],
                    UNAUTHORIZED: [{"error": _("_('unauthorized')")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('quiz'))")}],
                    GONE: [{"error": _("_('deleted', data=_('quiz'))")}],
                    FORBIDDEN: [{"error": _("_('quiz time has ended')")}],
                    UNAUTHORIZED: [{"error": _("_('unauthorized')")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('quiz'))")}],
                    UNAUTHORIZED: [{"error": _("_('unauthorized')")}],
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
                    UNAUTHORIZED: [{"error": _("_('unauthorized')")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('group'))")}],
                    CONFLICT: [{"error": _("_('already subscribed to group')")}],
                    GONE: [{"error": _("_('deleted', data=_('group'))")}],
                    UNAUTHORIZED: [{"error": _("_('unauthorized')")}],
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
                        {"error": _("_('not_found', data=_('group'))")},
                        {"error": _("_('user not subscribed to group')")}
                    ],
                    UNAUTHORIZED: [{"error": _("_('unauthorized')")}],
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
                    UNAUTHORIZED: [{"error": _("_('unauthorized')")}],
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
                    CONFLICT: [{"error": _("_('duplicate', data=_('group'))")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('group'))")}],
                },
            },
            PUT: {
                "desc": "update user group details",
                "tags": ['User', 'Group', 'Ownership'],
                "request": {"title": "str"},
                "responses": {
                    OK: [{}],
                    CONFLICT: [{"error": _("_('duplicate', data=_('title'))")}],
                    NOT_FOUND: [{"error": _("_('not_found', data=_('group'))")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('group'))")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('group'))")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('group'))")}],
                    CONFLICT: [{"error": _("_('duplicate', data=_('user'))")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('group'))")}],
                    CONFLICT: [{"error": _("_('duplicate', data=_('user'))")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('category'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _("_('invalid', data=_('sort key'))")},
                        {"error": _("_('invalid', data=_('difficulty'))")}
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
                    BAD_REQUEST: [{"error": _("_('incomplete', data=_('quiz'))")}],
                    NOT_FOUND: [
                        {"error": _("_('not_found', data=_('category'))")},
                        {"error": _("_('not_found', data=_('group'))")}
                    ],
                    CONFLICT: [{"error": _("_('duplicate', data=_('title'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _("_('invalid', data=_('duration'))")},
                        {"error": _("_('invalid', data=_('points'))")},
                        {"error": _("_('invalid', data=_('quiz schedule'))")}
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('quiz'))")}],
                    UNAUTHORIZED: [{"error": _("_('unauthorized')")}],
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
                        {"error": _("_('not_found', data=_('category'))")},
                        {"error": _("_('not_found', data=_('group'))")},
                        {"error": _("_('not_found', data=_('quiz'))")},
                    ],
                    CONFLICT: [{"error": _("_('duplicate', data=_('title'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _("_('invalid', data=_('duration'))")},
                        {"error": _("_('invalid', data=_('points'))")},
                        {"error": _("_('invalid', data=_('quiz schedule'))")}
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('quiz'))")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('quiz'))")}],
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
                    BAD_REQUEST: [{"error": _("_('missing', data=_('answers'))")}],
                    NOT_FOUND: [{"error": _("_('not_found', data=_('quiz'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _("_('invalid', data=_('question type'))")},
                        {"error": _("_('invalid', data=_('points'))")},
                        {"error": _("_('invalid', data=_('answer option'))")}
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('quiz'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _("_('invalid', data=_('question number'))")},
                        {"error": _("_('invalid', data=_('question type'))")},
                        {"error": _("_('invalid', data=_('points'))")},
                        {"error": _("_('invalid', data=_('answer option'))")}
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
                        {"error": _("_('invalid', data=_('question number'))")},
                        {"error": _("_('not_found', data=_('quiz'))")}
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('quiz'))")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('quiz'))")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('user'))")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('category'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _("_('invalid', data=_('sort key'))")},
                        {"error": _("_('invalid', data=_('difficulty'))")}
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('category'))")}],
                    UNPROCESSABLE_ENTITY: [
                        {"error": _("_('invalid', data=_('sort key'))")},
                        {"error": _("_('invalid', data=_('difficulty'))")}
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
    except Exception as e:
        print(f'[{e.__class__.__name__}]: {e}')
        abort(500)
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('quiz'))")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('quiz'))")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('group'))")}],
                    FORBIDDEN: [{"error": _("_('unauthorized')")}],
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
                    NOT_FOUND: [{"error": _("_('not_found', data=_('group'))")}],
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
