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
            if username=='Admin' and  password=='12345':
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
    lots=ParkingLot.query.all()
    return render_template('admin.html',lots=lots)


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
    if lot:
        if request.method=='POST':
            action=request.form.get('action')
            if action=='Save':
                lot.lot_name=request.form.get('lot_name')
                lot.location=request.form.get('location')
                lot.pincode=request.form.get('pincode')
                lot.price=request.form.get('price')
                lot.max_spot=lot.max_spot

                if lot.lot_name!='' and lot.location!='' and lot.pincode!='' and lot.price!='' and lot.max_spot!='':
                    db.session.commit()
                    return redirect('/admin')
                return redirect('/admin')
            if action=='Cancel':
                return redirect('/admin')
        return render_template('update_lot.html',lot=lot)
    return "No subject with this id"

@app.route('/user/<int:user_id>',methods=['GET','POST'])
def user(user_id):
    user=User.query.filter(User.id==user_id).first()
    lots=ParkingLot.query.all()
    return render_template('user.html',user=user,lots=lots)

