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

from app.extensions import db

from app.models import (
    Room,
    Hotel
)

from app.security import staff_required


room_bp = Blueprint(
    "room",
    __name__,
    url_prefix="/rooms"
)


# =====================================================
# VIEW ALL ROOMS
# =====================================================

@room_bp.route("/")
@staff_required
def rooms():

    all_rooms = Room.query.order_by(
        Room.hotel_id,
        Room.room_number
    ).all()

    return render_template(
        "staff/rooms.html",
        rooms=all_rooms
    )


# =====================================================
# ADD ROOM
# =====================================================

@room_bp.route(
    "/add",
    methods=["GET", "POST"]
)
@staff_required
def add_room():

    hotels = Hotel.query.order_by(
        Hotel.name
    ).all()

    if request.method == "POST":

        hotel_id = request.form.get(
            "hotel_id", ""
        )

        room_number = request.form.get(
            "room_number", ""
        ).strip()

        room_type = request.form.get(
            "room_type", ""
        ).strip()

        price = request.form.get(
            "price_per_night", ""
        )

        capacity = request.form.get(
            "capacity", ""
        )

        try:

            hotel_id = int(hotel_id)

            capacity = int(capacity)

            price = Decimal(price)

        except (ValueError, TypeError, InvalidOperation):

            flash(
                "Please enter valid room details.",
                "danger"
            )

            return redirect(
                url_for("room.add_room")
            )

        if (
            not room_number
            or not room_type
            or capacity < 1
            or price <= 0
        ):

            flash(
                "Room number, type, capacity and positive price are required.",
                "danger"
            )

            return redirect(
                url_for("room.add_room")
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
                url_for("room.add_room")
            )

        existing_room = Room.query.filter_by(
            hotel_id=hotel_id,
            room_number=room_number
        ).first()

        if existing_room:

            flash(
                "That room number already exists in this hotel.",
                "danger"
            )

            return redirect(
                url_for("room.add_room")
            )

        room = Room(
            hotel_id=hotel_id,
            room_number=room_number,
            room_type=room_type,
            price_per_night=price,
            capacity=capacity,
            status="available"
        )

        try:

            db.session.add(room)
            db.session.commit()

        except Exception:

            db.session.rollback()

            flash(
                "Unable to add room.",
                "danger"
            )

            return redirect(
                url_for("room.add_room")
            )

        flash(
            "Room added successfully.",
            "success"
        )

        return redirect(
            url_for("room.rooms")
        )

    return render_template(
        "staff/add_room.html",
        hotels=hotels
    )


# =====================================================
# ROOM DETAILS
# =====================================================

@room_bp.route("/<int:room_id>")
@staff_required
def room_details(room_id):

    room = db.session.get(
        Room,
        room_id
    )

    if room is None:
        abort(404)

    return render_template(
        "staff/rooms.html",
        rooms=[room]
    )


# =====================================================
# UPDATE ROOM STATUS
# =====================================================

@room_bp.route(
    "/<int:room_id>/status",
    methods=["POST"]
)
@staff_required
def update_status(room_id):

    room = db.session.get(
        Room,
        room_id
    )

    if room is None:
        abort(404)

    status = request.form.get(
        "status", ""
    ).strip().lower()

    allowed_statuses = [
        "available",
        "occupied",
        "maintenance"
    ]

    if status not in allowed_statuses:

        flash(
            "Invalid room status.",
            "danger"
        )

        return redirect(
            url_for("room.rooms")
        )

    # Do not manually mark a room available
    # while a guest is checked in.
    active_booking = None

    if status == "available":

        active_booking = next(
            (
                booking
                for booking in room.bookings
                if booking.status == "checked_in"
            ),
            None
        )

    if active_booking:

        flash(
            "Cannot mark a room available while a guest is checked in.",
            "danger"
        )

        return redirect(
            url_for("room.rooms")
        )

    room.status = status

    try:

        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Unable to update room status.",
            "danger"
        )

        return redirect(
            url_for("room.rooms")
        )

    flash(
        f"Room {room.room_number} status updated.",
        "success"
    )

    return redirect(
        url_for("room.rooms")
    )


# =====================================================
# DELETE ROOM
# =====================================================

@room_bp.route(
    "/<int:room_id>/delete",
    methods=["POST"]
)
@staff_required
def delete_room(room_id):

    room = db.session.get(
        Room,
        room_id
    )

    if room is None:
        abort(404)

    # Preserve booking history.
    if room.bookings:

        flash(
            "Cannot delete a room with existing booking records.",
            "danger"
        )

        return redirect(
            url_for("room.rooms")
        )

    try:

        db.session.delete(room)
        db.session.commit()

    except Exception:

        db.session.rollback()

        flash(
            "Unable to delete room.",
            "danger"
        )

        return redirect(
            url_for("room.rooms")
        )

    flash(
        "Room deleted successfully.",
        "success"
    )

    return redirect(
        url_for("room.rooms")
    )