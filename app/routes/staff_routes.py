from datetime import datetime
from decimal import Decimal, InvalidOperation

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

from werkzeug.security import check_password_hash

from app.extensions import db

from app.models import (
    Staff,
    Booking,
    Room,
    Bill,
    Payment
)

from app.security import staff_required


staff_bp = Blueprint(
    "staff",
    __name__,
    url_prefix="/staff"
)


# =====================================================
# STAFF LOGIN
# =====================================================

@staff_bp.route(
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

        staff = Staff.query.filter_by(
            email=email
        ).first()

        if staff and check_password_hash(
            staff.password_hash,
            password
        ):

            login_user(
                staff,
                remember=False
            )

            flash(
                "Staff login successful.",
                "success"
            )

            return redirect(
                url_for("staff.dashboard")
            )

        flash(
            "Invalid staff email or password.",
            "danger"
        )

    return render_template(
        "staff/login.html"
    )


# =====================================================
# STAFF DASHBOARD
# =====================================================

@staff_bp.route("/dashboard")
@staff_required
def dashboard():

    total_bookings = Booking.query.count()

    confirmed_bookings = Booking.query.filter_by(
        status="confirmed"
    ).count()

    checked_in = Booking.query.filter_by(
        status="checked_in"
    ).count()

    checked_out = Booking.query.filter_by(
        status="checked_out"
    ).count()

    available_rooms = Room.query.filter_by(
        status="available"
    ).count()

    occupied_rooms = Room.query.filter_by(
        status="occupied"
    ).count()

    maintenance_rooms = Room.query.filter_by(
        status="maintenance"
    ).count()

    return render_template(
        "staff/dashboard.html",
        total_bookings=total_bookings,
        confirmed_bookings=confirmed_bookings,
        checked_in=checked_in,
        checked_out=checked_out,
        available_rooms=available_rooms,
        occupied_rooms=occupied_rooms,
        maintenance_rooms=maintenance_rooms
    )


# =====================================================
# VIEW ALL BOOKINGS
# =====================================================

@staff_bp.route("/bookings")
@staff_required
def bookings():

    bookings = Booking.query.order_by(
        Booking.created_at.desc()
    ).all()

    return render_template(
        "staff/bookings.html",
        bookings=bookings
    )


# =====================================================
# STAFF CHECK-IN
# =====================================================

@staff_bp.route(
    "/checkin",
    methods=["GET", "POST"]
)
@staff_required
def checkin():

    if request.method == "POST":

        booking_id = request.form.get(
            "booking_id", ""
        )

        try:

            booking_id = int(booking_id)

        except (ValueError, TypeError):

            flash(
                "Invalid booking ID.",
                "danger"
            )

            return redirect(
                url_for("staff.checkin")
            )

        booking = db.session.get(
            Booking,
            booking_id
        )

        if booking is None:
            abort(404)

        if booking.status != "confirmed":

            flash(
                "Only confirmed bookings can be checked in.",
                "danger"
            )

            return redirect(
                url_for("staff.checkin")
            )

        room = booking.room

        if room is None:
            abort(404)

        if room.status != "available":

            flash(
                "This room is not currently available.",
                "danger"
            )

            return redirect(
                url_for("staff.checkin")
            )

        # Check for another active booking in this room.
        conflict = Booking.query.filter(
            Booking.room_id == room.id,
            Booking.id != booking.id,
            Booking.status == "checked_in"
        ).first()

        if conflict:

            flash(
                "Room already has a checked-in guest.",
                "danger"
            )

            return redirect(
                url_for("staff.checkin")
            )

        booking.status = "checked_in"

        room.status = "occupied"

        try:

            db.session.commit()

        except Exception:

            db.session.rollback()

            flash(
                "Check-in failed. Please try again.",
                "danger"
            )

            return redirect(
                url_for("staff.checkin")
            )

        flash(
            f"Guest checked in to room {room.room_number}.",
            "success"
        )

        return redirect(
            url_for("staff.bookings")
        )

    confirmed_bookings = Booking.query.filter_by(
        status="confirmed"
    ).order_by(
        Booking.check_in_date
    ).all()

    return render_template(
        "staff/checkin.html",
        bookings=confirmed_bookings
    )


# =====================================================
# STAFF CHECK-OUT
# =====================================================

@staff_bp.route(
    "/checkout",
    methods=["GET", "POST"]
)
@staff_required
def checkout():

    if request.method == "POST":

        booking_id = request.form.get(
            "booking_id", ""
        )

        try:

            booking_id = int(booking_id)

        except (ValueError, TypeError):

            flash(
                "Invalid booking ID.",
                "danger"
            )

            return redirect(
                url_for("staff.checkout")
            )

        booking = db.session.get(
            Booking,
            booking_id
        )

        if booking is None:
            abort(404)

        if booking.status != "checked_in":

            flash(
                "Only checked-in bookings can be checked out.",
                "danger"
            )

            return redirect(
                url_for("staff.checkout")
            )

        room = booking.room

        if room is None:
            abort(404)

        nights = (
            booking.check_out_date
            - booking.check_in_date
        ).days

        if nights <= 0:

            flash(
                "Invalid booking dates.",
                "danger"
            )

            return redirect(
                url_for("staff.checkout")
            )

        # Calculate bill amounts using Decimal.
        room_charges = (
            Decimal(str(room.price_per_night))
            * Decimal(nights)
        )

        tax_rate = Decimal("0.18")

        tax = (
            room_charges * tax_rate
        ).quantize(
            Decimal("0.01")
        )

        discount = Decimal("0.00")

        total_amount = (
            room_charges + tax - discount
        ).quantize(
            Decimal("0.01")
        )

        existing_bill = Bill.query.filter_by(
            booking_id=booking.id
        ).first()

        existing_payment = Payment.query.filter_by(
            booking_id=booking.id
        ).first()

        try:

            if existing_bill is None:

                bill = Bill(
                    booking_id=booking.id,
                    room_charges=room_charges,
                    tax=tax,
                    discount=discount,
                    total_amount=total_amount
                )

                db.session.add(bill)

            if existing_payment is None:

                payment = Payment(
                    booking_id=booking.id,
                    amount=total_amount,
                    payment_method="pending",
                    payment_status="pending"
                )

                db.session.add(payment)

            booking.status = "checked_out"

            room.status = "available"

            db.session.commit()

        except Exception:

            db.session.rollback()

            flash(
                "Checkout failed. Please try again.",
                "danger"
            )

            return redirect(
                url_for("staff.checkout")
            )

        flash(
            "Guest checked out and bill generated.",
            "success"
        )

        return redirect(
            url_for(
                "staff.view_bill",
                booking_id=booking.id
            )
        )

    checked_in_bookings = Booking.query.filter_by(
        status="checked_in"
    ).order_by(
        Booking.check_out_date
    ).all()

    return render_template(
        "staff/checkout.html",
        bookings=checked_in_bookings
    )


# =====================================================
# STAFF VIEW BILL
# =====================================================

@staff_bp.route(
    "/bill/<int:booking_id>"
)
@staff_required
def view_bill(booking_id):

    booking = db.session.get(
        Booking,
        booking_id
    )

    if booking is None:
        abort(404)

    bill = Bill.query.filter_by(
        booking_id=booking.id
    ).first()

    payment = Payment.query.filter_by(
        booking_id=booking.id
    ).first()

    if bill is None:

        flash(
            "Bill has not been generated yet.",
            "info"
        )

        return redirect(
            url_for("staff.bookings")
        )

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


# =====================================================
# PROCESS PAYMENT
# =====================================================

@staff_bp.route(
    "/payment/<int:booking_id>",
    methods=["POST"]
)
@staff_required
def process_payment(booking_id):

    booking = db.session.get(
        Booking,
        booking_id
    )

    if booking is None:
        abort(404)

    bill = Bill.query.filter_by(
        booking_id=booking.id
    ).first()

    if bill is None:

        flash(
            "Bill not found.",
            "danger"
        )

        return redirect(
            url_for("staff.bookings")
        )

    payment = Payment.query.filter_by(
        booking_id=booking.id
    ).first()

    if payment is None:

        payment = Payment(
            booking_id=booking.id,
            amount=bill.total_amount,
            payment_method="pending",
            payment_status="pending"
        )

        db.session.add(payment)

    if payment.payment_status == "paid":

        flash(
            "Payment has already been completed.",
            "info"
        )

        return redirect(
            url_for(
                "staff.view_bill",
                booking_id=booking.id
            )
        )

    payment_method = request.form.get(
        "payment_method", ""
    ).strip().lower()

    allowed_methods = [
        "cash",
        "card",
        "upi"
    ]

    if payment_method not in allowed_methods:

        flash(
            "Invalid payment method.",
            "danger"
        )

        return redirect(
            url_for(
                "staff.view_bill",
                booking_id=booking.id
            )
        )

    # This records payment in the project database.
    # It does not contact a real payment gateway.
    payment.amount = bill.total_amount

    payment.payment_method = payment_method

    payment.payment_status = "paid"

    payment.transaction_id = (
        f"TXN-{booking.id}-"
        f"{int(datetime.now().timestamp())}"
    )

    payment.paid_at = datetime.now()

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Payment recording failed.",
            "danger"
        )

        return redirect(
            url_for(
                "staff.view_bill",
                booking_id=booking.id
            )
        )

    flash(
        "Payment recorded successfully.",
        "success"
    )

    return redirect(
        url_for(
            "staff.view_bill",
            booking_id=booking.id
        )
    )


# =====================================================
# STAFF LOGOUT
# =====================================================

@staff_bp.route("/logout")
@staff_required
def logout():

    logout_user()

    flash(
        "Staff logged out successfully.",
        "success"
    )

    return redirect(
        url_for("staff.login")
    )