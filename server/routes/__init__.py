import logging
from models.user import User


LOGGER = logging.getLogger(__name__)


def fetch_user(userId: str) -> User:
    user = User(userId=userId)
    if not user:
        raise Exception("No such user exists")
    return user
