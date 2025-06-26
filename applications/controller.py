from flask import Flask , render_template,request,redirect,url_for,session
from flask import current_app as app
from .model import *
from datetime import datetime
import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from sqlalchemy import or_





@app.route('/',methods=['GET','POST'])
@app.route('/login',methods=['GET','POST'])
def login():
    admin=User.query.filter(User.id==1).first()
    if request.method=='POST':
        username=request.form.get('username')
        password=request.form.get('password')

        if username==admin.username and password==admin.password:
            return redirect('/admin')
        exist=User.query.filter(User.username==username).first()
        if exist:
            if username==exist.username :
                if password==exist.password:
                    return redirect(f'/user/{exist.id}')
                return render_template('not_found_password.html')
        return render_template('not_found_user.html')
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
    admin = User.query.filter(User.id==1).first()
    string = request.args.get('q')
    if not string or string=='*':
        parkinglots = ParkingLot.query.all()
    else:
        parkinglots = ParkingLot.query.filter(or_(ParkingLot.lot_name.ilike(f'%{string}%'),ParkingLot.location.ilike(f'%{string}%'))).all()


    for lot in parkinglots:
        lot.has_booking = any(spot.status == 'O' for spot in lot.parkingspots)
        lot.occupied_count=sum(1 for spot in lot.parkingspots if spot.status=='O')
    return render_template('admin.html',parkinglots=parkinglots,admin=admin)


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
        lot.occupied_count = sum(1 for spot in lot.parkingspots if spot.status=='O')
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
    return render_template('not_found_lot.html',lot=lot)

@app.route('/user/<int:user_id>',methods=['GET','POST'])
def user(user_id):
    user=User.query.filter(User.id==user_id).first()
    string = request.args.get('q1')
    field = request.args.get('q2')

    if not string:
        lots = ParkingLot.query.all()
    else:
        if field=='lot_id/lot_name':
            lots = ParkingLot.query.filter(or_(ParkingLot.id.ilike(f'%{string}%'),ParkingLot.lot_name.ilike(f'%{string}%'))).all()
        elif field=='location/pincode':
            lots = ParkingLot.query.filter(or_(ParkingLot.location.ilike(f'%{string}%'),ParkingLot.pincode.ilike(f'%{string}%'))).all()
    return render_template('user.html',user=user,lots=lots)

@app.route("/reserve/<int:user_id>/<int:lot_id>",methods=['GET','POST'])
def reserve(user_id,lot_id):
    user=User.query.filter(User.id==user_id).first()
    lot=ParkingLot.query.filter(ParkingLot.id==lot_id).first()
    spot=ParkingSpot.query.filter(ParkingSpot.lot_id==lot.id,ParkingSpot.status=="A").group_by(ParkingSpot.id).first()
    if spot:
        if request.method=="POST":
            action=request.form.get('action')
            if action=='Reserve':
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
                    return render_template('exist.html',user=user,lot=lot)
            if action=='Close':
                return redirect(f'/user/{user.id}')
        return render_template('reserve.html',user=user,lot=lot,spot=spot)
    return render_template('not_found_spot.html',user=user)

    
@app.route('/reservation_details', methods=['GET','POST'])
@app.route('/reservation_details/<int:spot_id>',methods=['GET','POST'])
def reserved_details(spot_id=None):
    user_id=request.args.get('q')
    if not user_id:
        reservations = [Reservation.query.filter(Reservation.spot_id==spot_id,Reservation.release_time.is_(None)).first()]
    else:
        reservations=[]
        user=User.query.filter(User.id==user_id).first()
        reservations=user.reservations
    return render_template('reservation_details.html',reservations=reservations)

@app.route('/see_reservation/<int:user_id>',methods=['GET','POST'])
def see_reservation(user_id):
    return redirect(url_for('reserved_details',q=user_id))

@app.route('/release/<int:reservation_id>',methods=['GET','POST'])
def release_spot(reservation_id):
    reservation=Reservation.query.filter(Reservation.id==reservation_id).first()
    reservation_spot=ParkingSpot.query.filter(ParkingSpot.id==reservation.spot_id).first()
    reservation_lot=ParkingLot.query.filter(ParkingLot.id==reservation.lot_id).first()
    reservation_user=User.query.filter(User.id==reservation.user_id).first()

    reservation.release_time=get_local_time()


    b_time=reservation.booking_time
    r_time=reservation.release_time
    if b_time.tzinfo is None:
        b_time=b_time.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
    if r_time.tzinfo is None:
        r_time=r_time.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
    reservation.parking_cost = round((((r_time - b_time).total_seconds())/3600)*reservation_lot.price,2)
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
                if user.id!=1:
                    return redirect(f'/user/{user.id}')
                else:
                    return redirect('/admin')
            return render_template('exist_user.html',user=user)
        if action=="Cancel":
            if user.id!=1:
                return redirect(f'/user/{user.id}')
            else:
                return redirect('/admin')
    return render_template('update_profile.html',user=user)

