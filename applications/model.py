from .database import db
from zoneinfo import ZoneInfo
from sqlalchemy import DateTime
from datetime import datetime

def get_local_time():
    return datetime.now(ZoneInfo("Asia/Kolkata"))

class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable = False)
    full_name = db.Column(db.String(50), nullable = False)
    phone = db.Column(db.String)

    reservations = db.relationship('Reservation', backref='users', lazy=True, cascade='all, delete-orphan')


class ParkingLot(db.Model):
    __tablename__='parkinglots'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_name = db.Column(db.String, unique = True, nullable=False)
    location = db.Column(db.Text)
    pincode = db.Column(db.String)
    price = db.Column(db.Integer)
    max_spot = db.Column(db.Integer , nullable=False)


    parkingspots = db.relationship('ParkingSpot', backref='parkinglots', lazy=True, cascade='all, delete-orphan')

class ParkingSpot(db.Model):
    __tablename__ = 'parkingspots'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.String, default='A')

    lot_id= db.Column(db.Integer, db.ForeignKey('parkinglots.id'), nullable=False)

    reservations = db.relationship('Reservation', backref='parkingspots', lazy=True, cascade='all, delete-orphan')

    
    
class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_time = db.Column(db.DateTime(timezone=True), default=get_local_time)
    release_time = db.Column(db.DateTime(timezone=True))
    parking_cost = db.Column(db.Integer)
    vehicle_num = db.Column(db.String(20),nullable=False)

    spot_id = db.Column(db.Integer, db.ForeignKey('parkingspots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lot_id = db.Column(db.Integer , db.ForeignKey('parkinglots.id'), nullable=False)