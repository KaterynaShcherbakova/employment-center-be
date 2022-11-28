from schemas import auth
from alembic_m.db import db_session
from resp_error import errs, json_error
from alembic_m.models import PersonModel
from bcrypt import checkpw


@auth.verify_password
def verify_password(username, password):
    user = db_session.query(PersonModel).filter(PersonModel.username == username).first()
    return user and checkpw(bytes(password, 'utf-8'), bytes(user.password, 'utf-8'))


def get_current_user() -> PersonModel:
    username = auth.current_user()
    return db_session.query(PersonModel).filter(PersonModel.username == username).first()


@auth.get_user_roles
def get_user_roles(user):
    user = db_session.query(PersonModel).filter(PersonModel.username == user.get('username', None)).first()
    return user.role


@auth.error_handler
def auth_error(status):
    if status == 401:
        return errs.no_auth
    elif status == 403:
        return errs.no_access
