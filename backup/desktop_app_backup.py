import sqlite3
from datetime import datetime
import flet as ft
import pandas as pd

DB_PATH = "maintenance.db"

# ---------- DB generic helpers ----------
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

def generic_add(table, field, value):
    return execute_query(f"INSERT INTO {table} ({field}) VALUES (?)", (value,))

def generic_update(table, id_field, id_value, field, value):
    return execute_query(f"UPDATE {table} SET {field} = ? WHERE {id_field} = ?", (value, id_value))

def generic_delete(table, id_field, id_value):
    return execute_query(f"DELETE FROM {table} WHERE {id_field} = ?", (id_value,))

def generic_get_all(table, cols="*"):
    res = execute_query(f"SELECT {cols} FROM {table}", fetch=True)
    return res if res else []

# ---------- init DB ----------
def init_db():
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
        # Seed
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

# ---------- thin wrappers ----------
def authenticate_user(username, password):
    print(f"Attempting to authenticate: username={username}, password={password}")  # Debug
    res = execute_query("SELECT role, technician_id FROM Users WHERE username = ? AND password = ?", (username, password), fetch=True)
    print(f"Query result: {res}")  # Debug
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

def add_branch(branch_name): return generic_add("Branches", "branch_name", branch_name)
def update_branch(branch_id, branch_name): return generic_update("Branches", "branch_id", branch_id, "branch_name", branch_name)
def delete_branch(branch_id): return generic_delete("Branches", "branch_id", branch_id)
def get_branches(): return generic_get_all("Branches")

def add_maintenance_type(name): return generic_add("MaintenanceTypes", "type_name", name)
def update_maintenance_type(id_, name): return generic_update("MaintenanceTypes", "type_id", id_, "type_name", name)
def delete_maintenance_type(id_): return generic_delete("MaintenanceTypes", "type_id", id_)
def get_maintenance_types(): return generic_get_all("MaintenanceTypes")

def add_equipment_name(name): return generic_add("EquipmentNames", "equipment_name", name)
def update_equipment_name(id_, name): return generic_update("EquipmentNames", "equipment_id", id_, "equipment_name", name)
def delete_equipment_name(id_): return generic_delete("EquipmentNames", "equipment_id", id_)
def get_equipment_names(): return generic_get_all("EquipmentNames")

def add_fault_type(name): return generic_add("FaultTypes", "fault_name", name)
def update_fault_type(id_, name): return generic_update("FaultTypes", "fault_id", id_, "fault_name", name)
def delete_fault_type(id_): return generic_delete("FaultTypes", "fault_id", id_)
def get_fault_types(): return generic_get_all("FaultTypes")

def add_spare_part(name): return generic_add("SpareParts", "part_name", name)
def get_spare_parts(): return execute_query("SELECT part_id, part_name FROM SpareParts", fetch=True) or []

