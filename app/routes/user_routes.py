from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from datetime import date

from app.extensions import db

from app.models import (
    User,
    Hotel,
    Room,
    Booking
)


 # USER BLUEPRINT
 
user_bp = Blueprint(
    "user",
    __name__,
    url_prefix="/user"
)


 # USER HOME
 
@user_bp.route("/")
def home():

    return render_template(
        "user/dashboard.html"
    )


 # USER REGISTER
 
@user_bp.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")

         # BASIC VALIDATION
 
        if not name or not email or not password:

            flash(
                "Name, email and password are required.",
                "danger"
            )

            return redirect(
                url_for("user.register")
            )

         # CHECK EXISTING USER
 
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email already registered.",
                "danger"
            )

            return redirect(
                url_for("user.register")
            )

         # CREATE USER
 
        user = User(

            name=name,

            email=email,

            phone=phone,

            password_hash=generate_password_hash(
                password
            )

        )

        db.session.add(user)

        db.session.commit()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(
            url_for("user.login")
        )

    return render_template(
        "user/register.html"
    )


 # USER LOGIN
 
@user_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get("email")

        password = request.form.get("password")

         # FIND USER
 
        user = User.query.filter_by(
            email=email
        ).first()

         # CHECK PASSWORD
 
        if user and check_password_hash(
            user.password_hash,
            password
        ):

            login_user(user)

            flash(
                "Login successful.",
                "success"
            )

            return redirect(
                url_for("user.dashboard")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "user/login.html"
    )


 # USER DASHBOARD
 
@user_bp.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "user/dashboard.html"
    )


 # SHOW ALL HOTELS
 
@user_bp.route("/hotels")
@login_required
def hotels():

    hotels = Hotel.query.order_by(
        Hotel.name
    ).all()

    return render_template(
        "user/hotels.html",
        hotels=hotels
    )


 # HOTEL DETAILS
 
@user_bp.route(
    "/hotels/<int:hotel_id>"
)
@login_required
def hotel_details(hotel_id):

    hotel = db.session.get(
        Hotel,
        hotel_id
    )

    if hotel is None:

        flash(
            "Hotel not found.",
            "danger"
        )

        return redirect(
            url_for("user.hotels")
        )

    return render_template(
        "user/hotels.html",
        hotels=[hotel]
    )


 # VIEW ALL AVAILABLE ROOMS
 
@user_bp.route("/rooms")
@login_required
def available_rooms():

    rooms = Room.query.filter_by(
        status="available"
    ).order_by(
        Room.hotel_id,
        Room.room_number
    ).all()

    return render_template(
        "user/rooms.html",
        rooms=rooms
    )


 # CHECK ROOM AVAILABILITY
 
