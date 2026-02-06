#!/usr/bin/env python3
"""
Mobile-Friendly Web Application for Maintenance Management System
Based on the original 14-9.py Flet application
"""

from datetime import datetime
from io import BytesIO
import os

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
import pandas as pd
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def get_database_url():
    database_url = os.environ.get("DATABASE_URL", "sqlite:///maintenance.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    return database_url


def create_app():
    app = Flask(__name__)

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        if os.environ.get("FLASK_ENV") == "production":
            raise RuntimeError("SECRET_KEY is required in production")
        secret_key = "dev-secret-change-me"

    app.secret_key = secret_key
    app.config.update(
        SQLALCHEMY_DATABASE_URI=get_database_url(),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("FLASK_ENV") == "production",
        SESSION_TYPE=os.environ.get("SESSION_TYPE", "filesystem"),
        SESSION_FILE_DIR=os.path.join(app.instance_path, "sessions"),
        SESSION_PERMANENT=False,
    )

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)

    Session(app)
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    register_routes(app)
    register_cli(app)

    return app


class Branch(db.Model):
    __tablename__ = "Branches"

    branch_id = db.Column(db.Integer, primary_key=True)
    branch_name = db.Column(db.String(255), unique=True, nullable=False)


class MaintenanceType(db.Model):
    __tablename__ = "MaintenanceTypes"

    type_id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(255), unique=True, nullable=False)


class EquipmentName(db.Model):
    __tablename__ = "EquipmentNames"

    equipment_id = db.Column(db.Integer, primary_key=True)
    equipment_name = db.Column(db.String(255), unique=True, nullable=False)


class FaultType(db.Model):
    __tablename__ = "FaultTypes"

    fault_id = db.Column(db.Integer, primary_key=True)
    fault_name = db.Column(db.String(255), unique=True, nullable=False)


class SparePart(db.Model):
    __tablename__ = "SpareParts"

    part_id = db.Column(db.Integer, primary_key=True)
    part_name = db.Column(db.String(255), unique=True, nullable=False)


class Technician(db.Model):
    __tablename__ = "Technicians"

    technician_id = db.Column(db.Integer, primary_key=True)
    technician_name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(50), unique=True, nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey("Branches.branch_id"), nullable=False)


class MaintenanceRequest(db.Model):
    __tablename__ = "MaintenanceRequests"

    request_id = db.Column(db.Integer, primary_key=True)
    request_date = db.Column(db.String(50), nullable=False)
    requester_name = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    branch = db.Column(db.String(255), nullable=False)
    maintenance_type = db.Column(db.String(255), nullable=False)
    equipment_name = db.Column(db.String(255), nullable=False)
    fault_type = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)
    assigned_technician = db.Column(db.String(255))
    status = db.Column(db.String(50), nullable=False, default="open")
    start_time = db.Column(db.String(50))
    end_time = db.Column(db.String(50))


class Notification(db.Model):
    __tablename__ = "Notifications"

    notification_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, nullable=False)
    recipient_type = db.Column(db.String(50), nullable=False)
    recipient_id = db.Column(db.Integer)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.String(50), nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False)


class SparePartsRequest(db.Model):
    __tablename__ = "SparePartsRequests"

    spare_request_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, nullable=False)
    part_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="pending")


class PurchaseOrder(db.Model):
    __tablename__ = "PurchaseOrders"

    purchase_order_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, nullable=False)
    part_name = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="pending")


class User(db.Model):
    __tablename__ = "Users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    technician_id = db.Column(db.Integer)


def seed_data():
    if Branch.query.first():
        return

    branches = [
        Branch(branch_name="Main Branch"),
        Branch(branch_name="Secondary Branch"),
    ]
    technicians = [
        Technician(technician_name="Technician 1", phone_number="123456789", branch_id=1),
        Technician(technician_name="Technician 2", phone_number="987654321", branch_id=2),
    ]
    maintenance_types = [
        MaintenanceType(type_name="Preventive"),
        MaintenanceType(type_name="Corrective"),
    ]
    equipment_names = [
        EquipmentName(equipment_name="Machine A"),
        EquipmentName(equipment_name="Machine B"),
    ]
    fault_types = [
        FaultType(fault_name="Electrical"),
        FaultType(fault_name="Mechanical"),
    ]
    spare_parts = [
        SparePart(part_name="Motor"),
        SparePart(part_name="Gearbox"),
    ]

    users = [
        User(username="engineer", password=generate_password_hash("pass123"), role="engineer"),
        User(username="technician", password=generate_password_hash("pass123"), role="technician", technician_id=1),
        User(username="store", password=generate_password_hash("pass123"), role="store"),
        User(username="branch", password=generate_password_hash("pass123"), role="branch"),
        User(username="admin", password=generate_password_hash("pass123"), role="admin"),
    ]

    db.session.add_all(branches + technicians + maintenance_types + equipment_names + fault_types + spare_parts + users)
    db.session.commit()


