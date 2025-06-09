from flask import Flask , render_template,request,redirect
from flask import current_app as app
from .model import *


@app.route('/',methods=['GET','POST'])
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        exist=User.query.filter(User.username==username).first()
        if exist:
            if username=='Admin@gmail.com' and  password=='12345':
                return redirect('/admin')
            if username==exist.username :
                if password==exist.password:
                    return redirect(f'/user/{exist.id}')
                return "INCORRECT PASSWORD"
        return "NO SUCH USERS"
    return render_template('login.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        address=request.form.get('address')
        phone=request.form.get('phone')
        fullname=request.form.get('fullname')
        new_user=User(username=username,password=password,phone=phone,full_name=fullname)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('signup.html')

@app.route('/admin',methods=['GET','POST'])
def admin():
    parkinglots=ParkingLot.query.all()
    for lot in parkinglots:
        lot.has_booking = any(spot.status == 'O' for spot in lot.parkingspots)
        
        lot.occupied_count=sum(1 for spot in lot.parkingspots if spot.status=='O')
    return render_template('admin.html',parkinglots=parkinglots)


@app.route('/new_lot',methods=['GET','POST'])
def new_lot():
    if request.method=='POST':
        action=request.form.get('action')
        if action=='Save':
            lot_name=request.form.get('lot_name')
            location=request.form.get('location')
            pincode=request.form.get('pincode')
            price=request.form.get('price')
            max_spot=request.form.get('max_spot')

            if lot_name!='' and location!='' and pincode!='' and price!='' and max_spot!='':
                new_parking_lot=ParkingLot(lot_name=lot_name,location=location,pincode=pincode,price=price,max_spot=max_spot)
                db.session.add(new_parking_lot)
                db.session.commit()
                for _ in range(new_parking_lot.max_spot):
                    new_parking_spot=ParkingSpot(status='A',lot_id=new_parking_lot.id)
                    db.session.add(new_parking_spot)
                db.session.commit()
                return redirect('/admin')
            return redirect('/admin')
        if action=='Cancel':
            return redirect('/admin')
    return render_template('new_lot.html')

@app.route('/delete/<int:lot_id>', methods=['GET','POST'])
def delete_lot(lot_id):
    lot=ParkingLot.query.filter(ParkingLot.id==lot_id).first()
    db.session.delete(lot)
    db.session.commit()
    return redirect('/admin')

@app.route('/edit/<int:lot_id>',methods=['GET','POST'])
def edit_lot(lot_id):
    lot=ParkingLot.query.filter(ParkingLot.id==lot_id).first()
    lot.occupied_count = sum(1 for spot in lot.parkingspots if spot.status=='O')
    if lot:
        if request.method=='POST':
            action=request.form.get('action')
            if action=='Save':
                lot.lot_name=request.form.get('lot_name')
                lot.location=request.form.get('location')
                lot.pincode=request.form.get('pincode')
                lot.price=request.form.get('price')
                lot.max_spot=request.form.get('max_spot')

                if lot.lot_name!='' and lot.location!='' and lot.pincode!='' and lot.price!='' and lot.max_spot!='':
                    db.session.commit()
                    ParkingSpot.query.filter(ParkingSpot.lot_id==lot.id,ParkingSpot.status=="A").delete()
                    db.session.commit()
                    for _ in range(lot.max_spot-lot.occupied_count):
                        new_spot = ParkingSpot(status="A",lot_id=lot.id)
                        db.session.add(new_spot)
                    db.session.commit()
                    return redirect("/admin")
                return redirect("/admin")
            if action=='Cancel':
                return redirect('/admin')
        return render_template('update_lot.html',lot=lot)
    return "No subject with this id"

@app.route('/user/<int:user_id>',methods=['GET','POST'])
def user(user_id):
    user=User.query.filter(User.id==user_id).first()
    lots=ParkingLot.query.all()
    return render_template('user.html',user=user,lots=lots)

@app.route("/reserve/<int:user_id>/<int:lot_id>",methods=['GET','POST'])
def reserve(user_id,lot_id):
    user=User.query.filter(User.id==user_id).first()
    lot=ParkingLot.query.filter(ParkingLot.id==lot_id).first()
    spot=ParkingSpot.query.filter(ParkingSpot.lot_id==lot.id,ParkingSpot.status=="A").group_by(ParkingSpot.id).first()
    if request.method=="POST":
        action=request.form.get('action')
        if action=='Reserve':
            if spot:

                vehicle_num=request.form.get('vehicle_num')
                exist_vehicle_num=Reservation.query.filter(Reservation.vehicle_num==vehicle_num,Reservation.release_time.is_(None)).first()
                if not  exist_vehicle_num:
                    new_reservation=Reservation(vehicle_num=vehicle_num,lot_id=lot.id,user_id=user.id,spot_id=spot.id)
                    db.session.add(new_reservation)
                    db.session.commit()
                    modify_spot=ParkingSpot.query.filter(ParkingSpot.id==spot.id,ParkingSpot.lot_id==lot.id).first()
                    modify_spot.status="O"
                    db.session.commit()
                    return redirect(f'/recent_booking/{user.id}')
                return "Already Parked"
            return "NO SPOT AVAILABLE"
        if action=='Close':
            return redirect(f'/user/{user.id}')
    return render_template('reserve.html',user=user,lot=lot,spot=spot)

@app.route('/reservation_details/<int:spot_id>',methods=['GET','POST'])
def reserved_details(spot_id):
    spot=ParkingSpot.query.filter(ParkingSpot.id==spot_id).first()
    reservations=spot.reservations
    return render_template('reservation_details.html',spot=spot,reservations=reservations)

@app.route('/release/<int:reservation_id>',methods=['GET','POST'])
def release_spot(reservation_id):
    reservation=Reservation.query.filter(Reservation.id==reservation_id).first()
    reservation_spot=ParkingSpot.query.filter(ParkingSpot.id==reservation.spot_id).first()
    reservation_lot=ParkingLot.query.filter(ParkingLot.id==reservation.lot_id).first()
    reservation_user=User.query.filter(User.id==reservation.user_id).first()

    reservation.release_time=datetime.utcnow()
    reservation.parking_cost = (((reservation.release_time - reservation.booking_time).total_seconds())/3600)*reservation_lot.price
    reservation_spot.status='A'
    db.session.commit()
    return redirect(f'/recent_booking/{reservation_user.id}')

@app.route("/recent_booking/<int:user_id>",methods=['GET','POST'])
def recent_booking(user_id):
    user=User.query.filter(User.id==user_id).first()
    return render_template('recent_booking.html',user=user)

@app.route('/edit_profile/<int:user_id>',methods=['GET','POST'])
def edit_profile(user_id):
    user=User.query.filter(User.id==user_id).first()
    if request.method=='POST':
        action=request.form.get('action')
        if action=="Update":

            updated_username=request.form.get('username')
            updated_password=request.form.get('password')
            updated_full_name=request.form.get('fullname')
            updated_phone=request.form.get('phone')
            exist=User.query.filter(User.username==updated_username,User.id!=user.id).first()
            if not exist:
                user.username=updated_username
                user.password=updated_password
                user.full_name=updated_full_name
                user.phone=updated_phone
                db.session.commit()
                return redirect(f'/user/{user.id}')
            return "Username exists"
        if action=="Close":
            return redirect(f'/user/{user.id}')
    return render_template('update_profile.html',user=user)

@app.route('/admin_users_list',methods=['GET','POST'])
def admin_users_list():
    users=User.query.filter(User.id!=1).all()
    return render_template('user_list.html',users=users)#left->Frontend

@app.route('/admin_summary',methods=["GET","POST"])
def admin_summary():
    total_users=User.query.filter(User.id!=1).count()
    total_lots=ParkingLot.query.count()
    total_active_reservations=Reservation.query.filter(Reservation.release_time.is_(None)).count()
    return render_template('admin_summary.html',total_users=total_users,total_lots=total_lots,total_active_reservations=total_active_reservations)