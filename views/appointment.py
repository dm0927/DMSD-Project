from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from sql.db import DB
from flask_bcrypt import Bcrypt
from datetime import date
from auth.models import User
from flask_login import login_user, login_required, logout_user, current_user

appointment = Blueprint('appointment', __name__, url_prefix='/appointment')

@appointment.route('/book', methods=['GET','POST'])
@login_required
def book():
    customer_id = current_user.get_id()
    vehicle = []
    location = []
    if request.method == "POST":
        try:
            bookingdate = request.form.get('bookingdate')
            location = request.form.get('location')
            vehicle = request.form.get('vehicle')
            services = request.form.getlist('services[]')
            customer_id = current_user.get_id()
            vehicletype = request.form.get('vehicletype')
                
            result = DB.insertOne("""
                                        INSERT INTO APPOINTMENT(Date, Location_ID, Customer_Id, Vehicle_ID)
                                        VALUES(%s, %s, %s, %s)
                                """, bookingdate, location, customer_id, vehicle)
            if result.status:
                result = DB.selectOne("""SELECT LAST_INSERT_ID() as Appointment_ID;""")
                overall_id = result.row['Appointment_ID']
                getSerivceDetailsget = DB.selectAll(f"""
                                        SELECT s.service_id as service_id, s.service_name, s.labor
                                        from service as s
                                        where s.service_id in ({','.join(map(str, services))})
                                    """)
                getPartDetails = DB.selectAll(f"""
                                        SELECT p.part_id, p.price
                                        from service as s
                                        left join service_offered as so on s.service_id = so.service_id 
                                        left join part as p on p.part_id = so.part_id
                                        where s.service_id in ({','.join(map(str, services))})
                                    """)
                grandTotal = 0
                billingInsert = """
                                INSERT INTO BILL(Appoint_ID, Vehicle_type, Service_Id, Invoice_ID, Price)
                                VALUES(%(Appoint_ID)s, %(Vehicle_type)s, %(Service_id)s, %(Invoice_ID)s, %(Price)s)
                            """
                billingPartInsert = """
                                INSERT INTO BILLPART(Appoint_ID, Part_ID, Invoice_ID, Price)
                                VALUES(%(Appoint_ID)s, %(Part_ID)s, %(Invoice_ID)s, %(Price)s)
                            """
                
                billingData = []
                billingPartData = []

                if getSerivceDetailsget.status and getSerivceDetailsget.rows:
                    for r in getSerivceDetailsget.rows:
                        grandTotal += float(r['labor'])
                        s = {
                            'Appoint_ID' : overall_id,
                            'Vehicle_type': vehicletype,
                            'Service_id' : r['service_id'],
                            'Invoice_ID' : overall_id,
                            'Price' : float(r['labor'])
                        }
                        billingData.append(s)
                if getPartDetails.status and getPartDetails.rows:
                    for r in getPartDetails.rows:
                        grandTotal += float(r['price'])
                        s = {
                            'Appoint_ID' : overall_id,
                            'Part_ID' : r['part_id'],
                            'Invoice_ID' : overall_id,
                            'Price' : float(r['price'])
                        }
                        billingPartData.append(s)

                    # Adding data in invoice table
                    result = DB.insertOne("""
                                                INSERT INTO invoice (Invoice_ID, Amount) VALUES(%s, %s)
                                            """, overall_id, grandTotal)
                    
                    result = DB.insertMany(billingInsert, billingData)
                    result = DB.insertMany(billingPartInsert, billingPartData)
                    flash("Booking Made Successfully, please drop your vehicle between Woody's working hours", "success")
        except Exception as e:
            print(str(e))
            flash("Something wen't wrong, please try again later", "danger")
    try:
        vehicle = DB.selectAll("""
                    SELECT Vehicle_ID
                    from VEHICLE
                    where Customer_ID = %s
                """, customer_id)

        location = DB.selectAll("""
                    SELECT Location_id, Address
                    from Location
                """)
    except Exception as e:
        flash("Something wen't wrong, please try again later", "danger")
    return render_template("appointmentbooking.html", vehicles=vehicle.rows, location=location.rows)

