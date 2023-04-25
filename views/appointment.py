from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from sql.db import DB
from flask_bcrypt import Bcrypt

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
        bookingdate = request.form.get('bookingdate')
        location = request.form.get('location')
        vehicle = request.form.get('vehicle')
        services = request.form.getlist('services[]')
        customer_id = current_user.get_id()
        services = "(" + ",".join(str(x) for x in services) + ")"
        result = DB.selectAll("""
                                    SELECT s.service_name, s.labor, p.name, p.price
                                    from service as s
                                    left join service_offered as so on s.service_id = so.service_id 
                                    left join part as p on p.part_id = so.part_id
                                    where s.service_id in %s
                                  """,services)
        print(result)

        # result = DB.insertOne("""
        #                             INSERT INTO APPOINTMENT(Date, Location_ID, Customer_Id, Vehicle_ID)
        #                             VALUES(%s, %s, %s, %s)
        #                       """, bookingdate, location, customer_id, vehicle)
        # if result.status:
        #     result = DB.selectOne("""SELECT LAST_INSERT_ID() as Appointment_ID;""")
        #     overall_id = result.row['Appointment_ID']
        #     result = DB.selectAll("""
        #                             SELECT s.service_name, s.labor, p.name, p.price
        #                             from service as s
        #                             left join service_offered as so on s.service_id = s.service_id
        #                             left join part as p on p.part_id = so.part_id
        #                             where s.service_name in %s
        #                           """, services)
            

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
        pass
    return render_template("appointmentbooking.html", vehicles=vehicle.rows, location=location.rows)

@appointment.route('/view')
@login_required
def view():
    customer_id = current_user.get_id()
    appointment = []
    try:
        appointment = DB.selectAll("""
                    SELECT Appoint_Id, Date
                    from Appointment
                    where Customer_ID = %s
                """, customer_id)
    except Exception as e:
        pass
    return render_template("appointmentview.html", appointment=appointment.rows)

@appointment.route('/getVehicleServices', methods=['POST'])
@login_required
def getVehicleServices():
    try:
        id = request.form.get('vehicleId')
        getData = DB.selectAll("""
                                    Select s.service_name as service_name, s.service_id as service_id
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