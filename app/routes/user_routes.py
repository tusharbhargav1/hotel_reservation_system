from datetime import date
from decimal import Decimal

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort
)

from flask_login import (
    login_user,
    logout_user,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app.extensions import db

from app.models import (
    User,
    Hotel,
    Room,
    Booking,
    Bill,
    Payment
)

from app.security import user_required


user_bp = Blueprint(
    "user",
    __name__,
    url_prefix="/user"
)


# =====================================================
# HOME
# =====================================================

@user_bp.route("/")
def home():

    return render_template(
        "user/dashboard.html"
    )


# =====================================================
# USER REGISTRATION
# =====================================================

@user_bp.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        name = request.form.get(
            "name", ""
        ).strip()

        email = request.form.get(
            "email", ""
        ).strip().lower()

        phone = request.form.get(
            "phone", ""
        ).strip()

        password = request.form.get(
            "password", ""
        )

        if not name or not email or not password:

            flash(
                "Name, email and password are required.",
                "danger"
            )

            return redirect(
                url_for("user.register")
            )

        if len(password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "danger"
            )

            return redirect(
                url_for("user.register")
            )

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email is already registered.",
                "danger"
            )

            return redirect(
                url_for("user.register")
            )

        user = User(
            name=name,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(
                password
            )
        )

        try:

            db.session.add(user)
            db.session.commit()

        except Exception:

            db.session.rollback()

            flash(
                "Registration failed. Please try again.",
                "danger"
            )

            return redirect(
                url_for("user.register")
            )

        flash(
            "Registration successful. Please log in.",
            "success"
        )

        return redirect(
            url_for("user.login")
        )

    return render_template(
        "user/register.html"
    )


# =====================================================
# USER LOGIN
# =====================================================

@user_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email", ""
        ).strip().lower()

        password = request.form.get(
            "password", ""
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):

            login_user(
                user,
                remember=False
            )

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


# =====================================================
# USER DASHBOARD
# =====================================================

@user_bp.route("/dashboard")
@user_required
def dashboard():

    total_bookings = Booking.query.filter_by(
        user_id=current_user.id
    ).count()

    active_bookings = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.status.in_([
            "confirmed",
            "checked_in"
        ])
    ).count()

    return render_template(
        "user/dashboard.html",
        total_bookings=total_bookings,
        active_bookings=active_bookings
    )


# =====================================================
# USER LOGOUT
# =====================================================

@user_bp.route("/logout")
@user_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("user.login")
    )


# =====================================================
# VIEW USER HOTELS
# =====================================================

@user_bp.route("/hotels")
@user_required
def hotels():

    hotels = Hotel.query.order_by(
        Hotel.name
    ).all()

    return render_template(
        "user/hotels.html",
        hotels=hotels
    )


# =====================================================
# VIEW ROOMS
# =====================================================

@user_bp.route("/rooms")
@user_required
def available_rooms():

    rooms = Room.query.filter_by(
        status="available"
    ).order_by(
        Room.room_number
    ).all()

    return render_template(
        "user/rooms.html",
        rooms=rooms
    )


# =====================================================
# CHECK ROOM AVAILABILITY
# =====================================================

@user_bp.route(
    "/availability",
    methods=["GET", "POST"]
)
@user_required
def check_availability():

    hotels = Hotel.query.order_by(
        Hotel.name
    ).all()

    rooms = []

    selected_hotel_id = request.args.get(
        "hotel_id", ""
    )

    check_in = ""
    check_out = ""
    guests = ""

    if request.method == "POST":

        selected_hotel_id = request.form.get(
            "hotel_id", ""
        )

        check_in = request.form.get(
            "check_in", ""
        )

        check_out = request.form.get(
            "check_out", ""
        )

        guests = request.form.get(
            "guests", ""
        )

    if check_in and check_out and guests and selected_hotel_id:

        try:

            check_in_date = date.fromisoformat(
                check_in
            )

            check_out_date = date.fromisoformat(
                check_out
            )

            guest_count = int(guests)

            hotel_id = int(
                selected_hotel_id
            )

        except (ValueError, TypeError):

            flash(
                "Please enter valid search details.",
                "danger"
            )

            return render_template(
                "user/availability.html",
                hotels=hotels,
                rooms=[],
                selected_hotel_id=selected_hotel_id,
                check_in=check_in,
                check_out=check_out,
                guests=guests
            )

        if (
            check_in_date < date.today()
            or check_out_date <= check_in_date
            or guest_count < 1
        ):

            flash(
                "Please select valid dates and guest count.",
                "danger"
            )

            return render_template(
                "user/availability.html",
                hotels=hotels,
                rooms=[],
                selected_hotel_id=selected_hotel_id,
                check_in=check_in,
                check_out=check_out,
                guests=guests
            )

        hotel = db.session.get(
            Hotel,
            hotel_id
        )

        if hotel is None:

            flash(
                "Selected hotel does not exist.",
                "danger"
            )

            return redirect(
                url_for("user.check_availability")
            )

        # Find bookings that overlap the requested dates.
        overlapping_bookings = Booking.query.filter(
            Booking.status.in_([
                "confirmed",
                "checked_in"
            ]),
            Booking.check_in_date < check_out_date,
            Booking.check_out_date > check_in_date
        ).all()

        booked_room_ids = {
            booking.room_id
            for booking in overlapping_bookings
        }

        candidate_rooms = Room.query.filter(
            Room.hotel_id == hotel_id,
            Room.status == "available",
            Room.capacity >= guest_count
        ).order_by(
            Room.room_number
        ).all()

        rooms = [
            room
            for room in candidate_rooms
            if room.id not in booked_room_ids
        ]

    return render_template(
        "user/availability.html",
        hotels=hotels,
        rooms=rooms,
        selected_hotel_id=selected_hotel_id,
        check_in=check_in,
        check_out=check_out,
        guests=guests
    )