@appointment.route('/view')
@login_required
def view():
    customer_id = current_user.get_id()
    appointment = []
    appointmentCondition = {}
    appointmentQuery = """
                            SELECT a.Appoint_Id, a.Date, l.address, a.status
                            from Appointment as a
                            left join location as l on l.location_id = a.location_id
                            where 1 = 1
                        """
    try: 
        appointmentQuery += " and Customer_ID = %(cust_id)s"
        appointmentCondition['cust_id'] = customer_id

        vehiclelist = request.args.get('vehiclelist')
        location = request.args.get('location')

        if vehiclelist:
            appointmentQuery += " and a.Vehicle_ID = %(vehiclelist)s"
            appointmentCondition['vehiclelist'] = vehiclelist
        if location:
            appointmentQuery += " and a.Location_ID = %(location)s"
            appointmentCondition['location'] = location

        print(appointmentQuery)
        print(appointmentCondition)

        appointment = DB.selectAll(appointmentQuery, appointmentCondition)

        location = DB.selectAll("""
                    SELECT Location_id, Address
                    from Location
                """)
        
        vehicle = DB.selectAll("""
                    SELECT Vehicle_ID
                    from VEHICLE
                    where Customer_ID = %s
                """, customer_id)
        
    except Exception as e:
        pass
    return render_template("appointmentview.html", appointment=appointment.rows, vehicles=vehicle.rows, location=location.rows)

@appointment.route('/appointment-view')
@login_required
def appointmentview():
    customer_id = current_user.get_id()
    appointment_id = request.args.get('id')
    if appointment_id:

        getCardNumber = DB.selectOne(
                                        """
                                            Select Credit_Card from customer where Cust_id = %s
                                        """
                                    ,customer_id)
        try:
            appointmentResult = DB.selectOne("""
                        SELECT a.Appoint_Id, a.Date, l.address, a.status
                        from Appointment as a
                        left join location as l on l.location_id = a.location_id
                        where Appoint_Id = %s
                    """, appointment_id)
            if appointmentResult.status and appointmentResult.row:
                appointmentResult.row['temp_status'] = appointmentResult.row['status']
                appointmentResult.row['Date'] = str(appointmentResult.row['Date'])
                appointmentResult.row['status'] = appointmentResult.row['status'] if appointmentResult.row['status'] != "Completed" else appointmentResult.row['status'] + " Waiting for Payment"
            
            serviceResult = DB.selectAll("""
                        SELECT i.Amount as grand_total, b.Service_id, s.service_name, b.price 
                        from Invoice as i
                        left join bill as b on b.invoice_id = i.invoice_id
                        left join service as s on s.Service_Id = b.Service_id
                        where b.Appoint_Id = %s
                    """, appointment_id)

            partResult = DB.selectAll("""
                        SELECT bp.Part_ID, bp.Price, p.name
                        from billpart as bp
                        left join part as p on p.part_Id = bp.part_Id
                        where bp.Appoint_Id = %s
                    """, appointment_id)
            if appointmentResult.status and appointmentResult.row:
                appointmentResult.row['Date'] = str(appointmentResult.row['Date'])
        except Exception as e:
            print(str(e))
    else:
        return redirect(url_for('appointment.view'))
    return render_template("appointmentsingleview.html", appointmentResult=appointmentResult.row, serviceResult=serviceResult.rows, partResult=partResult.rows, cardNumber=getCardNumber.row)

@appointment.route('/payment-process', methods=['POST'])
@login_required
def paymentprocess():
    try:
        id = request.form.get('appointment_id')
        credit_card = request.form.get('creditcard')
        customer_id = current_user.get_id()

        paidDate = date.today().strftime('%Y-%m-%d')
        
        updateAppointment = DB.update(  """
                                            UPDATE INVOICE SET DATE_PAID = %s where Invoice_Id = %s
                                        """, paidDate, id)
        
        updateAppointment = DB.update(  """
                                            UPDATE APPOINTMENT SET status = "PAID" where Appoint_Id = %s
                                        """, id)

        updateAppointment = DB.update(  """
                                            UPDATE CUSTOMER SET Credit_Card = %s where Cust_Id = %s
                                        """, credit_card, customer_id)
        flash("Payment Made Successfully", "success")
        return redirect(url_for('appointment.view'))
    except Exception as e:
        print(str(e))
        return jsonify({
            'success':False,
            'data':{}
        })

@appointment.route('/getVehicleServices', methods=['POST'])
@login_required
def getVehicleServices():
    try:
        id = request.form.get('vehicleId')
        getData = DB.selectAll("""
                                    Select s.service_name as service_name, s.service_id as service_id, v.type as type
                                    from service as s
                                    left join vehicle as v on v.type = s.vehicle_type
                                    where v.vehicle_id = %s
                                """, id)
        if getData.status and getData.rows:
            return jsonify({
                'success':True,
                'data':getData.rows
            })
        else:
            return jsonify({
                'success':False,
                'data':{}
            })
    except:
        return jsonify({
            'success':False,
            'data':{}
        })