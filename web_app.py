#!/usr/bin/env python3
"""
Mobile-Friendly Web Application for Maintenance Management System
Based on the original 14-9.py Flet application
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime
import pandas as pd
import os
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'maintenance_system_secret_key_2024_change_in_production')

DB_PATH = "maintenance.db"

# ---------- Database Functions (from original code) ----------
def execute_query(query, params=(), fetch=False, many=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        if many:
            cursor.executemany(query, params)
        else:
            cursor.execute(query, params)
        conn.commit()
        if fetch:
            return cursor.fetchall()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print("DB error:", e)
        return None
    finally:
        conn.close()

def init_db():
    """Initialize database with all tables and sample data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executescript('''
            CREATE TABLE IF NOT EXISTS MaintenanceRequests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_date TEXT NOT NULL,
                requester_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                branch TEXT NOT NULL,
                maintenance_type TEXT NOT NULL,
                equipment_name TEXT NOT NULL,
                fault_type TEXT NOT NULL,
                notes TEXT,
                assigned_technician TEXT,
                status TEXT NOT NULL DEFAULT 'open',
                start_time TEXT,
                end_time TEXT
            );
            CREATE TABLE IF NOT EXISTS Technicians (
                technician_id INTEGER PRIMARY KEY AUTOINCREMENT,
                technician_name TEXT NOT NULL,
                phone_number TEXT NOT NULL UNIQUE,
                branch_id INTEGER NOT NULL,
                FOREIGN KEY (branch_id) REFERENCES Branches(branch_id)
            );
            CREATE TABLE IF NOT EXISTS SparePartsRequests (
                spare_request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                part_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                FOREIGN KEY (request_id) REFERENCES MaintenanceRequests(request_id)
            );
            CREATE TABLE IF NOT EXISTS Notifications (
                notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                recipient_type TEXT NOT NULL,
                recipient_id INTEGER,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                is_read BOOLEAN NOT NULL DEFAULT 0,
                FOREIGN KEY (request_id) REFERENCES MaintenanceRequests(request_id)
            );
            CREATE TABLE IF NOT EXISTS Branches (
                branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
                branch_name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS MaintenanceTypes (
                type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS EquipmentNames (
                equipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS FaultTypes (
                fault_id INTEGER PRIMARY KEY AUTOINCREMENT,
                fault_name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS SpareParts (
                part_id INTEGER PRIMARY KEY AUTOINCREMENT,
                part_name TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS PurchaseOrders (
                purchase_order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                part_name TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                FOREIGN KEY (request_id) REFERENCES MaintenanceRequests(request_id)
            );
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                technician_id INTEGER,
                FOREIGN KEY (technician_id) REFERENCES Technicians(technician_id)
            );
        ''')
        # Seed data
        cursor.execute("INSERT OR IGNORE INTO Branches (branch_name) VALUES (?)", ("Main Branch",))
        cursor.execute("INSERT OR IGNORE INTO Branches (branch_name) VALUES (?)", ("Secondary Branch",))
        cursor.execute("INSERT OR IGNORE INTO Technicians (technician_name, phone_number, branch_id) VALUES (?, ?, ?)", ("Technician 1", "123456789", 1))
        cursor.execute("INSERT OR IGNORE INTO Technicians (technician_name, phone_number, branch_id) VALUES (?, ?, ?)", ("Technician 2", "987654321", 2))
        cursor.execute("INSERT OR IGNORE INTO MaintenanceTypes (type_name) VALUES (?)", ("Preventive",))
        cursor.execute("INSERT OR IGNORE INTO MaintenanceTypes (type_name) VALUES (?)", ("Corrective",))
        cursor.execute("INSERT OR IGNORE INTO EquipmentNames (equipment_name) VALUES (?)", ("Machine A",))
        cursor.execute("INSERT OR IGNORE INTO EquipmentNames (equipment_name) VALUES (?)", ("Machine B",))
        cursor.execute("INSERT OR IGNORE INTO FaultTypes (fault_name) VALUES (?)", ("Electrical",))
        cursor.execute("INSERT OR IGNORE INTO FaultTypes (fault_name) VALUES (?)", ("Mechanical",))
        cursor.execute("INSERT OR IGNORE INTO SpareParts (part_name) VALUES (?)", ("Motor",))
        cursor.execute("INSERT OR IGNORE INTO SpareParts (part_name) VALUES (?)", ("Gearbox",))
        cursor.execute("INSERT OR IGNORE INTO Users (username, password, role, technician_id) VALUES (?, ?, ?, ?)", ("engineer", "pass123", "engineer", None))
        cursor.execute("INSERT OR IGNORE INTO Users (username, password, role, technician_id) VALUES (?, ?, ?, ?)", ("technician", "pass123", "technician", 1))
        cursor.execute("INSERT OR IGNORE INTO Users (username, password, role, technician_id) VALUES (?, ?, ?, ?)", ("store", "pass123", "store", None))
        cursor.execute("INSERT OR IGNORE INTO Users (username, password, role, technician_id) VALUES (?, ?, ?, ?)", ("branch", "pass123", "branch", None))
        cursor.execute("INSERT OR IGNORE INTO Users (username, password, role, technician_id) VALUES (?, ?, ?, ?)", ("admin", "pass123", "admin", None))
        conn.commit()
    except sqlite3.Error as e:
        print("Database initialization error:", e)
    finally:
        conn.close()

