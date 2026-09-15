from flask import Flask, render_template, redirect, url_for
from config import Config

from app.extensions import db, login_manager
from flask_migrate import Migrate

migrate =Migrate()


def create_app():

    app = Flask(__name__)

     # CONFIGURATION
 
    app.config.from_object(Config)

     # INITIALIZE DATABASE
 
    db.init_app(app)
    migrate.init_app(app, db)


     # INITIALIZE LOGIN MANAGER
 
    login_manager.init_app(app)



     # IMPORT MODELS
 
    from app.models import (
        User,
        Staff,
        Hotel,
        Room,
        Booking,
        Payment,
        Bill
    )

     # REGISTER BLUEPRINTS
 
    from app.routes import user_bp, staff_bp, room_bp,hotel_bp

    app.register_blueprint(user_bp)

    app.register_blueprint(staff_bp)

    app.register_blueprint(room_bp)

    app.register_blueprint(hotel_bp)
    

     # HOME ROUTE
 
    @app.route("/")
    def home():
         return redirect( url_for("user.login") ) 
    return app
 
 # FLASK LOGIN USER LOADER
 
@login_manager.user_loader
def load_user(user_id):

    if user_id.startswith("user:"):

        from app.models import User

        user_id = int(
            user_id.split(":")[1]
        )

        return db.session.get(
            User,
            user_id
        )

    if user_id.startswith("staff:"):

        from app.models import Staff

        staff_id = int(
            user_id.split(":")[1]
        )

        return db.session.get(
            Staff,
            staff_id
        )

    return None


 