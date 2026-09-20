from functools import wraps

from flask import abort
from flask_login import current_user, login_required


def user_required(view_function):

    @wraps(view_function)
    @login_required
    def decorated_function(*args, **kwargs):

        user_id = current_user.get_id()

        if (
            not user_id
            or not user_id.startswith("user:")
        ):
            abort(403)

        return view_function(*args, **kwargs)

    return decorated_function


def staff_required(view_function):

    @wraps(view_function)
    @login_required
    def decorated_function(*args, **kwargs):

        user_id = current_user.get_id()

        if (
            not user_id
            or not user_id.startswith("staff:")
        ):
            abort(403)

        return view_function(*args, **kwargs)

    return decorated_function