def authenticate_user(username, password):
    res = execute_query("SELECT role, technician_id FROM Users WHERE username = ? AND password = ?", (username, password), fetch=True)
    return res[0] if res else None

def add_request(data):
    request_id = execute_query('''
        INSERT INTO MaintenanceRequests (request_date, requester_name, phone_number, branch, maintenance_type, equipment_name, fault_type, notes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open')
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), data["requester_name"], data["phone_number"], data["branch"],
          data["maintenance_type"], data["equipment_name"], data["fault_type"], data["notes"]))
    if request_id:
        execute_query('''
            INSERT INTO Notifications (request_id, recipient_type, message, created_at)
            VALUES (?, ?, ?, ?)
        ''', (request_id, "engineer", f"طلب صيانة جديد #{request_id} تم إنشاؤه", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    return request_id

def get_branches():
    return execute_query("SELECT branch_id, branch_name FROM Branches", fetch=True) or []

def get_maintenance_types():
    return execute_query("SELECT type_id, type_name FROM MaintenanceTypes", fetch=True) or []

def get_equipment_names():
    return execute_query("SELECT equipment_id, equipment_name FROM EquipmentNames", fetch=True) or []

def get_fault_types():
    return execute_query("SELECT fault_id, fault_name FROM FaultTypes", fetch=True) or []

def get_requests():
    return execute_query("SELECT * FROM MaintenanceRequests", fetch=True) or []

def get_notifications(recipient_type, recipient_id=None):
    if recipient_type == "technician" and recipient_id is not None:
        return execute_query("SELECT * FROM Notifications WHERE recipient_type = ? AND recipient_id = ? AND is_read = 0", (recipient_type, recipient_id), fetch=True) or []
    return execute_query("SELECT * FROM Notifications WHERE recipient_type = ? AND is_read = 0", (recipient_type,), fetch=True) or []

def get_technicians(branch_id=None):
    query = "SELECT technician_name FROM Technicians"
    params = ()
    if branch_id is not None:
        query += " WHERE branch_id = ?"
        params = (branch_id,)
    res = execute_query(query, params, fetch=True)
    return [r[0] for r in res] if res else []

def get_branch_id(branch_name):
    res = execute_query("SELECT branch_id FROM Branches WHERE branch_name = ?", (branch_name,), fetch=True)
    return res[0][0] if res else None

def assign_technician(request_id, technician_name):
    res = execute_query("SELECT technician_id FROM Technicians WHERE technician_name = ?", (technician_name,), fetch=True)
    technician_id = res[0][0] if res else None
    if technician_id:
        execute_query("UPDATE MaintenanceRequests SET assigned_technician = ? WHERE request_id = ?", (technician_name, request_id))
        execute_query("INSERT INTO Notifications (request_id, recipient_type, recipient_id, message, created_at) VALUES (?, ?, ?, ?, ?)",
                     (request_id, "technician", technician_id, f"تم تعيينك لطلب صيانة رقم #{request_id}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        execute_query("UPDATE Notifications SET is_read = 1 WHERE request_id = ? AND recipient_type = 'engineer'", (request_id,))

def update_request_status(request_id, status, start_time=None, end_time=None):
    if status == "in_progress":
        execute_query("UPDATE MaintenanceRequests SET status = ?, start_time = ? WHERE request_id = ?", (status, start_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request_id))
    elif status == "closed":
        execute_query("UPDATE MaintenanceRequests SET status = ?, end_time = ? WHERE request_id = ?", (status, end_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S"), request_id))
        execute_query("INSERT INTO Notifications (request_id, recipient_type, message, created_at) VALUES (?, ?, ?, ?)",
                     (request_id, "requester", f"تم إغلاق طلب الصيانة #{request_id}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        execute_query("INSERT INTO Notifications (request_id, recipient_type, message, created_at) VALUES (?, ?, ?, ?)",
                     (request_id, "engineer", f"تم إغلاق طلب الصيانة #{request_id}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    else:
        execute_query("UPDATE MaintenanceRequests SET status = ? WHERE request_id = ?", (status, request_id))

def mark_notification_read(notification_id):
    return execute_query("UPDATE Notifications SET is_read = 1 WHERE notification_id = ?", (notification_id,))

# ---------- Web Routes ----------

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
        else:
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
        else:
            flash('حدث خطأ في إنشاء الطلب', 'error')
    
    return render_template('create_request.html', 
                         branches=get_branches(),
                         maintenance_types=get_maintenance_types(),
                         equipment_names=get_equipment_names(),
                         fault_types=get_fault_types())

@app.route('/requests')
def view_requests():
    if 'user_role' not in session:
        return redirect(url_for('login'))
    
    requests = get_requests()
    return render_template('requests.html', requests=requests)

@app.route('/engineer')
def engineer_dashboard():
    if 'user_role' not in session or session['user_role'] not in ['engineer', 'admin']:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('index'))
    
    notifications = get_notifications("engineer")
    return render_template('engineer.html', notifications=notifications)

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
    
    request_id = request.form['request_id']
    technician_name = request.form['technician_name']
    
    assign_technician(request_id, technician_name)
    flash(f'تم تعيين الفني لطلب #{request_id}', 'success')
    return redirect(url_for('engineer_dashboard'))

@app.route('/update_status', methods=['POST'])
def update_status():
    if 'user_role' not in session:
        return jsonify({'error': 'غير مصرح'}), 403
    
    request_id = request.form['request_id']
    status = request.form['status']
    
    update_request_status(request_id, status)
    flash(f'تم تحديث حالة الطلب #{request_id}', 'success')
    
    if session['user_role'] == 'technician':
        return redirect(url_for('technician_dashboard'))
    else:
        return redirect(url_for('engineer_dashboard'))

@app.route('/report')
def report():
    if 'user_role' not in session or session['user_role'] not in ['engineer', 'admin']:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('index'))
    
    requests = get_requests()
    return render_template('report.html', requests=requests)

@app.route('/export_excel')
def export_excel():
    if 'user_role' not in session or session['user_role'] not in ['engineer', 'admin']:
        return jsonify({'error': 'غير مصرح'}), 403
    
    requests = get_requests()
    data = []
    for req in requests:
        data.append({
            'رقم الطلب': req[0],
            'التاريخ': req[1],
            'الطالب': req[2],
            'الهاتف': req[3],
            'الفرع': req[4],
            'نوع الصيانة': req[5],
            'المعدة': req[6],
            'العطل': req[7],
            'الحالة': req[10]
        })
    
    df = pd.DataFrame(data)
    df.to_excel('static/maintenance_report.xlsx', index=False, engine='openpyxl')
    
    flash('تم تصدير التقرير إلى maintenance_report.xlsx', 'success')
    return redirect(url_for('report'))

@app.route('/api/stats')
def api_stats():
    if 'user_role' not in session:
        return jsonify({'error': 'غير مصرح'}), 403
    
    requests = get_requests()
    stats = {
        'total': len(requests),
        'pending': len([r for r in requests if r[10] == 'open']),
        'in_progress': len([r for r in requests if r[10] == 'in_progress']),
        'completed': len([r for r in requests if r[10] == 'closed'])
    }
    
    return jsonify(stats)

# Initialize database on startup
init_db()

if __name__ == '__main__':
    # Create templates and static directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Run the app
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)