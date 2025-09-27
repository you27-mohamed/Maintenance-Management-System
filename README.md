# Maintenance Management System (نظام إدارة الصيانة)

A comprehensive maintenance management system built with Python, Flet, and SQLite. This application provides a complete solution for managing maintenance requests, technicians, spare parts, and purchase orders in Arabic.

## Features

### 🔐 User Authentication
- Multi-role authentication system (Admin, Engineer, Technician, Store, Branch)
- Role-based access control with different dashboards

### 👥 User Roles
- **Admin**: Full system access, user management, technician management
- **Engineer**: Create requests, assign technicians, manage purchase orders
- **Technician**: View assigned tasks, update status, request spare parts
- **Store**: Manage spare parts availability
- **Branch**: Create requests and view notifications

### 🛠️ Core Functionality
- **Maintenance Requests**: Create, track, and manage maintenance requests
- **Technician Assignment**: Assign technicians to specific maintenance tasks
- **Spare Parts Management**: Request and track spare parts availability
- **Purchase Orders**: Create and approve purchase orders for unavailable parts
- **Notifications System**: Real-time notifications for all stakeholders
- **Reporting**: Generate and export maintenance reports to Excel

### 📊 Data Management
- Branch management
- Maintenance types
- Equipment names
- Fault types
- Spare parts catalog
- User and technician management

## Technical Stack

- **Frontend**: Flet (Python GUI framework based on Flutter)
- **Backend**: Python with SQLite
- **Database**: SQLite with comprehensive schema
- **Export**: Pandas for Excel report generation
- **UI Language**: Arabic (RTL support)

## Database Schema

The system includes the following main tables:
- `MaintenanceRequests`: Core maintenance request data
- `Technicians`: Technician information and branch assignment
- `SparePartsRequests`: Spare parts requests
- `Notifications`: System notifications
- `PurchaseOrders`: Purchase order management
- `Users`: User authentication and roles
- `Branches`, `MaintenanceTypes`, `EquipmentNames`, `FaultTypes`, `SpareParts`: Master data

## Default Users

The system comes with pre-configured users:
- **admin** / pass123 (Administrator)
- **engineer** / pass123 (Engineer)
- **technician** / pass123 (Technician)
- **store** / pass123 (Store Manager)
- **branch** / pass123 (Branch User)

## Installation

1. Clone or download the project
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install required packages:
   ```bash
   pip install flet pandas openpyxl
   ```
4. Run the application:
   ```bash
   python 14-9.py
   ```

## Usage

1. Launch the application
2. Login with one of the default users
3. Navigate through the different modules based on your role
4. Create maintenance requests, assign technicians, manage spare parts, etc.

## Features by Role

### Admin Dashboard
- User management (create, edit, delete users)
- Technician management
- Master data management (branches, equipment, fault types, etc.)
- Full system access

### Engineer Dashboard
- Create maintenance requests
- View and respond to notifications
- Assign technicians to requests
- Manage purchase orders
- Generate reports

### Technician Dashboard
- View assigned maintenance tasks
- Update task status (start, in progress, complete)
- Request spare parts
- Close completed tasks

### Store Dashboard
- View spare parts requests
- Update parts availability (available/unavailable)
- Manage inventory status

### Branch Dashboard
- Create maintenance requests for their branch
- View notifications about request status

## Export Functionality

- Generate Excel reports of maintenance requests
- Filter reports by status and branch
- Export includes all request details and timestamps

## Database

The application automatically creates and initializes the SQLite database (`maintenance.db`) on first run with sample data including:
- Default branches (Main Branch, Secondary Branch)
- Sample technicians
- Basic maintenance types and equipment
- Default user accounts

## Notes

- The application uses Arabic text with RTL (Right-to-Left) layout
- All timestamps are automatically managed
- The system includes comprehensive notification management
- Excel export requires the `openpyxl` package
- The database file will be created in the same directory as the script