@user_bp.route(
    "/availability",
    methods=["GET", "POST"]
)
@login_required
def check_availability():

     # GET ALL HOTELS
 
    hotels = Hotel.query.order_by(
        Hotel.name
    ).all()

     # DEFAULT VALUES
 
    available_rooms = []

    check_in = None

    check_out = None

    guests = None

    hotel_id = None

     # GET HOTEL ID
 
    if request.method == "GET":

        hotel_id = request.args.get(
            "hotel_id"
        )

     # POST REQUEST
 
    if request.method == "POST":

        hotel_id = request.form.get(
            "hotel_id"
        )

        check_in_string = request.form.get(
            "check_in"
        )

        check_out_string = request.form.get(
            "check_out"
        )

        guests_string = request.form.get(
            "guests"
        )

         # CHECK HOTEL
 
        if not hotel_id:

            flash(
                "Please select a hotel.",
                "danger"
            )

            return render_template(
                "user/availability.html",
                rooms=[],
                hotels=hotels,
                selected_hotel_id=None,
                check_in=None,
                check_out=None,
                guests=None
            )

        hotel = db.session.get(
            Hotel,
            int(hotel_id)
        )

        if hotel is None:

            flash(
                "Selected hotel does not exist.",
                "danger"
            )

            return render_template(
                "user/availability.html",
                rooms=[],
                hotels=hotels,
                selected_hotel_id=None,
                check_in=None,
                check_out=None,
                guests=None
            )

         # CONVERT DATES
 
        try:

            check_in = date.fromisoformat(
                check_in_string
            )

            check_out = date.fromisoformat(
                check_out_string
            )

        except (ValueError, TypeError):

            flash(
                "Please enter valid dates.",
                "danger"
            )

            return render_template(
                "user/availability.html",
                rooms=[],
                hotels=hotels,
                selected_hotel_id=hotel_id,
                check_in=None,
                check_out=None,
                guests=None
            )

         # CONVERT GUESTS
 
        try:

            guests = int(
                guests_string
            )

        except (ValueError, TypeError):

            flash(
                "Please enter a valid number of guests.",
                "danger"
            )

            return render_template(
                "user/availability.html",
                rooms=[],
                hotels=hotels,
                selected_hotel_id=hotel_id,
                check_in=check_in,
                check_out=check_out,
                guests=None
            )

         # GUEST VALIDATION
 
        if guests < 1:

            flash(
                "Number of guests must be at least 1.",
                "danger"
            )

            return render_template(
                "user/availability.html",
                rooms=[],
                hotels=hotels,
                selected_hotel_id=hotel_id,
                check_in=check_in,
                check_out=check_out,
                guests=guests
            )

         # CHECK-IN DATE VALIDATION
 
        if check_in < date.today():

            flash(
                "Check-in date cannot be in the past.",
                "danger"
            )

            return render_template(
                "user/availability.html",
                rooms=[],
                hotels=hotels,
                selected_hotel_id=hotel_id,
                check_in=check_in,
                check_out=check_out,
                guests=guests
            )

         # CHECK-OUT DATE VALIDATION
 
        if check_out <= check_in:

            flash(
                "Check-out date must be after check-in date.",
                "danger"
            )

            return render_template(
                "user/availability.html",
                rooms=[],
                hotels=hotels,
                selected_hotel_id=hotel_id,
                check_in=check_in,
                check_out=check_out,
                guests=guests
            )

         # FIND OVERLAPPING BOOKINGS
 
        overlapping_bookings = Booking.query.filter(

            Booking.status.in_([
                "confirmed",
                "checked_in"
            ]),

            Booking.check_in_date < check_out,

            Booking.check_out_date > check_in

        ).all()

         # GET BOOKED ROOM IDS
 
        booked_room_ids = {

            booking.room_id

            for booking in overlapping_bookings

        }

         # FIND AVAILABLE ROOMS
 
        available_rooms = Room.query.filter(

            Room.hotel_id == int(hotel_id),

            Room.status == "available",

            Room.capacity >= guests

        ).order_by(
            Room.room_number
        ).all()

         # REMOVE ROOMS WITH BOOKINGS
 
        available_rooms = [

            room

            for room in available_rooms

            if room.id not in booked_room_ids

        ]

     # RENDER PAGE
 
    return render_template(

        "user/availability.html",

        rooms=available_rooms,

        hotels=hotels,

        selected_hotel_id=hotel_id,

        check_in=check_in,

        check_out=check_out,

        guests=guests

    )


 # BOOK ROOM
 