def add_purchase_order(request_id, part_name, details):
    return execute_query('''
        INSERT INTO PurchaseOrders (request_id, part_name, details, created_at, status)
        VALUES (?, ?, ?, ?, 'pending')
    ''', (request_id, part_name, details, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

def get_purchase_orders():
    return execute_query("SELECT purchase_order_id, request_id, part_name, details, created_at, status FROM PurchaseOrders", fetch=True) or []

def update_purchase_order_status(purchase_order_id, status, request_id):
    execute_query("UPDATE PurchaseOrders SET status = ? WHERE purchase_order_id = ?", (status, purchase_order_id))
    if status == "approved":
        execute_query("INSERT INTO Notifications (request_id, recipient_type, message, created_at) VALUES (?, ?, ?, ?)",
                     (request_id, "engineer", f"تم الموافقة على طلب الشراء #{purchase_order_id}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        execute_query("INSERT INTO Notifications (request_id, recipient_type, message, created_at) VALUES (?, ?, ?, ?)",
                     (request_id, "store", f"تم شراء الأصناف لطلب الشراء #{purchase_order_id}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    elif status == "rejected":
        execute_query("INSERT INTO Notifications (request_id, recipient_type, message, created_at) VALUES (?, ?, ?, ?)",
                     (request_id, "engineer", f"تم رفض طلب الشراء #{purchase_order_id}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

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

def request_spare_part(request_id, part_names):
    for part_name in part_names:
        execute_query("INSERT INTO SparePartsRequests (request_id, part_name) VALUES (?, ?)", (request_id, part_name))
        execute_query("INSERT INTO Notifications (request_id, recipient_type, message, created_at) VALUES (?, ?, ?, ?)",
                     (request_id, "store", f"طلب قطعة غيار للطلب #{request_id}: {part_name}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

def update_spare_part_status(spare_request_id, status):
    execute_query("UPDATE SparePartsRequests SET status = ? WHERE spare_request_id = ?", (status, spare_request_id))
    if status == "unavailable":
        res = execute_query("SELECT request_id, part_name FROM SparePartsRequests WHERE spare_request_id = ?", (spare_request_id,), fetch=True)
        if res:
            request_id, part_name = res[0]
            # جمع جميع الأصناف غير المتوفرة للطلب
            unavailable_parts = execute_query("SELECT part_name FROM SparePartsRequests WHERE request_id = ? AND status = 'unavailable'", (request_id,), fetch=True)
            parts_list = ', '.join([p[0] for p in unavailable_parts]) if unavailable_parts else part_name
            execute_query("INSERT INTO Notifications (request_id, recipient_type, message, created_at) VALUES (?, ?, ?, ?)",
                         (request_id, "engineer", f"الأصناف غير المتوفرة للطلب #{request_id}: {parts_list}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

def get_notifications(recipient_type, recipient_id=None):
    if recipient_type == "technician" and recipient_id is not None:
        return execute_query("SELECT * FROM Notifications WHERE recipient_type = ? AND recipient_id = ? AND is_read = 0", (recipient_type, recipient_id), fetch=True) or []
    return execute_query("SELECT * FROM Notifications WHERE recipient_type = ? AND is_read = 0", (recipient_type,), fetch=True) or []

def mark_notification_read(notification_id):
    return execute_query("UPDATE Notifications SET is_read = 1 WHERE notification_id = ?", (notification_id,))

def get_requests():
    return execute_query("SELECT * FROM MaintenanceRequests", fetch=True) or []

def get_branch_id(branch_name):
    res = execute_query("SELECT branch_id FROM Branches WHERE branch_name = ?", (branch_name,), fetch=True)
    return res[0][0] if res else None

def get_technicians(branch_id=None):
    query = "SELECT technician_name FROM Technicians"
    params = ()
    if branch_id is not None:
        query += " WHERE branch_id = ?"
        params = (branch_id,)
    res = execute_query(query, params, fetch=True)
    return [r[0] for r in res] if res else []

def get_technicians_all():
    return execute_query("""
        SELECT t.technician_id, t.technician_name, t.phone_number, t.branch_id, b.branch_name 
        FROM Technicians t JOIN Branches b ON t.branch_id = b.branch_id
    """, fetch=True) or []

def add_technician(name, phone, branch_id):
    return execute_query("INSERT INTO Technicians (technician_name, phone_number, branch_id) VALUES (?, ?, ?)", (name, phone, branch_id))

def update_technician(technician_id, name, phone, branch_id):
    return execute_query("UPDATE Technicians SET technician_name = ?, phone_number = ?, branch_id = ? WHERE technician_id = ?", (name, phone, branch_id, technician_id))

def delete_technician(technician_id):
    return execute_query("DELETE FROM Technicians WHERE technician_id = ?", (technician_id,))

def get_spare_parts_requests():
    return execute_query("SELECT * FROM SparePartsRequests WHERE status = 'pending'", fetch=True) or []

def add_user(username, password, role, technician_id=None):
    return execute_query("INSERT INTO Users (username, password, role, technician_id) VALUES (?, ?, ?, ?)", (username, password, role, technician_id))

def update_user(user_id, username, password, role, technician_id=None):
    return execute_query("UPDATE Users SET username = ?, password = ?, role = ?, technician_id = ? WHERE user_id = ?", (username, password, role, technician_id, user_id))

def delete_user(user_id):
    return execute_query("DELETE FROM Users WHERE user_id = ?", (user_id,))

def get_users():
    return execute_query("SELECT user_id, username, role, technician_id FROM Users", fetch=True) or []

# ---------- Flet UI ----------
def main(page: ft.Page):
    page.title = "تطبيق إدارة الصيانة"
    page.window_width = 1000
    page.window_height = 700
    page.window_min_width = 800
    page.window_min_height = 600
    page.window_resizable = True
    page.window_maximizable = True
    page.text_direction = "rtl"
    page.padding = 0

    init_db()

    def show_snackbar(page_obj, message):
        snack = ft.SnackBar(content=ft.Text(message, text_align=ft.TextAlign.RIGHT, color=ft.Colors.WHITE))
        page_obj.overlay.append(snack)
        snack.open = True
        page_obj.update()

    def logout(e):
        page.session.clear()
        page.views.clear()
        show_snackbar(page, "تم تسجيل الخروج بنجاح")
        page.views.append(login_view())
        page.update()

    def route_change(route):
        role = page.session.get("user_role") or None
        page.views.clear()
        print(f"Navigating to route: {page.route}, Role: {role}")  # Debug
        if page.route == "/login" or not role:
            print("Rendering login_view")  # Debug
            page.views.append(login_view())
        elif page.route == "/":
            print("Rendering main_menu_view")  # Debug
            page.views.append(main_menu_view())
        elif page.route == "/create_request" and role in ["engineer", "branch", "admin"]:
            print("Rendering create_request_view")  # Debug
            page.views.append(create_request_view())
        elif page.route == "/manage_data" and role in ["engineer", "admin"]:
            print("Rendering manage_data_view")  # Debug
            page.views.append(manage_data_view())
        elif page.route == "/report" and role in ["engineer", "admin"]:
            print("Rendering report_view")  # Debug
            page.views.append(report_view())
        elif page.route == "/engineer" and role in ["engineer", "admin"]:
            print("Rendering engineer_view")  # Debug
            page.views.append(engineer_view())
        elif page.route == "/technician" and role in ["technician", "admin"]:
            print("Rendering technician_view")  # Debug
            page.views.append(technician_view())
        elif page.route == "/store" and role in ["store", "admin"]:
            print("Rendering store_view")  # Debug
            page.views.append(store_view())
        elif page.route == "/purchase_orders" and role in ["engineer", "admin"]:
            print("Rendering purchase_orders_view")  # Debug
            page.views.append(purchase_orders_view())
        elif page.route == "/branch" and role in ["branch", "admin"]:
            print("Rendering branch_view")  # Debug
            page.views.append(branch_view())
        elif page.route == "/manage_users" and role == "admin":
            print("Rendering manage_users_view")  # Debug
            page.views.append(manage_users_view())
        elif page.route == "/manage_technicians" and role == "admin":
            print("Rendering manage_technicians_view")  # Debug
            page.views.append(manage_technicians_view())
        elif page.route == "/add_branch" and role == "admin":
            print("Rendering add_branch_view")  # Debug
            page.views.append(add_branch_view())
        elif page.route == "/add_maintenance_type" and role == "admin":
            print("Rendering add_maintenance_type_view")  # Debug
            page.views.append(add_maintenance_type_view())
        elif page.route == "/add_equipment" and role == "admin":
            print("Rendering add_equipment_name_view")  # Debug
            page.views.append(add_equipment_name_view())
        elif page.route == "/add_fault_type" and role == "admin":
            print("Rendering add_fault_type_view")  # Debug
            page.views.append(add_fault_type_view())
        elif page.route == "/add_spare_part" and role == "admin":
            print("Rendering add_spare_part_view")  # Debug
            page.views.append(add_spare_part_view())
        else:
            print("Rendering default main_menu_view")  # Debug
            show_snackbar(page, "غير مصرح لك بالوصول إلى هذه الصفحة")
            page.views.append(main_menu_view())
        page.update()

    page.on_route_change = route_change
    page.go("/login")

    # Login
    def login_view():
        username = ft.TextField(label="اسم المستخدم", width=300, text_align=ft.TextAlign.RIGHT, autofocus=True)
        password = ft.TextField(label="كلمة المرور", password=True, width=300, text_align=ft.TextAlign.RIGHT)
        def login(e):
            auth_result = authenticate_user(username.value, password.value)
            if auth_result:
                role, technician_id = auth_result
                page.session.set("user_role", role)
                if role == "technician" and technician_id:
                    page.session.set("technician_id", technician_id)
                page.views.clear()
                page.views.append(main_menu_view())
                page.update()
            else:
                show_snackbar(page, "اسم المستخدم أو كلمة المرور غير صحيحة")
        return ft.View("/login", [
            ft.AppBar(title=ft.Text("تسجيل الدخول", style=ft.TextStyle(weight=ft.FontWeight.BOLD)), automatically_imply_leading=False),
            ft.Container(
                content=ft.Column(
                    [username, password, ft.ElevatedButton("تسجيل الدخول", icon=ft.Icons.LOGIN, on_click=login)],
                    spacing=15, alignment=ft.MainAxisAlignment.CENTER
                ),
                padding=20, alignment=ft.alignment.center, expand=True
            )
        ])

    # Main menu
    def main_menu_view():
        role = page.session.get("user_role")
        buttons = []
        if role in ["engineer", "branch", "admin"]:
            buttons.append(ft.ElevatedButton("إنشاء طلب صيانة", on_click=lambda e: page.go("/create_request")))
        if role in ["engineer", "admin"]:
            buttons.extend([
                ft.ElevatedButton("تقرير طلبات الصيانة", on_click=lambda e: page.go("/report")),
                ft.ElevatedButton("إدارة طلبات الشراء", on_click=lambda e: page.go("/purchase_orders")),
                ft.ElevatedButton("لوحة المهندس", on_click=lambda e: page.go("/engineer")),
                ft.ElevatedButton("إدارة البيانات", on_click=lambda e: page.go("/manage_data"))
            ])
        if role in ["technician", "admin"]:
            buttons.append(ft.ElevatedButton("لوحة الفني", on_click=lambda e: page.go("/technician")))
        if role in ["store", "admin"]:
            buttons.append(ft.ElevatedButton("لوحة المخزن", on_click=lambda e: page.go("/store")))
        if role in ["branch", "admin"]:
            buttons.append(ft.ElevatedButton("لوحة الفرع", on_click=lambda e: page.go("/branch")))
        if role == "admin":
            buttons.extend([
                ft.ElevatedButton("إدارة المستخدمين", on_click=lambda e: page.go("/manage_users")),
                ft.ElevatedButton("إدارة الفنيين", on_click=lambda e: page.go("/manage_technicians")),
                ft.ElevatedButton("إضافة فرع", on_click=lambda e: page.go("/add_branch")),
                ft.ElevatedButton("إضافة نوع صيانة", on_click=lambda e: page.go("/add_maintenance_type")),
                ft.ElevatedButton("إضافة اسم معدة", on_click=lambda e: page.go("/add_equipment")),
                ft.ElevatedButton("إضافة نوع عطل", on_click=lambda e: page.go("/add_fault_type")),
                ft.ElevatedButton("إضافة قطعة غيار", on_click=lambda e: page.go("/add_spare_part"))
            ])
        return ft.View("/", [
            ft.AppBar(actions=[ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)], automatically_imply_leading=False, title=ft.Text("القائمة الرئيسية", style=ft.TextStyle(weight=ft.FontWeight.BOLD))),
            ft.Container(
                content=ft.Column(buttons + [ft.ElevatedButton("تسجيل الخروج", icon=ft.Icons.LOGOUT, on_click=logout)],
                                 spacing=15, alignment=ft.MainAxisAlignment.CENTER),
                padding=20, alignment=ft.alignment.center, expand=True
            )
        ])

    # Create request
    def create_request_view():
        requester_name = ft.TextField(label="اسم الطالب", width=300, text_align=ft.TextAlign.RIGHT)
        phone_number = ft.TextField(label="رقم الهاتف", width=300, text_align=ft.TextAlign.RIGHT)
        branch = ft.Dropdown(label="الفرع", options=[ft.dropdown.Option(b[1]) for b in get_branches()], width=300, text_align=ft.TextAlign.RIGHT)
        maintenance_type = ft.Dropdown(label="نوع الصيانة", options=[ft.dropdown.Option(t[1]) for t in get_maintenance_types()], width=300, text_align=ft.TextAlign.RIGHT)
        equipment_name = ft.Dropdown(label="اسم المعدة", options=[ft.dropdown.Option(e[1]) for e in get_equipment_names()], width=300, text_align=ft.TextAlign.RIGHT)
        fault_type = ft.Dropdown(label="نوع العطل", options=[ft.dropdown.Option(f[1]) for f in get_fault_types()], width=300, text_align=ft.TextAlign.RIGHT)
        notes = ft.TextField(label="ملاحظات", multiline=True, width=300, text_align=ft.TextAlign.RIGHT)
        def submit_request(e):
            if not all([requester_name.value, phone_number.value, branch.value, maintenance_type.value, equipment_name.value, fault_type.value]):
                show_snackbar(page, "يرجى ملء جميع الحقول المطلوبة")
                return
            data = {
                "requester_name": requester_name.value,
                "phone_number": phone_number.value,
                "branch": branch.value,
                "maintenance_type": maintenance_type.value,
                "equipment_name": equipment_name.value,
                "fault_type": fault_type.value,
                "notes": notes.value
            }
            request_id = add_request(data)
            show_snackbar(page, f"تم إنشاء الطلب #{request_id} بنجاح")
            page.views.clear()
            page.views.append(main_menu_view())
            page.update()
        return ft.View("/create_request", [
            ft.AppBar(actions=[ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)], automatically_imply_leading=False, title=ft.Text("إنشاء طلب صيانة", style=ft.TextStyle(weight=ft.FontWeight.BOLD))),
            ft.Container(
                content=ft.Column([
                    requester_name, phone_number, branch, maintenance_type, equipment_name, fault_type, notes,
                    ft.Row([
                        ft.ElevatedButton("إرسال", icon=ft.Icons.SEND, on_click=submit_request),
                        ft.ElevatedButton("رجوع", icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/"))
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
                padding=20, expand=True
            )
        ])

    # Generic add view factory
    def make_add_view(route, title_text, label_text, add_fn):
        field = ft.TextField(label=label_text, width=300, text_align=ft.TextAlign.RIGHT)
        def submit(e):
            if field.value:
                add_fn(field.value)
                show_snackbar(page, f"تم إضافة {field.value}")
                page.go("/")
            else:
                show_snackbar(page, "يرجى إدخال القيمة")
        return ft.View(route, [
            ft.AppBar(actions=[ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)], automatically_imply_leading=False, title=ft.Text(title_text, style=ft.TextStyle(weight=ft.FontWeight.BOLD))),
            ft.Container(
                content=ft.Column([
                    field,
                    ft.Row([
                        ft.ElevatedButton("إرسال", icon=ft.Icons.SAVE, on_click=submit),
                        ft.ElevatedButton("رجوع", icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/"))
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=15, alignment=ft.MainAxisAlignment.CENTER),
                padding=20, expand=True
            )
        ])

    def add_branch_view(): return make_add_view("/add_branch", "إضافة فرع", "اسم الفرع", add_branch)
    def add_maintenance_type_view(): return make_add_view("/add_maintenance_type", "إضافة نوع صيانة", "اسم نوع الصيانة", add_maintenance_type)
    def add_equipment_name_view(): return make_add_view("/add_equipment", "إضافة اسم معدة", "اسم المعدة", add_equipment_name)
    def add_fault_type_view(): return make_add_view("/add_fault_type", "إضافة نوع عطل", "اسم نوع العطل", add_fault_type)
    def add_spare_part_view(): return make_add_view("/add_spare_part", "إضافة قطعة غيار", "اسم قطعة الغيار", add_spare_part)

    # Manage data table factory
    def make_manage_table(title, get_fn, update_fn, delete_fn, name_label):
        print(f"Entering make_manage_table for {title}, fetching data...")  # Debug
        rows = []
        for rec in get_fn():
            print(f"Processing record: {rec}")  # Debug
            rid, name = rec[0], rec[1]
            name_tf = ft.TextField(value=name, width=200, text_align=ft.TextAlign.RIGHT)
            def do_update(e, rid=rid, tf=name_tf):
                update_fn(rid, tf.value)
                show_snackbar(page, f"تم تحديث '{tf.value}'")
                page.views.clear()
                page.views.append(manage_data_view())
                page.update()
            def do_delete(e, rid=rid):
                delete_fn(rid)
                show_snackbar(page, "تم الحذف")
                page.views.clear()
                page.views.append(manage_data_view())
                page.update()
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(name_tf),
                        ft.DataCell(ft.Row([ft.IconButton(ft.Icons.EDIT, on_click=do_update),
                                            ft.IconButton(ft.Icons.DELETE, on_click=do_delete)]))
                    ]
                )
            )
        print(f"make_manage_table: Number of rows for {title} = {len(rows)}")  # Debug
        table_content = ft.Text(f"لا توجد {title} متاحة للعرض") if not rows else ft.DataTable(
            columns=[ft.DataColumn(ft.Text(name_label)), ft.DataColumn(ft.Text("الإجراءات"))],
            rows=rows,
            expand=True
        )
        return ft.Column([
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            table_content
        ])

    def manage_data_view():
        return ft.View("/manage_data", [
            ft.AppBar(actions=[ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)], automatically_imply_leading=False, title=ft.Text("إدارة البيانات", style=ft.TextStyle(weight=ft.FontWeight.BOLD))),
            ft.Container(
                content=ft.Column([
                    make_manage_table("الفروع", get_branches, update_branch, delete_branch, "اسم الفرع"),
                    make_manage_table("أنواع الصيانة", get_maintenance_types, update_maintenance_type, delete_maintenance_type, "اسم النوع"),
                    make_manage_table("أسماء المعدات", get_equipment_names, update_equipment_name, delete_equipment_name, "اسم المعدة"),
                    make_manage_table("أنواع الأعطال", get_fault_types, update_fault_type, delete_fault_type, "اسم العطل"),
                    ft.ElevatedButton("رجوع", icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/"))
                ], scroll=ft.ScrollMode.AUTO, spacing=20),
                padding=20, expand=True
            )
        ])

    # Manage Users view (admin)
    def manage_users_view():
        print("Entering manage_users_view, fetching data...")  # Debug
        rows = []
        users = get_users()
        technicians = get_technicians_all()
        print(f"manage_users_view: Number of users = {len(users)}, Users = {users}")  # Debug
        print(f"manage_users_view: Number of technicians = {len(technicians)}, Technicians = {technicians}")  # Debug
        
        for u in users:
            if len(u) < 4:  # التأكد من أن السجل يحتوي على جميع الحقول المتوقعة
                print(f"Skipping invalid user record: {u}")  # Debug
                continue
            uid, uname, urole, technician_id = u
            if not uname or not urole:  # التأكد من أن الحقول ليست None أو فارغة
                print(f"Skipping user with invalid data: {u}")  # Debug
                continue
            
            uname_tf = ft.TextField(value=uname, width=180, text_align=ft.TextAlign.RIGHT)
            pass_tf = ft.TextField(value="", hint_text="كلمة مرور جديدة (اتركه فارغًا للاحتفاظ القديمة)", password=True, width=200, text_align=ft.TextAlign.RIGHT)
            role_dd = ft.Dropdown(
                value=urole,
                options=[ft.dropdown.Option(r) for r in ["admin", "engineer", "technician", "store", "branch"]],
                width=160, text_align=ft.TextAlign.RIGHT
            )
            technician_options = [ft.dropdown.Option(str(t[0]), t[1]) for t in technicians] + [ft.dropdown.Option("NULL", "غير مرتبط")]
            technician_dd = ft.Dropdown(
                value=str(technician_id) if technician_id else "NULL",
                options=technician_options,
                width=160, text_align=ft.TextAlign.RIGHT,
                visible=True  # دائمًا مرئي لتجنب AssertionError
            )
            if urole != "technician":  # إخفاء بصري للأدوار غير technician
                technician_dd.opacity = 0
                technician_dd.disabled = True
            def do_update(e, uid=uid, uname_tf=uname_tf, pass_tf=pass_tf, role_dd=role_dd, technician_dd=technician_dd):
                if not uname_tf.value.strip():
                    show_snackbar(page, "اسم المستخدم لا يمكن أن يكون فارغًا")
                    return
                if pass_tf.value:
                    new_pass = pass_tf.value
                else:
                    res = execute_query("SELECT password FROM Users WHERE user_id=?", (uid,), fetch=True)
                    new_pass = res[0][0] if res and res[0] else ""
                tech_id = int(technician_dd.value) if technician_dd.value and technician_dd.value != "NULL" else None
                res_upd = update_user(uid, uname_tf.value.strip(), new_pass, role_dd.value, tech_id)
                if res_upd is None:
                    show_snackbar(page, "خطأ أثناء تحديث المستخدم (ربما اسم المستخدم موجود مسبقًا)")
                else:
                    show_snackbar(page, f"تم تحديث المستخدم '{uname_tf.value}'")
                page.views.clear()
                page.views.append(manage_users_view())
                page.update()
            def do_delete(e, uid=uid):
                delete_user(uid)
                show_snackbar(page, "تم حذف المستخدم")
                page.views.clear()
                page.views.append(manage_users_view())
                page.update()
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(uname_tf),
                        ft.DataCell(role_dd),
                        ft.DataCell(pass_tf),
                        ft.DataCell(technician_dd),
                        ft.DataCell(ft.Row([ft.IconButton(ft.Icons.EDIT, on_click=do_update), ft.IconButton(ft.Icons.DELETE, on_click=do_delete)]))
                    ]
                )
            )
        
        valid_rows = [row for row in rows if len(row.cells) == 5]
        print(f"manage_users_view: Number of valid rows = {len(valid_rows)}")  # Debug
        
        table_content = ft.Text("لا يوجد مستخدمون متاحون للعرض", size=16, text_align=ft.TextAlign.CENTER) if not valid_rows else ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("اسم المستخدم")),
                ft.DataColumn(ft.Text("الدور")),
                ft.DataColumn(ft.Text("كلمة المرور (اختياري)")),
                ft.DataColumn(ft.Text("الفني")),
                ft.DataColumn(ft.Text("الإجراءات"))
            ],
            rows=valid_rows,
            expand=True
        )
        
        new_username = ft.TextField(label="اسم المستخدم", width=180, text_align=ft.TextAlign.RIGHT)
        new_password = ft.TextField(label="كلمة المرور", password=True, width=180, text_align=ft.TextAlign.RIGHT)
        new_role = ft.Dropdown(
            label="الدور",
            options=[ft.dropdown.Option(r) for r in ["admin", "engineer", "technician", "store", "branch"]],
            width=160, text_align=ft.TextAlign.RIGHT
        )
        new_technician = ft.Dropdown(
            label="الفني",
            options=[ft.dropdown.Option(str(t[0]), t[1]) for t in technicians] + [ft.dropdown.Option("NULL", "غير مرتبط")],
            width=160, text_align=ft.TextAlign.RIGHT,
            visible=False
        )
        def on_role_change(e):
            new_technician.visible = new_role.value == "technician"
            page.update()
        new_role.on_change = on_role_change
        def add_new_user(e):
            if not (new_username.value and new_password.value and new_role.value):
                show_snackbar(page, "يرجى إدخال جميع بيانات المستخدم الجديد")
                return
            tech_id = int(new_technician.value) if new_technician.value and new_technician.value != "NULL" else None
            res = add_user(new_username.value.strip(), new_password.value, new_role.value, tech_id)
            if res is None:
                show_snackbar(page, "خطأ أثناء إضافة المستخدم (اسم المستخدم قد يكون موجودًا)")
            else:
                show_snackbar(page, "تم إضافة المستخدم بنجاح")
            page.views.clear()
            page.views.append(manage_users_view())
            page.update()
        return ft.View("/manage_users", [
            ft.AppBar(actions=[ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)], automatically_imply_leading=False, title=ft.Text("إدارة المستخدمين", style=ft.TextStyle(weight=ft.FontWeight.BOLD))),
            ft.Container(
                content=ft.Column([
                    ft.Text("المستخدمون الحاليون", size=20, weight=ft.FontWeight.BOLD),
                    table_content,
                    ft.Divider(),
                    ft.Text("إضافة مستخدم جديد", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([new_username, new_password, new_role, new_technician, ft.ElevatedButton("إضافة", icon=ft.Icons.ADD, on_click=add_new_user)]),
                    ft.ElevatedButton("رجوع", icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/"))
                ], scroll=ft.ScrollMode.AUTO, spacing=20),
                padding=20, expand=True
            )
        ])

    # Manage Technicians view (admin)
    def manage_technicians_view():
        print("Entering manage_technicians_view, fetching data...")  # Debug
        rows = []
        technicians = get_technicians_all()
        branches = get_branches()
        print(f"manage_technicians_view: Number of technicians = {len(technicians)}")  # Debug
        for t in technicians:
            tid, tname, phone, branch_id, branch_name = t
            name_tf = ft.TextField(value=tname, width=180, text_align=ft.TextAlign.RIGHT)
            phone_tf = ft.TextField(value=phone, width=180, text_align=ft.TextAlign.RIGHT)
            branch_dd = ft.Dropdown(
                value=str(branch_id),
                options=[ft.dropdown.Option(str(b[0]), b[1]) for b in branches],
                width=180, text_align=ft.TextAlign.RIGHT
            )
            def do_update(e, tid=tid, name_tf=name_tf, phone_tf=phone_tf, branch_dd=branch_dd):
                update_technician(tid, name_tf.value, phone_tf.value, int(branch_dd.value))
                show_snackbar(page, f"تم تحديث الفني '{name_tf.value}'")
                page.views.clear()
                page.views.append(manage_technicians_view())
                page.update()
            def do_delete(e, tid=tid):
                delete_technician(tid)
                show_snackbar(page, "تم حذف الفني")
                page.views.clear()
                page.views.append(manage_technicians_view())
                page.update()
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(name_tf),
                        ft.DataCell(phone_tf),
                        ft.DataCell(branch_dd),
                        ft.DataCell(ft.Row([ft.IconButton(ft.Icons.EDIT, on_click=do_update), ft.IconButton(ft.Icons.DELETE, on_click=do_delete)]))
                    ]
                )
            )
        table_content = ft.Text("لا يوجد فنيون متاحون للعرض") if not rows else ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("اسم الفني")),
                ft.DataColumn(ft.Text("رقم الهاتف")),
                ft.DataColumn(ft.Text("الفرع")),
                ft.DataColumn(ft.Text("الإجراءات"))
            ],
            rows=rows,
            expand=True
        )
        new_name = ft.TextField(label="اسم الفني", width=180, text_align=ft.TextAlign.RIGHT)
        new_phone = ft.TextField(label="رقم الهاتف", width=180, text_align=ft.TextAlign.RIGHT)
        new_branch = ft.Dropdown(
            label="الفرع",
            options=[ft.dropdown.Option(str(b[0]), b[1]) for b in branches],
            width=180, text_align=ft.TextAlign.RIGHT
        )
        def add_new_technician(e):
            if not (new_name.value and new_phone.value and new_branch.value):
                show_snackbar(page, "يرجى إدخال جميع بيانات الفني الجديد")
                return
            add_technician(new_name.value, new_phone.value, int(new_branch.value))
            show_snackbar(page, "تم إضافة الفني بنجاح")
            page.views.clear()
            page.views.append(manage_technicians_view())
            page.update()
        return ft.View("/manage_technicians", [
            ft.AppBar(actions=[ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)], automatically_imply_leading=False, title=ft.Text("إدارة الفنيين", style=ft.TextStyle(weight=ft.FontWeight.BOLD))),
            ft.Container(
                content=ft.Column([
                    ft.Text("الفنيون الحاليون", size=20, weight=ft.FontWeight.BOLD),
                    table_content,
                    ft.Divider(),
                    ft.Text("إضافة فني جديد", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([new_name, new_phone, new_branch, ft.ElevatedButton("إضافة", icon=ft.Icons.ADD, on_click=add_new_technician)]),
                    ft.ElevatedButton("رجوع", icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/"))
                ], scroll=ft.ScrollMode.AUTO, spacing=20),
                padding=20, expand=True
            )
        ])

    # Report view
    def report_view():
        status_filter = ft.Dropdown(
            label="تصفية حسب الحالة",
            options=[
                ft.dropdown.Option("all", "الكل"),
                ft.dropdown.Option("open", "مفتوح"),
                ft.dropdown.Option("in_progress", "تحت التنفيذ"),
                ft.dropdown.Option("waiting", "انتظار"),
                ft.dropdown.Option("closed", "مغلق")
            ],
            value="all", width=200, text_align=ft.TextAlign.RIGHT
        )
        branch_filter = ft.Dropdown(
            label="تصفية حسب الفرع",
            options=[ft.dropdown.Option("all", "الكل")] + [ft.dropdown.Option(b[1], b[1]) for b in get_branches()],
            value="all", width=200, text_align=ft.TextAlign.RIGHT
        )
        def get_report_rows():
            rows = []
            for req in get_requests():
                if status_filter.value != "all" and req[10] != status_filter.value: continue
                if branch_filter.value != "all" and req[4] != branch_filter.value: continue
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(req[0]))),
                            ft.DataCell(ft.Text(req[1])),
                            ft.DataCell(ft.Text(req[2])),
                            ft.DataCell(ft.Text(req[3])),
                            ft.DataCell(ft.Text(req[4])),
                            ft.DataCell(ft.Text(req[5])),
                            ft.DataCell(ft.Text(req[6])),
                            ft.DataCell(ft.Text(req[7])),
                            ft.DataCell(ft.Text(req[10]))
                        ]
                    )
                )
            return rows
        rows = get_report_rows()
        table_content = ft.Text("لا توجد بيانات متاحة للعرض") if not rows else ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("رقم الطلب")),
                ft.DataColumn(ft.Text("التاريخ")),
                ft.DataColumn(ft.Text("الطالب")),
                ft.DataColumn(ft.Text("الهاتف")),
                ft.DataColumn(ft.Text("الفرع")),
                ft.DataColumn(ft.Text("نوع الصيانة")),
                ft.DataColumn(ft.Text("المعدة")),
                ft.DataColumn(ft.Text("العطل")),
                ft.DataColumn(ft.Text("الحالة"))
            ],
            rows=rows,
            border=ft.border.all(1, ft.Colors.GREY_400),
            heading_row_color=ft.Colors.BLUE_50,
            data_row_color=ft.Colors.WHITE,
            expand=True
        )
        def update_report(e):
            page.views.clear()
            page.views.append(report_view())
            page.update()
        def export_report(e):
            data = []
            for req in get_requests():
                if status_filter.value != "all" and req[10] != status_filter.value: continue
                if branch_filter.value != "all" and req[4] != branch_filter.value: continue
                data.append({
                    "رقم الطلب": req[0], "التاريخ": req[1], "الطالب": req[2],
                    "الهاتف": req[3], "الفرع": req[4], "نوع الصيانة": req[5],
                    "المعدة": req[6], "العطل": req[7], "الحالة": req[10]
                })
            df = pd.DataFrame(data)
            df.to_excel("maintenance_report.xlsx", index=False, engine='openpyxl')
            show_snackbar(page, "تم تصدير التقرير إلى maintenance_report.xlsx")
        return ft.View("/report", [
            ft.AppBar(actions=[ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)], automatically_imply_leading=False, title=ft.Text("تقرير طلبات الصيانة", style=ft.TextStyle(weight=ft.FontWeight.BOLD))),
            ft.Container(
                content=ft.Column([
                    ft.Row([status_filter, branch_filter], alignment=ft.MainAxisAlignment.CENTER),
                    ft.Row([
                        ft.ElevatedButton("تحديث التقرير", icon=ft.Icons.REFRESH, on_click=update_report),
                        ft.ElevatedButton("تصدير التقرير", icon=ft.Icons.DOWNLOAD, on_click=export_report)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    table_content,
                    ft.ElevatedButton("رجوع", icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/"))
                ], scroll=ft.ScrollMode.AUTO, spacing=20),
                padding=20, expand=True
            )
        ])
        def on_filter_change(e):
            page.views.clear()
            page.views.append(report_view())
            page.update()
        status_filter.on_change = on_filter_change
        rows = []
        for r in get_report_rows():
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(r[0]))),
                        ft.DataCell(ft.Text(r[1])),
                        ft.DataCell(ft.Text(r[2])),
                        ft.DataCell(ft.Text(r[3])),
                        ft.DataCell(ft.Text(r[4])),
                        ft.DataCell(ft.Text(r[5])),
                        ft.DataCell(ft.Text(r[6])),
                        ft.DataCell(ft.Text(r[7])),
                        ft.DataCell(ft.Text(r[8] or "غير محدد")),
                        ft.DataCell(ft.Text(r[10])),
                        ft.DataCell(ft.Text(r[11] or "غير محدد")),
                        ft.DataCell(ft.Text(r[12] or "غير محدد"))
                    ]
                )
            )
        print(f"report_view: Number of rows = {len(rows)}")  # Debug
        table_content = ft.Text("لا توجد بيانات متاحة للعرض") if not rows else ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("رقم الطلب")),
                ft.DataColumn(ft.Text("تاريخ الطلب")),
                ft.DataColumn(ft.Text("اسم الطالب")),
                ft.DataColumn(ft.Text("رقم الهاتف")),
                ft.DataColumn(ft.Text("الفرع")),
                ft.DataColumn(ft.Text("نوع الصيانة")),
                ft.DataColumn(ft.Text("اسم المعدة")),
                ft.DataColumn(ft.Text("نوع العطل")),
                ft.DataColumn(ft.Text("ملاحظات")),
                ft.DataColumn(ft.Text("الحالة")),
                ft.DataColumn(ft.Text("وقت البدء")),
                ft.DataColumn(ft.Text("وقت الانتهاء"))
            ],
            rows=rows,
            expand=True
        )
        def export_to_excel(e):
            if not rows:
                show_snackbar(page, "لا توجد بيانات لتصديرها")
                return
            df = pd.DataFrame([r.cells for r in rows], columns=[c.label.value for c in table_content.columns])
            df.to_excel("maintenance_report.xlsx", index=False)
            show_snackbar(page, "تم تصدير التقرير إلى maintenance_report.xlsx")
        return ft.View("/report", [
            ft.AppBar(actions=[ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)], automatically_imply_leading=False, title=ft.Text("تقرير طلبات الصيانة", style=ft.TextStyle(weight=ft.FontWeight.BOLD))),
            ft.Container(
                content=ft.Column([
                    status_filter,
                    table_content,
                    ft.ElevatedButton("تصدير إلى Excel", icon=ft.Icons.TABLE_CHART, on_click=export_to_excel),
                    ft.ElevatedButton("رجوع", icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/"))
                ], scroll=ft.ScrollMode.AUTO, spacing=20),
                padding=20, expand=True
            )
        ])

    # Engineer view
    def engineer_view():
        print("Entering engineer_view, fetching data...")  # Debug
        notifications = get_notifications("engineer")
        print(f"engineer_view: Number of notifications = {len(notifications)}")  # Debug
        rows = []
        for n in notifications:
            nid, request_id, _, _, message, created_at, _ = n
            request_data = execute_query("SELECT * FROM MaintenanceRequests WHERE request_id = ?", (request_id,), fetch=True)
            if not request_data:
                continue
            r = request_data[0]
            technician_dd = ft.Dropdown(
                label="اختيار الفني",
                options=[ft.dropdown.Option(t) for t in get_technicians(get_branch_id(r[4]))],
                width=200, text_align=ft.TextAlign.RIGHT
            )
            def assign(e, request_id=request_id, technician_dd=technician_dd):
                if technician_dd.value:
                    assign_technician(request_id, technician_dd.value)
                    mark_notification_read(nid)
                    show_snackbar(page, f"تم تعيين الفني لطلب #{request_id}")
                    page.views.clear()
                    page.views.append(engineer_view())
                    page.update()
            def create_purchase_order(e, request_id=request_id):
                # استرجاع الأصناف غير المتوفرة
                unavailable_parts = execute_query("SELECT part_name FROM SparePartsRequests WHERE request_id = ? AND status = 'unavailable'", (request_id,), fetch=True)
                parts_list = ', '.join([p[0] for p in unavailable_parts]) if unavailable_parts else ""
                if parts_list:
                    add_purchase_order(request_id, parts_list, parts_list)
                    execute_query("INSERT INTO Notifications (request_id, recipient_type, message, created_at) VALUES (?, ?, ?, ?)",
                                 (request_id, "admin", f"طلب شراء جديد #{request_id} للأصناف: {parts_list}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    mark_notification_read(nid)
                    show_snackbar(page, f"تم إنشاء طلب شراء للطلب #{request_id}")
                    page.views.clear()
                    page.views.append(engineer_view())
                    page.update()
            buttons = [
                ft.ElevatedButton("تعيين", on_click=assign) if r[10] == "open" else None,
                ft.ElevatedButton("موافقة على الشراء", on_click=create_purchase_order) if "الأصناف غير المتوفرة" in message else None
            ]
            buttons = [b for b in buttons if b]
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(request_id))),
                        ft.DataCell(ft.Text(message)),
                        ft.DataCell(ft.Text(created_at)),
                        ft.DataCell(technician_dd if r[10] == "open" else ft.Text("تم التعيين" if r[9] else "غير معين")),
                        ft.DataCell(ft.Row(buttons))
                    ]
                )
            )
        table_content = ft.Text("لا توجد إشعارات متاحة للعرض") if not rows else ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("رقم الطلب")),
                ft.DataColumn(ft.Text("الرسالة")),
                ft.DataColumn(ft.Text("التاريخ")),
                ft.DataColumn(ft.Text("الفني")),
                ft.DataColumn(ft.Text("الإجراءات"))
            ],
            rows=rows,
            expand=True
        )
        return ft.View("/engineer", [
            ft.AppBar(actions=[ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)], automatically_imply_leading=False, title=ft.Text("لوحة المهندس", style=ft.TextStyle(weight=ft.FontWeight.BOLD))),
            ft.Container(
                content=ft.Column([
                    ft.Text("الإشعارات", size=20, weight=ft.FontWeight.BOLD),
                    table_content,
                    ft.ElevatedButton("رجوع", icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/"))
                ], scroll=ft.ScrollMode.AUTO, spacing=20),
                padding=20, expand=True
            )
        ])

    # Technician view (Modified to use ListView with Checkboxes)
    def technician_view():
        print("Entering technician_view, fetching data...")  # Debug
        technician_id = page.session.get("technician_id")
        notifications = get_notifications("technician", technician_id)
        print(f"technician_view: Number of notifications = {len(notifications)}")  # Debug
        rows = []
        for n in notifications:
            nid, request_id, _, _, message, created_at, _ = n
            request_data = execute_query("SELECT * FROM MaintenanceRequests WHERE request_id = ?", (request_id,), fetch=True)
            if not request_data:
                continue
            r = request_data[0]
            # إنشاء قائمة قطع الغيار باستخدام ListView و Checkbox
            spare_parts_checkboxes = []
            selected_parts = []
            for part in get_spare_parts():
                part_id, part_name = part
                checkbox = ft.Checkbox(label=part_name, value=False, on_change=lambda e, pn=part_name: selected_parts.append(pn) if e.control.value else selected_parts.remove(pn) if pn in selected_parts else None)
                spare_parts_checkboxes.append(checkbox)
            spare_parts_container = ft.Container(
                content=ft.ListView(
                    controls=spare_parts_checkboxes,
                    height=100,
                    width=200,
                    auto_scroll=True
                ),
                border=ft.border.all(1, ft.Colors.GREY),
                padding=5
            )
            def change_status(e, request_id=request_id, status=None):
                update_request_status(request_id, status)
                mark_notification_read(nid)
                show_snackbar(page, f"تم تحديث حالة الطلب #{request_id} إلى {status}")
                page.views.clear()
                page.views.append(technician_view())
                page.update()
            def request_parts(e, request_id=request_id):
                if not selected_parts:
                    show_snackbar(page, "يرجى اختيار قطعة غيار واحدة على الأقل")
                    return
                request_spare_part(request_id, selected_parts)
                update_request_status(request_id, "waiting")
                mark_notification_read(nid)
                show_snackbar(page, f"تم طلب قطع الغيار للطلب #{request_id}")
                page.views.clear()
                page.views.append(technician_view())
                page.update()
            buttons = []
            if r[10] == "open":
                buttons.append(ft.ElevatedButton("بدء العمل", on_click=lambda e: change_status(e, request_id, "in_progress")))
            elif r[10] == "in_progress":
                buttons.extend([
                    ft.ElevatedButton("إرسال طلب قطعة غيار", on_click=request_parts),
                    ft.ElevatedButton("إغلاق الطلب", on_click=lambda e: change_status(e, request_id, "closed"))
                ])
            elif r[10] == "waiting":
                buttons.append(ft.ElevatedButton("إغلاق الطلب", on_click=lambda e: change_status(e, request_id, "closed")))
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(request_id))),
                        ft.DataCell(ft.Text(message)),
                        ft.DataCell(ft.Text(created_at)),
                        ft.DataCell(spare_parts_container if r[10] == "in_progress" else ft.Text("غير مطلوب")),
                        ft.DataCell(ft.Row(buttons))
                    ]
                )
            )
        table_content = ft.Text("لا توجد إشعارات متاحة للعرض") if not rows else ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("رقم الطلب")),
                ft.DataColumn(ft.Text("الرسالة")),
                ft.DataColumn(ft.Text("التاريخ")),
                ft.DataColumn(ft.Text("قطع الغيار")),
                ft.DataColumn(ft.Text("الإجراءات"))
            ],
            rows=rows,
            expand=True
        )
        return ft.View("/technician", [
            ft.AppBar(actions=[ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)], automatically_imply_leading=False, title=ft.Text("لوحة الفني", style=ft.TextStyle(weight=ft.FontWeight.BOLD))),
            ft.Container(
                content=ft.Column([
                    ft.Text("الإشعارات", size=20, weight=ft.FontWeight.BOLD),
                    table_content,
                    ft.ElevatedButton("رجوع", icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/"))
                ], scroll=ft.ScrollMode.AUTO, spacing=20),
                padding=20, expand=True
            )
        ])

    # Store view
    def store_view():
        print("Entering store_view, fetching data...")  # Debug
        notifications = get_notifications("store")
        print(f"store_view: Number of notifications = {len(notifications)}")  # Debug
        rows = []
        for n in notifications:
            nid, request_id, _, _, message, created_at, _ = n
            spare_requests = get_spare_parts_requests()
            for sr in spare_requests:
                srid, s_request_id, part_name, status = sr
                if s_request_id != request_id:
                    continue
                def update_part_status(e, srid=srid, status=None):
                    update_spare_part_status(srid, status)
                    mark_notification_read(nid)
                    show_snackbar(page, f"تم تحديث حالة قطعة الغيار '{part_name}' إلى {status}")
                    page.views.clear()
                    page.views.append(store_view())
                    page.update()
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(str(request_id))),
                            ft.DataCell(ft.Text(part_name)),
                            ft.DataCell(ft.Text(created_at)),
                            ft.DataCell(ft.Row([
                                ft.ElevatedButton("متوفر", on_click=lambda e: update_part_status(e, srid, "available")),
                                ft.ElevatedButton("غير متوفر", on_click=lambda e: update_part_status(e, srid, "unavailable"))
                            ]))
                        ]
                    )
                )
        table_content = ft.Text("لا توجد طلبات قطع غيار متاحة للعرض") if not rows else ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("رقم الطلب")),
                ft.DataColumn(ft.Text("اسم القطعة")),
                ft.DataColumn(ft.Text("التاريخ")),
                ft.DataColumn(ft.Text("الإجراءات"))
            ],
            rows=rows,
            expand=True
        )
        return ft.View("/store", [
            ft.AppBar(actions=[ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)], automatically_imply_leading=False, title=ft.Text("لوحة المخزن", style=ft.TextStyle(weight=ft.FontWeight.BOLD))),
            ft.Container(
                content=ft.Column([
                    ft.Text("طلبات قطع الغيار", size=20, weight=ft.FontWeight.BOLD),
                    table_content,
                    ft.ElevatedButton("رجوع", icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/"))
                ], scroll=ft.ScrollMode.AUTO, spacing=20),
                padding=20, expand=True
            )
        ])

    # Purchase Orders view
    def purchase_orders_view():
        print("Entering purchase_orders_view, fetching data...")  # Debug
        rows = []
        for po in get_purchase_orders():
            po_id, request_id, part_name, details, created_at, status = po
            def approve_purchase(e, po_id=po_id, request_id=request_id):
                update_purchase_order_status(po_id, "approved", request_id)
                show_snackbar(page, f"تم الموافقة على طلب الشراء #{po_id}")
                page.views.clear()
                page.views.append(purchase_orders_view())
                page.update()
            def reject_purchase(e, po_id=po_id, request_id=request_id):
                update_purchase_order_status(po_id, "rejected", request_id)
                show_snackbar(page, f"تم رفض طلب الشراء #{po_id}")
                page.views.clear()
                page.views.append(purchase_orders_view())
                page.update()
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(po_id))),
                        ft.DataCell(ft.Text(str(request_id))),
                        ft.DataCell(ft.Text(part_name)),
                        ft.DataCell(ft.Text(details)),
                        ft.DataCell(ft.Text(created_at)),
                        ft.DataCell(ft.Text(status)),
                        ft.DataCell(ft.Row([
                            ft.ElevatedButton("إتمام الشراء", on_click=approve_purchase) if status == "pending" else None,
                            ft.ElevatedButton("عدم توفر الشراء", on_click=reject_purchase) if status == "pending" else None
                        ]))
                    ]
                )
            )
        print(f"purchase_orders_view: Number of rows = {len(rows)}")  # Debug
        table_content = ft.Text("لا توجد طلبات شراء متاحة للعرض") if not rows else ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("رقم طلب الشراء")),
                ft.DataColumn(ft.Text("رقم طلب الصيانة")),
                ft.DataColumn(ft.Text("الأصناف")),
                ft.DataColumn(ft.Text("التفاصيل")),
                ft.DataColumn(ft.Text("التاريخ")),
                ft.DataColumn(ft.Text("الحالة")),
                ft.DataColumn(ft.Text("الإجراءات"))
            ],
            rows=[r for r in rows if r.cells[-1].content.controls],
            expand=True
        )
        return ft.View("/purchase_orders", [
            ft.AppBar(actions=[ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)], automatically_imply_leading=False, title=ft.Text("إدارة طلبات الشراء", style=ft.TextStyle(weight=ft.FontWeight.BOLD))),
            ft.Container(
                content=ft.Column([
                    ft.Text("طلبات الشراء", size=20, weight=ft.FontWeight.BOLD),
                    table_content,
                    ft.ElevatedButton("رجوع", icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/"))
                ], scroll=ft.ScrollMode.AUTO, spacing=20),
                padding=20, expand=True
            )
        ])

    # Branch view
    def branch_view():
        print("Entering branch_view, fetching data...")  # Debug
        notifications = get_notifications("requester")
        print(f"branch_view: Number of notifications = {len(notifications)}")  # Debug
        rows = []
        for n in notifications:
            nid, request_id, _, _, message, created_at, _ = n
            def mark_read(e, nid=nid):
                mark_notification_read(nid)
                show_snackbar(page, f"تم تحديد الإشعار #{request_id} كمقروء")
                page.views.clear()
                page.views.append(branch_view())
                page.update()
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(request_id))),
                        ft.DataCell(ft.Text(message)),
                        ft.DataCell(ft.Text(created_at)),
                        ft.DataCell(ft.ElevatedButton("تحديد كمقروء", on_click=mark_read))
                    ]
                )
            )
        table_content = ft.Text("لا توجد إشعارات متاحة للعرض") if not rows else ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("رقم الطلب")),
                ft.DataColumn(ft.Text("الرسالة")),
                ft.DataColumn(ft.Text("التاريخ")),
                ft.DataColumn(ft.Text("الإجراءات"))
            ],
            rows=rows,
            expand=True
        )
        return ft.View("/branch", [
            ft.AppBar(actions=[ft.IconButton(icon=ft.Icons.LOGOUT, on_click=logout)], automatically_imply_leading=False, title=ft.Text("لوحة الفرع", style=ft.TextStyle(weight=ft.FontWeight.BOLD))),
            ft.Container(
                content=ft.Column([
                    ft.Text("الإشعارات", size=20, weight=ft.FontWeight.BOLD),
                    table_content,
                    ft.ElevatedButton("رجوع", icon=ft.Icons.ARROW_BACK, on_click=lambda e: page.go("/"))
                ], scroll=ft.ScrollMode.AUTO, spacing=20),
                padding=20, expand=True
            )
        ])

if __name__ == "__main__":
    ft.app(target=main)