@app.route('/admin_users_list',methods=['GET','POST'])
def admin_users_list():
    users=User.query.filter(User.id!=1).all()
    return render_template('user_list.html',users=users)

@app.route('/user_summary/<int:user_id>',methods=['GET','POST'])
def user_summary(user_id):
    user=User.query.filter_by(id=user_id).first()
    reservations=[i for i in user.reservations if i.release_time]
    active_booking=sum(1 for i in user.reservations if not i.release_time)

    if reservations:
        total_seconds=0
        total_cost=0
        lot_visitor_counter=Counter()
        duration_count=0

        for r in reservations:
            if r.release_time:
                b_time=r.booking_time
                r_time=r.release_time

                if b_time.tzinfo is None:
                    b_time=b_time.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
                    r_time=r_time.replace(tzinfo=ZoneInfo("Asia/Kolkata"))
                   

                duration=(r_time-b_time).total_seconds()
                total_seconds+=duration
                duration_count+=1
            if r.parking_cost:
                total_cost+=r.parking_cost
            lot_visitor_counter[r.lot_id]+=1

        total_hours=total_seconds/3600
        avg_duration_hours=(total_seconds/duration_count)/3600
        most_visited_lot_id=lot_visitor_counter.most_common(1)[0][0] if lot_visitor_counter else None
        most_visited_lot=ParkingLot.query.get(most_visited_lot_id) if most_visited_lot_id else 'N/A'
   

        lot_spending=defaultdict(float)

        for r in reservations:
            if r.parking_cost and r.lot_id:
                lot_spending[r.lot_id]+=r.parking_cost

        if not lot_spending:
            return

        lot_names=[]
        total_spent=[]

        for lot_id,amount in lot_spending.items():
            lot=ParkingLot.query.get(lot_id)
            lot_name=lot.lot_name
            lot_names.append(lot_name)
            total_spent.append(round(amount,2))

        plt.figure(figsize=(6,5))
        bars = plt.bar(lot_names, total_spent, color='blue', edgecolor='black')

        plt.xlabel("Parking Lot", fontsize=14)
        plt.ylabel("Total Amount (₹)", fontsize=14)
        plt.xticks(rotation=45, fontsize=12)
        plt.yticks(fontsize=12)
        plt.ylim(0, max(total_spent) * 1.2)
        plt.tight_layout()


        for bar in bars:
            height = bar.get_height()
            y = height + 0.01
            plt.text(bar.get_x() + bar.get_width()/2, y, f"₹{height:.2f}", ha='center', va='bottom', fontsize=12)

        plt.savefig("static/user_spending_per_lot.png", dpi=200)
        plt.close()
            
            
        lot_counts=defaultdict(int)
        for r in reservations:
            if r.lot_id:
                lot_counts[r.lot_id]+=1

        if not lot_counts:
            print("No reservation data to be plotted")
            return

        lot_names=[]
        reservation_counts=[]

        for lot_id, count in lot_counts.items():
            lot = ParkingLot.query.get(lot_id)
            lot_name = lot.lot_name if lot else f"Lot {lot_id}"
            lot_names.append(lot_name)
            reservation_counts.append(count)


        plt.figure(figsize=(6,5))
        bars=plt.bar(lot_names,reservation_counts,color='blue')

        plt.xlabel("Parking Lot",fontsize=14)
        plt.ylabel("Reservations",fontsize=14)
        plt.xticks(rotation=45,fontsize=12)
        plt.yticks(fontsize=12)
        plt.ylim(0, max(reservation_counts) * 1.2)
        plt.tight_layout()
        for bar in bars:
            height=bar.get_height()
            y=height+0.01
            plt.text(bar.get_x() + bar.get_width()/2, y, str(int(height)),ha='center', va="bottom",fontsize=12)

        plt.savefig("static/user_reservation_count.png",dpi=200)
        plt.close()

        return render_template('user_summary.html',user=user,reservations=reservations,total_hours=round(total_hours,2),total_cost=round(total_cost,0),
        avg_duration=round(avg_duration_hours,2),most_visited_lot=most_visited_lot,active_booking=active_booking)
        
    return render_template('user_summary.html',user=user,reservations=reservations,active_booking=active_booking)