def authenticate_user(username, password):
    user = User.query.filter_by(username=username).first()
    if not user:
        return None

    if check_password_hash(user.password, password):
        return user.role, user.technician_id

    if user.password == password:
        user.password = generate_password_hash(password)
        db.session.commit()
        return user.role, user.technician_id

    return None


def add_request(data):
    request_item = MaintenanceRequest(
        request_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        requester_name=data["requester_name"],
        phone_number=data["phone_number"],
        branch=data["branch"],
        maintenance_type=data["maintenance_type"],
        equipment_name=data["equipment_name"],
        fault_type=data["fault_type"],
        notes=data["notes"],
        status="open",
    )
    db.session.add(request_item)
    db.session.flush()

    notification = Notification(
        request_id=request_item.request_id,
        recipient_type="engineer",
        message=f"طلب صيانة جديد #{request_item.request_id} تم إنشاؤه",
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        is_read=False,
    )
    db.session.add(notification)
    db.session.commit()
    return request_item.request_id


def get_notifications(recipient_type, recipient_id=None):
    query = Notification.query.filter_by(recipient_type=recipient_type, is_read=False)
    if recipient_type == "technician" and recipient_id is not None:
        query = query.filter_by(recipient_id=recipient_id)
    return query.order_by(Notification.created_at.desc()).all()


def assign_technician(request_id, technician_name):
    technician = Technician.query.filter_by(technician_name=technician_name).first()
    request_item = db.session.get(MaintenanceRequest, request_id)
    if not technician or not request_item:
        return False

    request_item.assigned_technician = technician.technician_name
    notification = Notification(
        request_id=request_item.request_id,
        recipient_type="technician",
        recipient_id=technician.technician_id,
        message=f"تم تعيينك لطلب صيانة رقم #{request_item.request_id}",
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        is_read=False,
    )
    Notification.query.filter_by(
        request_id=request_item.request_id,
        recipient_type="engineer",
    ).update({"is_read": True})

    db.session.add(notification)
    db.session.commit()
    return True


def update_request_status(request_id, status, start_time=None, end_time=None):
    request_item = db.session.get(MaintenanceRequest, request_id)
    if not request_item:
        return False

    if status == "in_progress":
        request_item.status = status
        request_item.start_time = start_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif status == "closed":
        request_item.status = status
        request_item.end_time = end_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.session.add(
            Notification(
                request_id=request_item.request_id,
                recipient_type="requester",
                message=f"تم إغلاق طلب الصيانة #{request_item.request_id}",
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                is_read=False,
            )
        )
        db.session.add(
            Notification(
                request_id=request_item.request_id,
                recipient_type="engineer",
                message=f"تم إغلاق طلب الصيانة #{request_item.request_id}",
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                is_read=False,
            )
        )
    else:
        request_item.status = status

    db.session.commit()
    return True


def register_cli(app):
    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("Database tables created.")

    @app.cli.command("seed-db")
    def seed_db_command():
        seed_data()
        print("Seed data inserted.")


