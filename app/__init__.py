from flask import Flask, render_template

from config import Config

from app.extensions import (
    db,
    login_manager,
    csrf
)


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY is missing from .env"
        )

    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        raise RuntimeError(
            "DATABASE_URL is missing from .env"
        )

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)

    login_manager.init_app(app)

    csrf.init_app(app)

    # Import models
    from app.models import (
        User,
        Staff,
        Hotel,
        Room,
        Booking,
        Payment,
        Bill
    )

    # Import blueprints
    from app.routes import (
        user_bp,
        staff_bp,
        room_bp,
        hotel_bp
    )

    # Register blueprints
    app.register_blueprint(user_bp)

    app.register_blueprint(staff_bp)

    app.register_blueprint(room_bp)

    app.register_blueprint(hotel_bp)

    # Home route
    @app.route("/")
    def home():

        return render_template(
            "user/dashboard.html"
        )

    # Forbidden error
    @app.errorhandler(403)
    def forbidden(error):

        return render_template(
            "403.html"
        ), 403

    # Not found error
    @app.errorhandler(404)
    def not_found(error):

        return render_template(
            "404.html"
        ), 404

    return app


@login_manager.user_loader
def load_user(user_id):

    if not user_id:
        return None

    try:

        role, actual_id = user_id.split(":", 1)

        actual_id = int(actual_id)

    except (ValueError, AttributeError):
        return None

    if role == "user":

        from app.models import User

        return db.session.get(
            User,
            actual_id
        )

    if role == "staff":

        from app.models import Staff

        return db.session.get(
            Staff,
            actual_id
        )

    return None