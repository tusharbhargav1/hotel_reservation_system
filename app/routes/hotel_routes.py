from flask import (
    Blueprint,
    render_template
)

from flask_login import login_required

from app.models import Hotel

hotel_bp = Blueprint(
    "hotel",
    __name__,
    url_prefix="/hotels"
)

# SHOW ALL HOTELS

@hotel_bp.route("/")
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

@hotel_bp.route("/<int:hotel_id>")
@login_required
def hotel_details(hotel_id):

    hotel = Hotel.query.get_or_404(
        hotel_id
    )

    return render_template(
        "user/hotels.html",
        hotels=[hotel]
    )