def register_routes(app):
    @app.route('/')
    def index():
        if 'user_role' not in session:
            return redirect(url_for('login'))
        return render_template('dashboard.html', role=session['user_role'])

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            auth_result = authenticate_user(username, password)
            if auth_result:
                role, technician_id = auth_result
                session['user_role'] = role
                session['username'] = username
                if role == "technician" and technician_id:
                    session['technician_id'] = technician_id
                flash('تم تسجيل الدخول بنجاح', 'success')
                return redirect(url_for('index'))
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')

        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('تم تسجيل الخروج بنجاح', 'success')
        return redirect(url_for('login'))

    @app.route('/create_request', methods=['GET', 'POST'])
    def create_request():
        if 'user_role' not in session or session['user_role'] not in ['engineer', 'branch', 'admin']:
            flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('index'))

        if request.method == 'POST':
            data = {
                'requester_name': request.form['requester_name'],
                'phone_number': request.form['phone_number'],
                'branch': request.form['branch'],
                'maintenance_type': request.form['maintenance_type'],
                'equipment_name': request.form['equipment_name'],
                'fault_type': request.form['fault_type'],
                'notes': request.form.get('notes', '')
            }

            request_id = add_request(data)
            if request_id:
                flash(f'تم إنشاء الطلب #{request_id} بنجاح', 'success')
                return redirect(url_for('index'))
            flash('حدث خطأ في إنشاء الطلب', 'error')

        return render_template(
            'create_request.html',
            branches=Branch.query.order_by(Branch.branch_name.asc()).all(),
            maintenance_types=MaintenanceType.query.order_by(MaintenanceType.type_name.asc()).all(),
            equipment_names=EquipmentName.query.order_by(EquipmentName.equipment_name.asc()).all(),
            fault_types=FaultType.query.order_by(FaultType.fault_name.asc()).all(),
        )

    @app.route('/requests')
    def view_requests():
        if 'user_role' not in session:
            return redirect(url_for('login'))

        requests = MaintenanceRequest.query.order_by(MaintenanceRequest.request_id.desc()).all()
        return render_template('requests.html', requests=requests)

    @app.route('/engineer')
    def engineer_dashboard():
        if 'user_role' not in session or session['user_role'] not in ['engineer', 'admin']:
            flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('index'))

        notifications = get_notifications("engineer")
        technicians = Technician.query.order_by(Technician.technician_name.asc()).all()
        return render_template('engineer.html', notifications=notifications, technicians=technicians)

    @app.route('/technician')
    def technician_dashboard():
        if 'user_role' not in session or session['user_role'] not in ['technician', 'admin']:
            flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('index'))

        technician_id = session.get('technician_id')
        notifications = get_notifications("technician", technician_id)
        return render_template('technician.html', notifications=notifications)

    @app.route('/assign_technician', methods=['POST'])
    def assign_technician_route():
        if 'user_role' not in session or session['user_role'] not in ['engineer', 'admin']:
            return jsonify({'error': 'غير مصرح'}), 403

        try:
            request_id = int(request.form['request_id'])
        except (TypeError, ValueError):
            flash('رقم الطلب غير صالح', 'error')
            return redirect(url_for('engineer_dashboard'))
        technician_name = request.form['technician_name']

        if assign_technician(request_id, technician_name):
            flash(f'تم تعيين الفني لطلب #{request_id}', 'success')
        else:
            flash('تعذر تعيين الفني', 'error')
        return redirect(url_for('engineer_dashboard'))

    @app.route('/update_status', methods=['POST'])
    def update_status():
        if 'user_role' not in session:
            return jsonify({'error': 'غير مصرح'}), 403

        try:
            request_id = int(request.form['request_id'])
        except (TypeError, ValueError):
            flash('رقم الطلب غير صالح', 'error')
            return redirect(url_for('technician_dashboard'))
        status = request.form['status']

        if update_request_status(request_id, status):
            flash(f'تم تحديث حالة الطلب #{request_id}', 'success')
        else:
            flash('تعذر تحديث حالة الطلب', 'error')

        if session['user_role'] == 'technician':
            return redirect(url_for('technician_dashboard'))
        return redirect(url_for('engineer_dashboard'))

    @app.route('/report')
    def report():
        if 'user_role' not in session or session['user_role'] not in ['engineer', 'admin']:
            flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('index'))

        requests = MaintenanceRequest.query.order_by(MaintenanceRequest.request_id.desc()).all()
        stats = {
            "total": len(requests),
            "open": len([req for req in requests if req.status == "open"]),
            "in_progress": len([req for req in requests if req.status == "in_progress"]),
            "closed": len([req for req in requests if req.status == "closed"]),
        }
        return render_template('report.html', requests=requests, stats=stats)

    @app.route('/export_excel')
    def export_excel():
        if 'user_role' not in session or session['user_role'] not in ['engineer', 'admin']:
            return jsonify({'error': 'غير مصرح'}), 403

        requests = MaintenanceRequest.query.order_by(MaintenanceRequest.request_id.desc()).all()
        data = []
        for req in requests:
            data.append({
                'رقم الطلب': req.request_id,
                'التاريخ': req.request_date,
                'الطالب': req.requester_name,
                'الهاتف': req.phone_number,
                'الفرع': req.branch,
                'نوع الصيانة': req.maintenance_type,
                'المعدة': req.equipment_name,
                'العطل': req.fault_type,
                'الحالة': req.status
            })

        df = pd.DataFrame(data)
        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        return send_file(
            output,
            download_name='maintenance_report.xlsx',
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )

    @app.route('/api/stats')
    def api_stats():
        if 'user_role' not in session:
            return jsonify({'error': 'غير مصرح'}), 403

        requests = MaintenanceRequest.query.all()
        stats = {
            'total': len(requests),
            'pending': len([r for r in requests if r.status == 'open']),
            'in_progress': len([r for r in requests if r.status == 'in_progress']),
            'completed': len([r for r in requests if r.status == 'closed'])
        }

        return jsonify(stats)


app = create_app()


if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)