from typing import Literal
from faker import Faker
import requests as rs
import unittest as ut
import random
from datetime import datetime, timedelta
from pprint import pformat
from models.base import time_fmt

faker = Faker()

HOST = "http://localhost:5000"


def paginated_response(item_name, items, page, page_size, apply):
    total_items = len(items)
    total_pages = (
        total_items + page_size - 1
    ) // page_size  # Round up to get total pages
    start = (page - 1) * page_size
    end = start + page_size
    items_page = items[start:end]
    return {
        item_name: [apply(item) for item in items_page],
        "page": page,
        "next": page + 1 if page < total_pages else page,
        "prev": page - 1 if page > 1 else page,
        "page_size": page_size,
        f"total_{item_name}": len(items),
        "total_pages": total_pages,
    }


def _user_login(asrt, user):
    resp = rs.post(
        url=f"{HOST}/api/v1/auth/login",
        json={
            "email": user["email"],
            "password": user["password"],
        },
    )
    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual({}, resp.json())

    session_cookie = {"session_id": resp.cookies["session_id"]}
    user["session"] = session_cookie
    return session_cookie

def _gen_quiz():
    quiz = {
        "title": faker.sentence(nb_words=3),
        "category": random.choice(["Science", "Math", "History", "Programming"]),
        "difficulty": random.randint(1, 5),
        "points": random.randint(10, 100),
        "duration": (random.randint(10, 60)),
        # 'group_id': group['id'] if random.choice([True, False]) else None
    }
    start: datetime = faker.date_time_between(start_date="+1d", end_date="+2d")
    end: datetime = faker.date_time_between(start_date="+2d", end_date="+3d")

    quiz["start"] = datetime.strftime(start, time_fmt)
    quiz["end"] = datetime.strftime(end, time_fmt)
    return quiz
    
    

def _gen_question():
    question = {
        "statement": faker.sentence(),
        "points": random.randint(1, 10),
        "type": random.choice(["TFQ", "SCQ", "MCQ"]),
        "options": [],
        "correct_answer": [],
    }

    match question['type']:
        case 'TFQ':
            question["options"] = ['true', 'false']
            question["correct_answer"] = [random.randint(0, 1)]
        case 'SCQ':
            opt_count = random.randint(2, 10)
            question["options"] = [faker.sentence(nb_words=2) for _ in range(opt_count)]
            question["correct_answer"] = [random.randint(0, opt_count-1)]
        case 'MCQ':
            opt_count = random.randint(2, 10)
            cor_count = random.randint(1, opt_count-1)
            question["options"] = [faker.sentence(nb_words=2) for _ in range(opt_count)]
            question["correct_answer"] = list(set(random.randint(0, opt_count-1) for _ in range(cor_count)))
    return question

def _gen_attempt(questions):
    answers = []
    for q in questions:
        match q['type']:
            case 'TFQ':
                answer = q['correct_answer'] if random.randint(1, 100) <= 70 else [random.randint(0, 1)]
            case 'SCQ':
                l = len(q['options'])
                answer = q['correct_answer'] if random.randint(1, 100) <= 70 else [random.randint(0, l)]
            case 'MCQ':
                l = len(q['options'])
                cor = random.randint(1, l-1)
                answer = q['correct_answer'] if random.randint(1, 100) <= 70 else [random.randint(0, l) for _ in range(cor)]
        answers.append({"options": answer})
    
    total_score = 0
    
    for ans in answers:
        if set(ans['options']) == set(q['correct_answer']):
            total_score += q['points']
    return total_score, {"answers": answers}


def check_status(asrt: ut.TestCase):
    """Check Status"""
    print("GET /status")
    resp = rs.get(url=f"{HOST}/api/v1/status")
    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual({"status": "OK"}, resp.json())
    print("(OK)")