@app.route('/admin_summary',methods=['GET','POST'])
def admin_summary():
    total_user = User.query.filter(User.id!=1).count()
    total_lot = ParkingLot.query.count()
    active_reservation = Reservation.query.filter(Reservation.release_time.is_(None)).count()
    total_spots = ParkingSpot.query.count()
    total_reservations = Reservation.query.count()



    if total_lot:
        occupied_count = ParkingSpot.query.filter(ParkingSpot.status=='O').count()
        available_count = ParkingSpot.query.filter(ParkingSpot.status=='A').count() 
        spot_status_chart(occupied_count,available_count)


    revenue_data = (db.session.query(ParkingLot.lot_name, db.func.sum(Reservation.parking_cost))
        .join(Reservation, Reservation.lot_id == ParkingLot.id)
        .group_by(ParkingLot.lot_name).all())
    revenue_chart(revenue_data)
    reservation_data = db.session.query(ParkingLot.lot_name, db.func.count(Reservation.id))\
        .join(Reservation, Reservation.lot_id == ParkingLot.id)\
        .group_by(ParkingLot.lot_name).all()
    reservation_count_chart(reservation_data)



    today = datetime.today()
    start_dt = datetime.combine(today, datetime.min.time())
    end_dt = datetime.combine(today, datetime.max.time())
    todays_reservations = Reservation.query.filter(
        Reservation.booking_time >= start_dt,
        Reservation.booking_time <= end_dt
    ).all()
    for i in todays_reservations:
        i.parkinglot = ParkingLot.query.filter(ParkingLot.id==i.lot_id).first()
    
    

    return render_template('admin_summary.html',total_user=total_user,total_lot=total_lot,active_reservation=active_reservation,total_spots=total_spots,total_reservations=total_reservations,todays_reservations=todays_reservations)

def spot_status_chart(occupied,available):
    labels = ['Occupied', 'Available']
    sizes = [occupied, available]      
    colors = ['white', 'blue']

    plt.figure(figsize=(3, 3))
    plt.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        pctdistance=1.25,
        startangle=45
    )


    plt.gca().add_patch(
        plt.Circle((0, 0), 1.0, color='blue', fill=False, linewidth=2)
    )

    
    plt.savefig("static/spot_status_pie_chart.png", dpi=200, bbox_inches="tight")
    plt.close()

def revenue_chart(data):  
    lots = [d[0] for d in data]
    revenue = [d[1] or 0 for d in data]

    plt.figure(figsize=(8,5))
    plt.bar(lots, revenue, color='blue')
    plt.xlabel('Parking Lot',fontsize=20)
    plt.ylabel('Revenue (₹)',fontsize=20)
    plt.xticks(rotation=45,fontsize=20)
    plt.yticks(fontsize=20)
    plt.ylim(0, max(revenue) * 1.2)
    plt.tight_layout()
    plt.savefig("static/revenue_bar_chart.png", dpi=200, bbox_inches="tight")
    plt.close()

def reservation_count_chart(data):
    lots = [d[0] for d in data]
    counts = [d[1] for d in data]

    plt.figure(figsize=(8,5))
    # ax = plt.gca()
    # ax.yaxis.set_major_locator(MaxNLocator(integer=True)) 
    plt.bar(lots, counts, color='blue')
    plt.xlabel('Parking Lot',fontsize=20)
    plt.ylabel('Total Reservations',fontsize=20)
    plt.xticks(rotation=45,fontsize=20)
    plt.yticks(fontsize=20)
    plt.savefig("static/reservation_count_bar_chart.png", dpi=200, bbox_inches="tight")
    plt.close()

@app.route('/user_list', methods=['GET','POST'])
def user_list():
    string = request.args.get('q')
    if not string or string=='*':
        users = User.query.filter(User.id!=1).all()
    else:
        users = User.query.filter(User.id!=1,or_(User.username.ilike(f'%{string}%'),User.id.ilike(f'%{string}%'))).all()

    return render_template('user_list.html',users=users)

@app.route('/admin_search',methods=['GET','POST'])
def admin_search():
    string=request.form.get('string')
    field=request.form.get('field')
    
    if field=="user_id/username":
        return redirect(url_for('user_list', q=string))
    if field=='lot_name/location':
        return redirect(url_for('admin',q=string))
        

@app.route("/user_search/<int:user_id>", methods=['GET','POST'])
def user_search(user_id):
    string = request.form.get('string')
    field = request.form.get('field')
    
    if field=="lot_id/lot_name":
        return redirect(url_for('user',user_id=user_id,q1=string,q2=field))
    if field=="location/pincode":
        return redirect(url_for('user',user_id=user_id,q1=string,q2=field))


@app.route("/read_available_spot/<int:spot_id>/<int:lot_id>",methods=['GET','POST'])
def read_available_spot(spot_id,lot_id):
    spot=ParkingSpot.query.filter(ParkingSpot.id==spot_id).first()
    lot=ParkingLot.query.filter(ParkingLot.id==lot_id).first()
    if lot:
        if spot:
            if request.method=='POST':
                action=request.form.get('action')
                if action=="Delete":
                    db.session.delete(spot)
                    lot.max_spot-=1
                    db.session.commit()
                    return redirect('/admin')
                if action=="Cancel":
                    return redirect('/admin')
            return render_template('read_available_spot.html',spot=spot,lot=lot)
        return render_template('incorrect_spot_id.html')
    return render_template('incorrect_lot_id.html')