# =====================================================
# BOOK A ROOM
# =====================================================

@user_bp.route(
    "/book/<int:room_id>",
    methods=["GET", "POST"]
)
@user_required
def book_room(room_id):

    room = db.session.get(
        Room,
        room_id
    )

    if room is None:
        abort(404)

    if request.method == "POST":

        check_in = request.form.get(
            "check_in", ""
        )

        check_out = request.form.get(
            "check_out", ""
        )

        guests = request.form.get(
            "guests", ""
        )

    else:

        check_in = request.args.get(
            "check_in", ""
        )

        check_out = request.args.get(
            "check_out", ""
        )

        guests = request.args.get(
            "guests", ""
        )

    try:

        check_in_date = date.fromisoformat(
            check_in
        )

        check_out_date = date.fromisoformat(
            check_out
        )

        guest_count = int(guests)

    except (ValueError, TypeError):

        flash(
            "Invalid booking details. Please search again.",
            "danger"
        )

        return redirect(
            url_for(
                "user.check_availability",
                hotel_id=room.hotel_id
            )
        )

    if (
        check_in_date < date.today()
        or check_out_date <= check_in_date
        or guest_count < 1
        or guest_count > room.capacity
    ):

        flash(
            "Invalid dates or guest count for this room.",
            "danger"
        )

        return redirect(
            url_for(
                "user.check_availability",
                hotel_id=room.hotel_id
            )
        )

    if room.status != "available":

        flash(
            "This room is currently unavailable.",
            "danger"
        )

        return redirect(
            url_for("user.check_availability")
        )

    # Recheck overlapping bookings before confirmation.
    conflict = Booking.query.filter(
        Booking.room_id == room.id,
        Booking.status.in_([
            "confirmed",
            "checked_in"
        ]),
        Booking.check_in_date < check_out_date,
        Booking.check_out_date > check_in_date
    ).first()

    if conflict:

        flash(
            "This room has already been booked for those dates.",
            "danger"
        )

        return redirect(
            url_for(
                "user.check_availability",
                hotel_id=room.hotel_id
            )
        )

    if request.method == "GET":

        return render_template(
            "user/booking.html",
            room=room,
            check_in=check_in,
            check_out=check_out,
            guests=guest_count
        )

    booking = Booking(
        user_id=current_user.id,
        room_id=room.id,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        guests=guest_count,
        status="confirmed"
    )

    try:

        db.session.add(booking)
        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Booking failed. Please try again.",
            "danger"
        )

        return redirect(
            url_for("user.check_availability")
        )

    flash(
        "Room booked successfully.",
        "success"
    )

    return redirect(
        url_for("user.booking_history")
    )


# =====================================================
# BOOKING HISTORY
# =====================================================

@user_bp.route("/bookings")
@user_required
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


# =====================================================
# CANCEL BOOKING
# =====================================================

@user_bp.route(
    "/booking/<int:booking_id>/cancel",
    methods=["POST"]
)
@user_required
def cancel_booking(booking_id):

    booking = db.session.get(
        Booking,
        booking_id
    )

    if booking is None:
        abort(404)

    if booking.user_id != current_user.id:
        abort(403)

    if booking.status != "confirmed":

        flash(
            "Only confirmed bookings can be cancelled.",
            "danger"
        )

        return redirect(
            url_for("user.booking_history")
        )

    booking.status = "cancelled"

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Unable to cancel booking.",
            "danger"
        )

        return redirect(
            url_for("user.booking_history")
        )

    flash(
        "Booking cancelled successfully.",
        "success"
    )

    return redirect(
        url_for("user.booking_history")
    )


# =====================================================
# CUSTOMER BILL VIEW
# =====================================================

@user_bp.route(
    "/booking/<int:booking_id>/bill"
)
@user_required
def view_bill(booking_id):

    booking = db.session.get(
        Booking,
        booking_id
    )

    if booking is None:
        abort(404)

    if booking.user_id != current_user.id:
        abort(403)

    bill = Bill.query.filter_by(
        booking_id=booking.id
    ).first()

    if bill is None:

        flash(
            "Bill has not been generated yet.",
            "info"
        )

        return redirect(
            url_for("user.booking_history")
        )

    payment = Payment.query.filter_by(
        booking_id=booking.id
    ).first()

    nights = (
        booking.check_out_date
        - booking.check_in_date
    ).days

    return render_template(
        "user/bill.html",
        booking=booking,
        bill=bill,
        payment=payment,
        nights=nights
    )