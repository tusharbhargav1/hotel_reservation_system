from flask_login import UserMixin
from app.extensions import db

 # USER MODEL
 
class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(20)
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    bookings = db.relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def get_id(self):
        return f"user:{self.id}"


 # STAFF MODEL
 
class Staff(UserMixin, db.Model):

    __tablename__ = "staff"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(50),
        default="staff",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    def get_id(self):
        return f"staff:{self.id}"

    


 # HOTEL MODEL
 
class Hotel(db.Model):

    __tablename__ = "hotels"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    city = db.Column(
        db.String(100),
        nullable=False
    )

    address = db.Column(
        db.String(255),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    rooms = db.relationship(
        "Room",
        back_populates="hotel",
        cascade="all, delete-orphan"
    )


 # ROOM MODEL
 
class Room(db.Model):

    __tablename__ = "rooms"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    hotel_id = db.Column(
        db.Integer,
        db.ForeignKey("hotels.id"),
        nullable=False
    )

    room_number = db.Column(
        db.String(20),
        nullable=False
    )

    room_type = db.Column(
        db.String(50),
        nullable=False
    )

    price_per_night = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    capacity = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="available",
        nullable=False
    )

    hotel = db.relationship(
        "Hotel",
        back_populates="rooms"
    )

    bookings = db.relationship(
        "Booking",
        back_populates="room"
    )


 # BOOKING MODEL
 
class Booking(db.Model):

    __tablename__ = "bookings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    room_id = db.Column(
        db.Integer,
        db.ForeignKey("rooms.id"),
        nullable=False
    )

    check_in_date = db.Column(
        db.Date,
        nullable=False
    )

    check_out_date = db.Column(
        db.Date,
        nullable=False
    )

    guests = db.Column(
        db.Integer,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="confirmed",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    user = db.relationship(
        "User",
        back_populates="bookings"
    )

    room = db.relationship(
        "Room",
        back_populates="bookings"
    )

    payment = db.relationship(
        "Payment",
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan"
    )

    bill = db.relationship(
        "Bill",
        back_populates="booking",
        uselist=False,
        cascade="all, delete-orphan"
    )


 # PAYMENT MODEL
 
class Payment(db.Model):

    __tablename__ = "payments"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id"),
        unique=True,
        nullable=False
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    payment_method = db.Column(
        db.String(30),
        nullable=False
    )

    payment_status = db.Column(
        db.String(30),
        default="pending",
        nullable=False
    )

    transaction_id = db.Column(
        db.String(100),
        unique=True
    )

    paid_at = db.Column(
        db.DateTime
    )

    booking = db.relationship(
        "Booking",
        back_populates="payment"
    )


 # BILL MODEL
 
class Bill(db.Model):

    __tablename__ = "bills"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    booking_id = db.Column(
        db.Integer,
        db.ForeignKey("bookings.id"),
        unique=True,
        nullable=False
    )

    room_charges = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    tax = db.Column(
        db.Numeric(10, 2),
        default=0
    )

    discount = db.Column(
        db.Numeric(10, 2),
        default=0
    )

    total_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    generated_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    booking = db.relationship(
        "Booking",
        back_populates="bill"
    )