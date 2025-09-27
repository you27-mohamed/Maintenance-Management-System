# 📱 Maintenance Management System - Mobile Web App

<div align="center">

![Maintenance System](https://img.shields.io/badge/Maintenance-System-blue?style=for-the-badge&logo=tools)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green?style=for-the-badge&logo=flask)
![Mobile](https://img.shields.io/badge/Mobile-Optimized-orange?style=for-the-badge&logo=mobile)
![PWA](https://img.shields.io/badge/PWA-Ready-purple?style=for-the-badge&logo=pwa)

**A comprehensive maintenance management system with mobile-first design and Progressive Web App capabilities**

[🚀 Live Demo](#) | [📱 Install as App](#mobile-installation) | [📖 Documentation](DEPLOYMENT_GUIDE.md)

</div>

## 🌟 Features

### 📱 **Mobile-First Design**
- **Responsive UI**: Perfect on phones, tablets, and desktops
- **Progressive Web App**: Install like a native mobile app
- **Touch-Optimized**: Large buttons and gesture support
- **Offline Support**: Basic functionality without internet

### 🔐 **Multi-User System**
- **Role-Based Access**: Admin, Engineer, Technician, Store, Branch
- **Secure Authentication**: Session-based login system
- **Permission Control**: Different features per user role

### 🛠️ **Core Functionality**
- **Maintenance Requests**: Create, track, and manage requests
- **Technician Assignment**: Assign tasks to specific technicians
- **Status Tracking**: Real-time updates (Open → In Progress → Closed)
- **Notifications**: Dashboard alerts for all user types
- **Reporting**: Export Excel reports with filtering
- **Data Management**: Manage branches, equipment, fault types

## 🚀 Quick Start

### 🌐 **Option 1: Deploy to Web (Recommended)**

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
[![Deploy to Railway](https://railway.app/button.svg)](https://railway.app/new/template)

### 💻 **Option 2: Run Locally**

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/maintenance-management-system.git
cd maintenance-management-system

# Install dependencies
pip install -r requirements.txt

# Run the application
python web_app.py

# Access at http://localhost:8080
```

### 📱 **Option 3: One-Click Deploy**

```bash
# Run the automated deployment script
./deploy.sh
```

## 👥 **Default User Accounts**

| Username | Password | Role | Access Level |
|----------|----------|------|-------------|
| `admin` | `pass123` | Administrator | Full system access |
| `engineer` | `pass123` | Engineer | Create requests, assign technicians, reports |
| `technician` | `pass123` | Technician | View tasks, update status |
| `store` | `pass123` | Store Manager | Manage spare parts inventory |
| `branch` | `pass123` | Branch User | Create requests for branch |

> ⚠️ **Security Note**: Change these passwords in production!

## 📱 **Mobile Installation**

Your app can be installed on mobile devices like a native app:

### **iPhone/iPad (iOS Safari):**
1. Open the web app in Safari
2. Tap the Share button (square with arrow)
3. Scroll down and tap "Add to Home Screen"
4. Tap "Add" to install

### **Android (Chrome):**
1. Open the web app in Chrome
2. Tap the menu (three dots)
3. Tap "Add to Home Screen" or "Install App"
4. Tap "Add" to install

### **Desktop (Chrome/Edge):**
1. Look for the install icon in the address bar
2. Click "Install" when prompted
3. The app will open in its own window

## 🎨 **Screenshots**

<div align="center">

### Mobile Interface
<img src="docs/mobile-login.png" width="250" alt="Mobile Login"> <img src="docs/mobile-dashboard.png" width="250" alt="Mobile Dashboard"> <img src="docs/mobile-requests.png" width="250" alt="Mobile Requests">

### Desktop Interface
<img src="docs/desktop-dashboard.png" width="800" alt="Desktop Dashboard">

</div>

## 🏗️ **Architecture**

### **Backend**
- **Framework**: Flask 2.3.3
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **Session Management**: Flask-Session
- **Export**: Pandas + OpenPyXL for Excel reports

### **Frontend**
- **UI Framework**: Bootstrap 5 (Mobile-first)
- **Icons**: FontAwesome 6
- **PWA**: Service Worker + Web Manifest
- **Language**: Arabic RTL support

### **Deployment**
- **Containerized**: Docker support
- **Cloud Ready**: Heroku, Railway, Render compatible
- **CI/CD**: GitHub Actions workflows
- **Monitoring**: Built-in statistics and logging

## 📊 **Database Schema**

The system includes these main tables:
- `MaintenanceRequests` - Core request data
- `Users` - Authentication and roles
- `Technicians` - Technician information
- `Notifications` - System alerts
- `Branches` - Location management
- `SpareParts` - Inventory tracking

## 🛡️ **Security Features**

- **Session Security**: Secure user sessions
- **Role Validation**: Server-side permission checks
- **Input Sanitization**: Protected against injection attacks
- **HTTPS Ready**: SSL/TLS support
- **Environment Variables**: Secure configuration

## 📈 **Performance**

- **Fast Loading**: Optimized for mobile networks
- **Caching**: Service worker caches resources
- **Responsive**: Smooth animations and transitions
- **Scalable**: Handles multiple concurrent users

## 🌍 **Internationalization**

- **Arabic Interface**: Full RTL (Right-to-Left) support
- **English Documentation**: Code and comments in English
- **Extensible**: Easy to add more languages

## 🔧 **Development**

### **Setup Development Environment**

```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/maintenance-management-system.git
cd maintenance-management-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
export FLASK_ENV=development
python web_app.py
```

### **Project Structure**

```
maintenance-management-system/
├── web_app.py              # Main Flask application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── Procfile               # Heroku deployment
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── login.html        # Login page
│   ├── dashboard.html    # Main dashboard
│   └── ...               # Other pages
├── static/               # Static assets
│   ├── manifest.json     # PWA manifest
│   ├── sw.js            # Service worker
│   └── icons/           # App icons
├── .github/workflows/    # CI/CD configurations
└── docs/                # Documentation
```

## 🚀 **Deployment Options**

### **Free Hosting Platforms**

| Platform | Setup Time | Features | URL Format |
|----------|------------|----------|------------|
| **Heroku** | 5 minutes | Auto-deploy, Add-ons | `app-name.herokuapp.com` |
| **Railway** | 3 minutes | Modern UI, Fast | `app-name.railway.app` |
| **Render** | 5 minutes | Free SSL, CDN | `app-name.onrender.com` |
| **GitHub Codespaces** | 2 minutes | Development | `codespace-url.github.dev` |

### **Production Hosting**

For production use with custom domains:
- **DigitalOcean App Platform**
- **AWS Elastic Beanstalk**
- **Google Cloud Run**
- **Azure Web Apps**

## 📚 **Documentation**

- [📖 **Deployment Guide**](DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [🌐 **Web App README**](WEB_APP_README.md) - Technical documentation
- [💻 **Original Desktop App**](README.md) - Flet desktop version
- [🔧 **API Documentation**](docs/API.md) - REST API endpoints

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Email**: your.email@domain.com

## 🎯 **Roadmap**

- [ ] **Real-time notifications** with WebSocket
- [ ] **File attachments** for maintenance requests
- [ ] **GPS location** tracking for mobile technicians
- [ ] **Barcode scanning** for equipment identification
- [ ] **Multi-language** support (English, French, etc.)
- [ ] **Advanced reporting** with charts and analytics
- [ ] **API integration** with external systems
- [ ] **Mobile app** (React Native/Flutter)

## 🏆 **Acknowledgments**

- **Flask Community** for the excellent web framework
- **Bootstrap Team** for the responsive UI components
- **FontAwesome** for the beautiful icons
- **Contributors** who help improve this project

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

[![GitHub Stars](https://img.shields.io/github/stars/YOUR_USERNAME/maintenance-management-system?style=social)](../../stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/YOUR_USERNAME/maintenance-management-system?style=social)](../../network/members)

**Made with ❤️ for maintenance teams worldwide**

</div>