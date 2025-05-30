
from flask import Flask, render_template,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
import os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'J12345'  # SECURING SESSION DATA
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # AVOID UNNECESSARY
    app.config['CHART_FOLDER'] = os.path.join('static', 'charts')
    os.makedirs(app.config['CHART_FOLDER'], exist_ok=True)
    app.config['passwd_hash'] = 'J12345'
    db.init_app(app)
    return app

db = SQLAlchemy()  # CREATING DB INSTANCE

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    psswd = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    
    bookings = db.relationship('Reservations', back_populates='user', cascade='all, delete-orphan')

class Parkinglots(db.Model):
    __tablename__ = 'parkinglots'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    location = db.Column(db.String(30), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(20), nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    
    spots = db.relationship('Parkingspots', back_populates='parkinglot', cascade='all, delete-orphan')

class Parkingspots(db.Model):
    __tablename__ = 'parkingspots'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parkinglots.id"), nullable=False)
    status = db.Column(db.String, nullable=False)
    spot_number = db.Column(db.String(20), nullable=False, default='A')
    
    parkinglot = db.relationship('Parkinglots', back_populates='spots')
    bookings = db.relationship('Reservations', back_populates='spot', cascade='all, delete-orphan')

class Reservations(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spot_id = db.Column(db.Integer, db.ForeignKey("parkingspots.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=False)
    parking_cost_per_unit_time = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False, default='0')
    
    user = db.relationship('Users', back_populates='bookings')
    spot = db.relationship('Parkingspots', back_populates='bookings')

def create_admin():
    admin = Users.query.filter_by(name='Jigyasa').first()
    if not admin:
        admin = Users(
            name='Jigyasa',
            email='jigyasa@gmail.com',
            psswd=generate_password_hash('J12345'),
            address='myaddress',
            pincode='1234XX'
        )
        db.session.add(admin)
        db.session.commit()

app = create_app()
app.app_context().push()
with app.app_context():
    db.create_all()
    create_admin()


@app.route('/')
def main():
    return render_template('main.html')

@app.route('/login.html', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form('username')
        password=request.form('password')
        print(username,password)
        user=User.query.filter_by(username=username).first()
        if user:
            if not check_password_hash(user.password,password):
                return redirect(url_for('login'))
            if user.username=='Jigyasa':
                session['username']=username
                return redirect(url_for('admin'))
            else:
                session['username']=username
                session[user_id]=user_id
                return redirect(url_for('user'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/admin', methods=['GET','POST'])
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('admin.html')


@app.route('/user',methods=['GET','POST'])
def user():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('user.html')


if __name__ == '__main__':
    app.run(debug=True)