from models.engine.relational_storage import RelationalStorage

storage = RelationalStorage()

storage.reload()

if __name__ == '__main__':
    from models.user import User
    from models.group import Group
    from models.quiz import Quiz
    from models.user_session import UserSession
    from models.question import Question
    from models.answer import Answer
    from models.quiz_attempt import QuizAttempt
    from models.user_answer import UserAnswer
    from faker import Faker
    
    f = Faker()

    storage.new(User())
