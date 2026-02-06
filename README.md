# 🔧 Maintenance Management System

A comprehensive mobile-ready maintenance management web application converted from desktop to web platform.

## 🌟 **Web Application Features**
- 📱 **Mobile-First Responsive Design**
- 🌐 **PWA (Progressive Web App) - Installable on Mobile**
- 🔄 **Arabic RTL Support**
- 🔐 **Role-Based Access Control (5 Roles)**
- 📊 **Real-time Statistics Dashboard**
- 📋 **Complete Maintenance Management**
- 📈 **Data Export to Excel**
- 🚀 **Deployed on GitHub & Ready for Cloud**

## 🚀 **Quick Start**

### **Run Locally**
```bash
# Activate virtual environment
source .venv/bin/activate

# Run the web application
python web_app.py
```
**Access:** http://localhost:5000 or http://192.168.1.10:5000

### **Database Setup (First Run)**
```bash
# Create tables
flask --app web_app.py init-db

# Optional: load sample data
flask --app web_app.py seed-db
```

### **Production Environment Variables**
```
SECRET_KEY=your-strong-secret
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SESSION_TYPE=filesystem
```

### **Deploy to Cloud**
```bash
# Deploy using automated script
./deploy.sh
```

## 🔑 **Login Credentials**
| Username | Password | Role | Access |
|----------|----------|------|--------|
| admin | pass123 | Admin | Full Access |
| engineer | pass123 | Engineer | Engineering |
| technician | pass123 | Technician | Maintenance |
| store | pass123 | Store | Parts Management |
| branch | pass123 | Branch | Branch Operations |

## 📱 **Mobile Access**
1. **Visit the web app URL** on any mobile device
2. **Tap "Add to Home Screen"** for PWA installation
3. **Use like a native app** with offline support

## 🏗️ **Project Structure**
```
maintenance-management-system/
├── web_app.py              # Main Flask application
├── maintenance.db          # SQLite database
├── templates/              # HTML templates
│   ├── base.html          # Base template with PWA
│   ├── login.html         # Login page
│   ├── dashboard.html     # Role-based dashboards
│   └── [other pages]      # Feature pages
├── static/                # PWA assets
│   ├── manifest.json      # PWA manifest
│   ├── sw.js             # Service worker
│   └── [icons]           # App icons
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── Procfile             # Heroku deployment
└── deploy.sh            # Automated deployment
```

## 🗄️ **Database Schema**
- **12 Tables:** MaintenanceRequests, Users, Technicians, Parts, WorkOrders, etc.
- **Sample Data:** 12 requests, 15 technicians, 20 parts, 5 users
- **SQLite:** Lightweight, portable database

## 🌐 **Deployment Options**
- ✅ **GitHub:** https://github.com/you27-mohamed/Maintenance-Management-System
- 🚀 **Railway:** Instant deployment
- 🆓 **Render:** Free hosting
- ☁️ **Heroku:** Scalable platform
- 🐳 **Docker:** Containerized deployment

## 🔧 **Technologies Used**
- **Backend:** Python Flask 2.3.3
- **Frontend:** Bootstrap 5, PWA
- **Database:** SQLite
- **Deployment:** Docker, Gunicorn
- **Mobile:** Responsive design, Service Worker

---
**GitHub Repository:** https://github.com/you27-mohamed/Maintenance-Management-System  
**Status:** ✅ Production Ready | 📱 Mobile Optimized | 🌍 Globally Deployable