def create_users(asrt: ut.TestCase) -> list:
    users = [
        {
            "email": faker.email(),
            "password": faker.password(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
            "user_name": faker.user_name(),
            "profile_picture": (
                faker.image_url() if random.choice([True, False]) else None
            ),
        }
        for _ in range(20)
    ]

    # Create user (main) and 19 other new users
    users = list(sorted(users, key=lambda u: u["user_name"]))

    print("POST /auth/signup")
    for user in users:
        resp = rs.post(url=f"{HOST}/api/v1/auth/signup", json=user)
        asrt.assertEqual(resp.status_code, 201)
        user['id'] = resp.json()["user_id"]
    print("(OK)")
        

    # Check all added users
    print("GET /profile")
    resp = rs.get(url=f"{HOST}/api/v1/profile", json={"page": 1, "page_size": 10})
    asrt.assertEqual(resp.status_code, 200)
    resp = resp.json()


    paginated_users = paginated_response(
        "users",
        users,
        1,
        10,
        lambda u: {
            "user_id": u["id"],
            "user_name": u["user_name"],
        },
    )

    asrt.assertDictEqual(
        paginated_users, resp, pformat(paginated_users) + "\n\n" + pformat(resp)
    )
    print("(OK)")
    return users


def user_crud(asrt: ut.TestCase):
    """User profile & auth functionality"""
    # Create a new user (dummy)
    dummy = {
        "email": faker.email(),
        "password": faker.password(),
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "user_name": faker.user_name(),
        "profile_picture": faker.image_url() if random.choice([True, False]) else None,
    }
    print("POST /auth/signup")
    resp = rs.post(url=f"{HOST}/api/v1/auth/signup", json=dummy)
    asrt.assertEqual(resp.status_code, 201)
    dummy["id"] = resp.json()["user_id"]
    print("(OK)")

    # Login with (dummy)
    session_cookie = _user_login(asrt, dummy)

    # Check profile details
    print("GET /user/profile")
    resp = rs.get(url=f"{HOST}/api/v1/user/profile", cookies=session_cookie)

    asrt.assertEqual(resp.status_code, 200)
    d_user = {
        "user": {
            "email": dummy["email"],
            "first_name": dummy["first_name"],
            "last_name": dummy["last_name"],
            "user_name": dummy["user_name"],
            "profile_picture": dummy["profile_picture"],
        }
    }
    asrt.assertDictEqual(d_user, resp.json())

    # Update profile details
    update = {
        "first_name": faker.first_name(),
        "last_name": faker.last_name(),
        "user_name": faker.user_name(),
        "profile_picture": faker.image_url(),
    }
    dummy.update(update)
    resp = rs.put(
        url=f"{HOST}/api/v1/user/profile", json=update, cookies=session_cookie
    )
    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual({}, resp.json())

    # Check updated profile details
    d_user = {
        "user": {
            "email": dummy["email"],
            "first_name": dummy["first_name"],
            "last_name": dummy["last_name"],
            "user_name": dummy["user_name"],
            "profile_picture": dummy["profile_picture"],
        }
    }
    resp = rs.get(url=f"{HOST}/api/v1/user/profile", cookies=session_cookie)

    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual(d_user, resp.json())

    # Get Reset token (no email)
    resp = rs.get(url=f"{HOST}/api/v1/auth/password/reset", cookies=session_cookie)

    asrt.assertEqual(resp.status_code, 200)
    reset_token = resp.json()["reset_token"]

    # Reset password
    new_password = faker.password()
    dummy["password"] = new_password
    resp = rs.post(
        url=f"{HOST}/api/v1/auth/password/reset/confirm",
        json={"reset_token": reset_token, "new_password": new_password},
        cookies=session_cookie,
    )
    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual({}, resp.json())

    # Logout
    resp = rs.delete(url=f"{HOST}/api/v1/auth/logout", cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 204)

    # Test login
    resp = rs.get(url=f"{HOST}/api/v1/user/profile", cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 403)

    # Login again with (dummy)
    session_cookie = _user_login(asrt, dummy)

    # Deactivate account
    resp = rs.delete(url=f"{HOST}/api/v1/auth/deactivate", cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 204)

    # Test login
    resp = rs.get(url=f"{HOST}/api/v1/user/profile", cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 403)


def create_groups(asrt: ut.TestCase, users) -> list:
    # Login with (main)
    user = users[0]
    session_cookie = _user_login(asrt, user)

    # Create group (main) and 19 other new groups
    groups = [{"title": faker.sentence(nb_words=3)} for _ in range(20)]
    groups = list(sorted(groups, key=lambda g: g['title']))

    print("POST /user/group")
    for group in groups:
        resp = rs.post(
            f"{HOST}/api/v1/user/group",
            json=group,
            cookies=session_cookie,
        )
        asrt.assertEqual(resp.status_code, 201)
        group["id"] = resp.json()["group_id"]
        group["owner_id"] = user['id']
        group["owner_name"] = user['user_name']
    print("(OK)")

    # Check all added groups
    print("GET /group")
    resp = rs.get(url=f"{HOST}/api/v1/group", json={"page": 1, "page_size": 10})
    asrt.assertEqual(resp.status_code, 200)
    resp = resp.json()
    paginated_groups = paginated_response(
        "groups",
        groups,
        1,
        10,
        lambda g: {"group_id": g["id"], "title": g['title'], "owner_id": g['owner_id'], "owner_name": g['owner_name']},
    )
    asrt.assertDictEqual(paginated_groups, resp, pformat(paginated_groups) + "\n\n" + pformat(resp))
    print("(OK)")
    return groups


def group_crud(asrt: ut.TestCase, user):
    """Group CRUD functionality"""
    session_cookie = user["session"]

    # Create group (dummy)
    dummy = {"title": faker.sentence(nb_words=3)}
    print("POST /user/group")
    resp = rs.post(
        f"{HOST}/api/v1/user/group",
        json=dummy,
        cookies=session_cookie,
    )
    asrt.assertEqual(resp.status_code, 201)
    print("(OK)")

    dummy["id"] = resp.json()["group_id"]

    # Check group details
    print("GET /user/group/<int:group_id>")
    resp = rs.get(f"{HOST}/api/v1/user/group/{dummy["id"]}", cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual({"group": {"title": dummy["title"]}}, resp.json())
    print("(OK)")


    # Update group details
    update = {"title": faker.sentence(nb_words=3)}
    dummy.update(update)
    print("PUT /user/group/<int:group_id>")
    resp = rs.put(
        f"{HOST}/api/v1/user/group/{dummy["id"]}", json=update, cookies=session_cookie
    )
    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual({}, resp.json())
    print("(OK)")

    # Check group details (after update)
    print("GET /user/group/<int:group_id>")
    resp = rs.get(f"{HOST}/api/v1/user/group/{dummy["id"]}", cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual({"group": {"title": dummy["title"]}}, resp.json())
    print("(OK)")

    # Delete group
    print("DELETE /user/group/<int:group_id>")
    resp = rs.delete(f"{HOST}/api/v1/user/group/{dummy["id"]}", cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 204)
    print("(OK)")


def subscribe_to_groups(asrt: ut.TestCase, user, groups):
    # Subscribe user (main) to groups (10-20)
    session_cookie = user["session"]

    print("POST /user/profile/group")
    for group in groups[10:20]:
        resp = rs.post(
            f"{HOST}/api/v1/user/profile/group",
            json={"group_id": group["id"]},
            cookies=session_cookie,
        )
        asrt.assertEqual(resp.status_code, 200)
        asrt.assertDictEqual(resp.json(), {})
    print("(OK)")

    # List user groups
    print("GET /user/profile/group")
    resp = rs.get(f"{HOST}/api/v1/user/profile/group", json={'page': 1, 'page_size': 20}, cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 200)
    paginated_user_groups = paginated_response(
        "groups",
        groups[10:20],
        1,
        20,
        lambda g: {"group_id": g["id"], "group_title": g["title"]},
    )
    asrt.assertDictEqual(resp.json(), paginated_user_groups, pformat(paginated_user_groups) + '\n'+ pformat(resp.json()))
    print("(OK)")

    # Unsubscribe user (main) from groups (13-18)
    print("DELETE /user/profile/group/<int:group_id>")
    for group in groups[13:18]:
        resp = rs.delete(
            f"{HOST}/api/v1/user/profile/group/{group['id']}", cookies=session_cookie
        )
        asrt.assertEqual(resp.status_code, 204)
    print("(OK)")


    # List user groups (after unsubscription)
    print("GET /user/profile/group")
    resp = rs.get(f"{HOST}/api/v1/user/profile/group", json={"page": 1, "page_size": 20}, cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 200)
    paginated_user_groups = paginated_response(
        "groups",
        groups[10:13] + groups[18:20],
        1,
        20,
        lambda g: {"group_id": g["id"], "group_title": g["title"]},
    )
    asrt.assertDictEqual(resp.json(), paginated_user_groups)
    print("(OK)")


def add_users_to_group(asrt: ut.TestCase, group, users):
    # Add users (10-20) to group (main)
    session_cookie = users[0]["session"]

    print("POST /user/group/<int:group_id>/users")
    resp = rs.post(
        f"{HOST}/api/v1/user/group/{group['id']}/users",
        json={"users": [{"user_id": u["id"]} for u in users[10:20]]},
        cookies=session_cookie,
    )
    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual(resp.json(), {})
    print("(OK)")

    for i in range(10, 20):
        users[i].update(
            {
                "total_score": {group["id"]: 0},
                "attempted_quizzes": {group["id"]: 0},
            }
        )
    # List group (main) users
    print("GET /user/group/<int:group_id>/users")
    resp = rs.get(
        f"{HOST}/api/v1/user/group/{group['id']}/users", json={"page": 1, "page_size": 20}, cookies=session_cookie
    )
    asrt.assertEqual(resp.status_code, 200)

    paginated_group_users = paginated_response(
        "users",
        users[10:20],
        1,
        20,
        lambda u: {
            "user_id": u["id"],
            "user_name": u["user_name"],
            "total_score": u["total_score"][group["id"]],
            "attempted_quizzes": u["attempted_quizzes"][group["id"]],
        },
    )
    asrt.assertDictEqual(resp.json(), paginated_group_users, f"\n{pformat(resp.json())}\n{pformat(paginated_group_users)}")
    print("(OK)")

    print("DELETE /user/group/<int:group_id>/users")
    # Remove users (13-18) from group (main)
    resp = rs.delete(
        f"{HOST}/api/v1/user/group/{group['id']}/users",
        json={"users": [{"user_id": u["id"]} for u in users[13:18]]},
        cookies=session_cookie,
    )
    asrt.assertEqual(resp.status_code, 204)
    print("(OK)")

    # List group (main) users (after removal)
    print("GET /user/group/<int:group_id>/users")
    resp = rs.get(
        f"{HOST}/api/v1/user/group/{group['id']}/users", json={"page": 1, "page_size": 20}, cookies=session_cookie
    )
    asrt.assertEqual(resp.status_code, 200)

    paginated_group_users = paginated_response(
        "users",
        users[10:13] + users[18:20],
        1,
        20,
        lambda u: {
            "user_id": u["id"],
            "user_name": u["user_name"],
            "total_score": u["total_score"][group["id"]],
            "attempted_quizzes": u["attempted_quizzes"][group["id"]],
        },
    )
    asrt.assertDictEqual(resp.json(), paginated_group_users)
    print("(OK)")


def create_quizzes(asrt: ut.TestCase, user, group) -> list:
    session_cookie = user["session"]

    # Create quiz (main) and 19 other new quizzes
    quizzes = [_gen_quiz() for _ in range(20)]
    quizzes = list(sorted(quizzes, key=lambda q: q["title"]))

    print("POST /user/quiz")
    for quiz in quizzes:
        resp = rs.post(
            f"{HOST}/api/v1/user/quiz",
            json=quiz,
            cookies=session_cookie,
        )
        asrt.assertEqual(resp.status_code, 201)
        quiz["id"] = resp.json()["quiz_id"]
    print("(OK)")


    # Check all added quizzes
    print("GET /quiz")
    resp = rs.get(
        url=f"{HOST}/api/v1/quiz",
        json={"page": 1, "page_size": 20},
        cookies=session_cookie,
    )
    asrt.assertEqual(resp.status_code, 200)
    resp = resp.json()
    print("(OK)")

    paginated_quizzes = paginated_response(
        "quizzes",
        quizzes,
        1,
        20,
        lambda q: {
            "quiz_id": q["id"],
            "title": q["title"],
            "category": q["category"],
            "difficulty": q["difficulty"],
            "points": q["points"],
            "duration": q["duration"],
            "start": q["start"],
            "end": q["end"],
            "group_id": q.get("group_id", None),
        },
    )
    asrt.assertDictEqual(paginated_quizzes, resp)

    # Add quizzes (10-20) to group (main)
    update = {"group_id": group["id"]}
    
    for i in range(10, 20):
        quizzes[i].update(update)

    print("PUT /user/quiz/<int:quiz_id>")
    for i in range(10, 20):
        resp = rs.put(
            f"{HOST}/api/v1/user/quiz/{quizzes[i]['id']}",
            json=update,
            cookies=session_cookie,
        )
        asrt.assertEqual(resp.status_code, 200)
        asrt.assertDictEqual(resp.json(), {})
    print("(OK)")

    # List group (main) quizzes
    resp = rs.get(f"{HOST}/api/v1/group/{group['id']}/quizzes", json={"page": 1, "page_size": 20}, cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 200)
    paginated_group_quizzes = paginated_response(
        "quizzes",
        quizzes[10:20],
        1,
        20,
        lambda q: {
            "quiz_id": q["id"],
            "title": q["title"],
            "start": q["start"],
            "end": q["end"],
        },
    )

    asrt.assertDictEqual(resp.json(), paginated_group_quizzes)

    # List quizzes (after exclusion)
    resp = rs.get(
        url=f"{HOST}/api/v1/quiz",
        json={"page": 1, "page_size": 20},
        cookies=session_cookie,
    )
    asrt.assertEqual(resp.status_code, 200)
    resp = resp.json()

    paginated_quizzes = paginated_response(
        "quizzes",
        quizzes[:10],
        1,
        20,
        lambda q: {
            "quiz_id": q["id"],
            "title": q["title"],
            "category": q["category"],
            "difficulty": q["difficulty"],
            "points": q["points"],
            "duration": q["duration"],
            "start": q["start"],
            "end": q["end"],
            "group_id": q.get("group_id", None),
        },
    )
    asrt.assertDictEqual(paginated_quizzes, resp)
    return quizzes

def quiz_crud(asrt: ut.TestCase, user, group):
    """Quiz CRUD functionality"""
    session_cookie = user['session']
    # Create quiz (dummy)
    dummy = _gen_quiz()
    resp = rs.post(f"{HOST}/api/v1/user/quiz", json=dummy, cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 201)
    dummy['id'] = resp.json()['quiz_id']

    # Check quiz details
    resp = rs.get(f"{HOST}/api/v1/user/quiz/{dummy['id']}", cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual(resp.json(), {
        "title": dummy['title'],
        "category": dummy['category'],
        "difficulty": dummy["difficulty"],
        "points": dummy["points"],
        "duration": dummy["duration"],
        "start": dummy["start"],
        "end": dummy["end"],
        "group_id": None,
    })
    
    update = _gen_quiz()
    dummy.update(update)
    resp = rs.put(f"{HOST}/api/v1/user/quiz/{dummy['id']}", json=update, cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 200, pformat(resp.json()))
    asrt.assertDictEqual(resp.json(), {})

    # Check quiz details (after update)
    resp = rs.get(f"{HOST}/api/v1/user/quiz/{dummy['id']}", cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual(resp.json(), {
        "title": dummy['title'],
        "category": dummy['category'],
        "difficulty": dummy["difficulty"],
        "points": dummy["points"],
        "duration": dummy["duration"],
        "start": dummy["start"],
        "end": dummy["end"],
        "group_id": None,
    })

    # Delete quiz
    resp = rs.delete(f"{HOST}/api/v1/user/quiz/{dummy['id']}", cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 204)

def add_questions_to_quiz(asrt: ut.TestCase, user, group, quiz) -> list:
    # Add 10 questions to quiz (main)
    session_cookie = user['session']
    questions = [_gen_question() for _ in range(10)]
    resp = rs.post(f"{HOST}/api/v1/user/quiz/{quiz['id']}/question", json={"questions": questions}, cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 201, pformat(resp.json()))
    
    resp = resp.json()
    
    for i, q in enumerate(questions):
        q['id'] = resp[i]["question_id"]

    # List questions in quiz (main)
    resp = rs.get(f"{HOST}/api/v1/user/quiz/{quiz['id']}/question", cookies=session_cookie)
    
    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual(resp.json(), {
        "questions": [
            {
                "statement": q['statement'],
                "points": q['points'],
                "type": q['type'],
                "options": q['options'],
                "correct_answer": q['correct_answer'],
            } for q in questions
        ]
    })
    
    # Modify questions (3-8) in quiz (main)
    update = []
    for i in range(3, 8):
        q = _gen_question()
        q["question_id"] = questions[i]['id']
        questions[i].update(q)
        update.append(q)
    
    resp = rs.put(f"{HOST}/api/v1/user/quiz/{quiz['id']}/question", json={"questions": update}, cookies=session_cookie)

    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual(resp.json(), {})
    
    # List questions in quiz (main) (after modification)
    resp = rs.get(f"{HOST}/api/v1/user/quiz/{quiz['id']}/question", cookies=session_cookie)
    
    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual(resp.json(), {
        "questions": [
            {
                "statement": q['statement'],
                "points": q['points'],
                "type": q['type'],
                "options": q['options'],
                "correct_answer": q['correct_answer'],
            } for q in questions
        ]
    })

    # Delete questions (3-8) from quiz (main)
    resp = rs.delete(f"{HOST}/api/v1/user/quiz/{quiz['id']}/question", json=[{"question_id": q['id'] for q in questions[3:8]}], cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 200)

    # List questions in quiz (main) (after deletion)
    resp = rs.get(f"{HOST}/api/v1/user/quiz/{quiz['id']}/question", cookies=session_cookie)
    
    asrt.assertEqual(resp.status_code, 200)
    asrt.assertDictEqual(resp.json(), {
        "questions": [
            {
                "statement": q['statement'],
                "points": q['points'],
                "type": q['type'],
                "options": q['options'],
                "correct_answer": q['correct_answer'],
            } for q in (questions[:3] + questions[8:])
        ]
    })
    return questions

def attempt_quizzes(asrt: ut.TestCase, users, group, quiz, questions):
    # Logout
    session_cookie = users[0]['session']
    resp = rs.delete(url=f"{HOST}/api/v1/auth/logout", cookies=session_cookie)
    asrt.assertEqual(resp.status_code, 204)

    # Login as user (3-8)
    for i in range(3, 8):
        user = users[i]
        session_cookie = _user_login(asrt, user)
        resp = rs.delete(url=f"{HOST}/api/v1/auth/logout", cookies=session_cookie)
        asrt.assertEqual(resp.status_code, 204)
        # Attempt quiz (1) 3 times
        user["attempted_quizzes"][group["id"]] += 1
        for _ in range(3):
            total_score, attempt = _gen_attempt(questions)
            user["total_score"][group["id"]] += total_score
            resp = rs.post(f"{HOST}/api/v1/user/profile/quiz/{quiz['id']}/attempts", json=attempt, cookies=session_cookie)
            asrt.assertEqual(resp.status_code, 200)
            attempt['id'] = resp.json()['attempt_id']
            attempt['time'] = resp.json()['time']
            asrt.assertDictEqual(resp.json(), {
                "attempt_id": attempt['id'],
                "time": attempt['time'],
                "total_score": total_score,
                "correct_answers": [{"answer": q['correct_answer']} for q in questions],
            })
        
        resp = rs.post(f"{HOST}/api/v1/user/profile/quiz/{quiz['id']}/attempts", json=attempt, cookies=session_cookie)
        asrt.assertEqual(resp.status_code, 200)
        asrt.assertDictEqual(resp.json(), {})
        {"attempt_id": "int", "time": "datetime", "score": "int"}


class E2E_test(ut.TestCase):
    def test_body(self):
        self.maxDiff = None
        check_status(self)

        users = create_users(self)

        users = list(sorted(users, key=lambda u: u["user_name"]))
        user_crud(self)

        _user_login(self, users[0])

        groups = create_groups(self, users)

        group_crud(self, users[0])

        subscribe_to_groups(self, users[0], groups)

        add_users_to_group(self, groups[0], users)

        quizzes = create_quizzes(self, users[0], groups[0])
        quiz_crud(self, users[0], groups[0])
        
        questions = add_questions_to_quiz(self, users[0], groups[0], quizzes[0])

        attempt_quizzes(self, users, groups[0], quizzes[0], questions)


if __name__ == "__main__":
    ut.main()
