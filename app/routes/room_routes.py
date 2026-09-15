from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required

from app.extensions import db

from app.models import (
    Room,
    Hotel
)


room_bp = Blueprint(
    "room",
    __name__,
    url_prefix="/rooms"
)


 # VIEW ALL ROOMS
 
@room_bp.route("/")
@login_required
def rooms():

    all_rooms = Room.query.order_by(
        Room.hotel_id,
        Room.room_number
    ).all()

    return render_template(
        "staff/rooms.html",
        rooms=all_rooms
    )


 # ADD NEW ROOM
 
@room_bp.route(
    "/add",
    methods=["GET", "POST"]
)
@login_required
def add_room():

    hotels = Hotel.query.order_by(
        Hotel.name
    ).all()

    if request.method == "POST":

        hotel_id = request.form.get(
            "hotel_id"
        )

        room_number = request.form.get(
            "room_number"
        )

        room_type = request.form.get(
            "room_type"
        )

        price_per_night = request.form.get(
            "price_per_night"
        )

        capacity = request.form.get(
            "capacity"
        )

        hotel = db.session.get(
            Hotel,
            hotel_id
        )

        if hotel is None:

            flash(
                "Invalid hotel selected.",
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
                "This room number already exists in this hotel.",
                "danger"
            )

            return redirect(
                url_for("room.add_room")
            )

        room = Room(

            hotel_id=hotel_id,

            room_number=room_number,

            room_type=room_type,

            price_per_night=price_per_night,

            capacity=capacity,

            status="available"

        )

        db.session.add(room)

        db.session.commit()

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


 # VIEW SINGLE ROOM
 
@room_bp.route("/<int:room_id>")
@login_required
def room_details(room_id):

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
            url_for("room.rooms")
        )

    return render_template(
        "staff/rooms.html",
        rooms=[room]
    )


 # UPDATE ROOM STATUS
 
@room_bp.route(
    "/<int:room_id>/status",
    methods=["POST"]
)
@login_required
def update_status(room_id):

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
            url_for("room.rooms")
        )

    status = request.form.get(
        "status"
    )

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

    room.status = status

    db.session.commit()

    flash(
        f"Room {room.room_number} status updated.",
        "success"
    )

    return redirect(
        url_for("room.rooms")
    )


 # DELETE ROOM
 
@room_bp.route(
    "/<int:room_id>/delete",
    methods=["POST"]
)
@login_required
def delete_room(room_id):

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
            url_for("room.rooms")
        )

    if room.bookings:

        flash(
            "Cannot delete a room with existing bookings.",
            "danger"
        )

        return redirect(
            url_for("room.rooms")
        )

    db.session.delete(room)

    db.session.commit()

    flash(
        f"Room {room.room_number} deleted successfully.",
        "success"
    )

    return redirect(
        url_for("room.rooms")
    )