@user_bp.route(
    "/book/<int:room_id>",
    methods=["GET", "POST"]
)
@login_required
def book_room(room_id):

     # FIND ROOM
 
    room = db.session.get(
        Room,
        room_id
    )

    if room is None:

        flash(
            "Room not found.",
            "danger"
        )

        return redirect(
            url_for("user.check_availability")
        )

     # GET REQUEST
 
    if request.method == "GET":

        check_in_string = request.args.get(
            "check_in"
        )

        check_out_string = request.args.get(
            "check_out"
        )

        guests_string = request.args.get(
            "guests"
        )

        hotel_id = request.args.get(
            "hotel_id"
        )

         # CHECK REQUIRED DATA
 
        if not check_in_string or not check_out_string:

            flash(
                "Please select booking dates first.",
                "danger"
            )

            return redirect(
                url_for("user.check_availability")
            )

         # CONVERT DATA
 
        try:

            check_in = date.fromisoformat(
                check_in_string
            )

            check_out = date.fromisoformat(
                check_out_string
            )

            guests = int(
                guests_string
            )

        except (ValueError, TypeError):

            flash(
                "Invalid booking information.",
                "danger"
            )

            return redirect(
                url_for("user.check_availability")
            )

         # VALIDATION
 
        if check_in < date.today():

            flash(
                "Check-in date cannot be in the past.",
                "danger"
            )

            return redirect(
                url_for("user.check_availability")
            )

        if check_out <= check_in:

            flash(
                "Check-out date must be after check-in date.",
                "danger"
            )

            return redirect(
                url_for("user.check_availability")
            )

        if guests < 1:

            flash(
                "Number of guests must be at least 1.",
                "danger"
            )

            return redirect(
                url_for("user.check_availability")
            )

         # CHECK ROOM CAPACITY
 
        if guests > room.capacity:

            flash(
                "This room cannot accommodate that many guests.",
                "danger"
            )

            return redirect(
                url_for("user.check_availability")
            )

         # CHECK ROOM STATUS
 
        if room.status != "available":

            flash(
                "This room is currently unavailable.",
                "danger"
            )

            return redirect(
                url_for("user.check_availability")
            )

         # CHECK HOTEL
 
        if hotel_id:

            if int(hotel_id) != room.hotel_id:

                flash(
                    "Invalid hotel and room combination.",
                    "danger"
                )

                return redirect(
                    url_for("user.hotels")
                )

         # CHECK OVERLAPPING BOOKING
 
        overlapping_booking = Booking.query.filter(

            Booking.room_id == room.id,

            Booking.status.in_([
                "confirmed",
                "checked_in"
            ]),

            Booking.check_in_date < check_out,

            Booking.check_out_date > check_in

        ).first()

        if overlapping_booking:

            flash(
                "Sorry, this room is no longer available.",
                "danger"
            )

            return redirect(
                url_for(
                    "user.check_availability",
                    hotel_id=room.hotel_id
                )
            )

         # SHOW CONFIRMATION PAGE
 
        return render_template(

            "user/booking.html",

            room=room,

            check_in=check_in,

            check_out=check_out,

            guests=guests

        )

     # POST REQUEST
 
    check_in_string = request.form.get(
        "check_in"
    )

    check_out_string = request.form.get(
        "check_out"
    )

    guests_string = request.form.get(
        "guests"
    )

     # CONVERT DATA
 
    try:

        check_in = date.fromisoformat(
            check_in_string
        )

        check_out = date.fromisoformat(
            check_out_string
        )

        guests = int(
            guests_string
        )

    except (ValueError, TypeError):

        flash(
            "Invalid booking information.",
            "danger"
        )

        return redirect(
            url_for("user.check_availability")
        )

     # VALIDATION
 
    if check_in < date.today():

        flash(
            "Check-in date cannot be in the past.",
            "danger"
        )

        return redirect(
            url_for("user.check_availability")
        )

    if check_out <= check_in:

        flash(
            "Check-out date must be after check-in date.",
            "danger"
        )

        return redirect(
            url_for("user.check_availability")
        )

    if guests < 1:

        flash(
            "Number of guests must be at least 1.",
            "danger"
        )

        return redirect(
            url_for("user.check_availability")
        )

     # CHECK CAPACITY
 
    if guests > room.capacity:

        flash(
            "Room capacity exceeded.",
            "danger"
        )

        return redirect(
            url_for("user.check_availability")
        )

     # CHECK ROOM STATUS
 
    if room.status != "available":

        flash(
            "Room is currently unavailable.",
            "danger"
        )

        return redirect(
            url_for(
                "user.check_availability",
                hotel_id=room.hotel_id
            )
        )

     # FINAL DOUBLE-BOOKING CHECK
 
    overlapping_booking = Booking.query.filter(

        Booking.room_id == room.id,

        Booking.status.in_([
            "confirmed",
            "checked_in"
        ]),

        Booking.check_in_date < check_out,

        Booking.check_out_date > check_in

    ).first()

    if overlapping_booking:

        flash(
            "Sorry, this room has already been booked.",
            "danger"
        )

        return redirect(
            url_for(
                "user.check_availability",
                hotel_id=room.hotel_id
            )
        )

     # CREATE BOOKING
 
    booking = Booking(

        user_id=current_user.id,

        room_id=room.id,

        check_in_date=check_in,

        check_out_date=check_out,

        guests=guests,

        status="confirmed"

    )

    db.session.add(
        booking
    )

    db.session.commit()

    flash(
        "Room booked successfully!",
        "success"
    )

    return redirect(
        url_for("user.booking_history")
    )


 # BOOKING HISTORY
 
@user_bp.route("/bookings")
@login_required
def booking_history():

    bookings = Booking.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Booking.created_at.desc()

    ).all()

    return render_template(

        "user/bookings.html",

        bookings=bookings

    )


 # CANCEL BOOKING
 
@user_bp.route(
    "/booking/<int:booking_id>/cancel",
    methods=["POST"]
)
@login_required
def cancel_booking(booking_id):

     # FIND USER'S BOOKING
 
    booking = Booking.query.filter_by(

        id=booking_id,

        user_id=current_user.id

    ).first()

    if booking is None:

        flash(
            "Booking not found.",
            "danger"
        )

        return redirect(
            url_for("user.booking_history")
        )

     # CHECK BOOKING STATUS
 
    if booking.status != "confirmed":

        flash(
            "Only confirmed bookings can be cancelled.",
            "danger"
        )

        return redirect(
            url_for("user.booking_history")
        )

     # CANCEL BOOKING
 
    booking.status = "cancelled"

    db.session.commit()

    flash(
        "Booking cancelled successfully.",
        "success"
    )

    return redirect(
        url_for("user.booking_history")
    )


 # USER LOGOUT
 
@user_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash( "You have been logged out.","success")

    return redirect(url_for("user.login"))