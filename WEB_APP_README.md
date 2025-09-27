# 📱 Maintenance Management Web App

A modern, mobile-friendly web application for maintenance management, converted from the original Flet desktop application (`14-9.py`). This responsive web app provides the same functionality with enhanced mobile support and Progressive Web App (PWA) capabilities.

## 🌟 Features

### 📱 Mobile-First Design
- **Responsive UI**: Optimized for mobile devices, tablets, and desktops
- **Touch-Friendly**: Large buttons and touch-optimized interface
- **Progressive Web App**: Installable on mobile devices like a native app
- **Offline Support**: Service worker for basic offline functionality
- **Mobile Navigation**: Bottom navigation bar for easy thumb navigation

### 🔐 User Authentication & Roles
- **Multi-Role System**: Admin, Engineer, Technician, Store, Branch
- **Session Management**: Secure user sessions with Flask-Session
- **Role-Based Access**: Different dashboards and permissions per role

### 🛠️ Core Functionality
- **Maintenance Requests**: Create, view, and manage maintenance requests
- **Technician Assignment**: Assign technicians to specific tasks
- **Status Tracking**: Real-time status updates (Open, In Progress, Waiting, Closed)
- **Notifications**: Dashboard notifications for each user role
- **Reporting**: Generate and export Excel reports
- **Data Management**: Manage branches, equipment, fault types, etc.

### 📊 Dashboard Features
- **Quick Statistics**: Real-time counters for different request statuses
- **Role-Specific Dashboards**: Customized interface for each user type
- **Quick Actions**: Fast access to frequently used functions
- **Visual Status Indicators**: Color-coded badges and cards

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Quick Start
```bash
# Navigate to project directory
cd /Users/yousseffadel/Documents/mohamed_fadel

# Activate virtual environment (if not already active)
source .venv/bin/activate

# Install required packages (already installed)
# pip install flask flask-session pandas openpyxl

# Run the web application
python web_app.py
```

### Access the Application
- **Local Access**: http://127.0.0.1:8080
- **Network Access**: http://192.168.1.10:8080 (accessible from other devices on your network)
- **Mobile Access**: Use the network IP to access from mobile devices

## 📱 Mobile Installation (PWA)

### On Mobile Browsers:
1. Open the web app in your mobile browser
2. Look for "Add to Home Screen" or install prompt
3. Tap "Install" or "Add"
4. The app will be installed like a native mobile app

### Features as PWA:
- **Home Screen Icon**: Apps appears on home screen
- **Full Screen**: Runs without browser UI
- **Offline Support**: Basic offline functionality
- **Native Feel**: Behaves like a native mobile app

## 👥 Default User Accounts

| Username   | Password | Role       | Description |
|------------|----------|------------|-------------|
| admin      | pass123  | Admin      | Full system access |
| engineer   | pass123  | Engineer   | Create requests, assign technicians, reports |
| technician | pass123  | Technician | View assigned tasks, update status |
| store      | pass123  | Store      | Manage spare parts inventory |
| branch     | pass123  | Branch     | Create requests for branch |

## 🎨 User Interface

### Mobile-Optimized Design
- **Bootstrap 5**: Modern, responsive framework
- **RTL Support**: Right-to-left layout for Arabic interface
- **Touch Targets**: Appropriately sized touch targets (44px minimum)
- **Readable Fonts**: Optimized font sizes for mobile screens
- **High Contrast**: Accessible color schemes

### Navigation
- **Desktop**: Top navigation with dropdown menus
- **Mobile**: Fixed bottom navigation bar with icons
- **Quick Access**: Dashboard cards for main functions
- **Breadcrumbs**: Clear navigation hierarchy

## 🔧 Technical Architecture

### Backend (Flask)
- **Framework**: Flask web framework
- **Database**: SQLite (same as original app)
- **Session Management**: Flask-Session
- **Templates**: Jinja2 templating engine
- **Static Files**: CSS, JS, PWA assets

### Frontend
- **CSS Framework**: Bootstrap 5
- **Icons**: FontAwesome 6
- **JavaScript**: Vanilla JS for interactivity
- **PWA**: Service Worker for offline support

### Database
- **Same Schema**: Uses identical database schema as original app
- **Data Compatibility**: Fully compatible with existing data
- **Automatic Initialization**: Creates and seeds database on first run

## 📱 Mobile-Specific Features

### Touch Interactions
- **Swipe Gestures**: Natural mobile navigation
- **Long Press**: Context actions where appropriate
- **Pull to Refresh**: Refresh data with pull gesture
- **Touch Feedback**: Visual feedback for all interactions

### Performance
- **Lazy Loading**: Images and content loaded as needed
- **Caching**: Service worker caches resources
- **Compression**: Optimized assets for mobile bandwidth
- **Fast Loading**: Minimal initial payload

## 🛡️ Security Features

- **Session Security**: Secure session management
- **Role Validation**: Server-side role checking
- **CSRF Protection**: Protected forms
- **Input Validation**: Sanitized user inputs
- **SQL Injection Protection**: Parameterized queries

## 📈 Monitoring & Analytics

### Built-in Statistics
- **Request Counters**: Real-time statistics
- **Status Distribution**: Visual breakdown of request statuses
- **Performance Metrics**: Response time monitoring
- **User Activity**: Track user interactions

## 🔄 API Endpoints

- `GET /` - Dashboard
- `GET /login` - Login page
- `POST /login` - Authentication
- `GET /create_request` - Create request form
- `POST /create_request` - Submit new request
- `GET /requests` - View all requests
- `GET /engineer` - Engineer dashboard
- `GET /technician` - Technician dashboard
- `POST /assign_technician` - Assign technician to request
- `POST /update_status` - Update request status
- `GET /report` - Reports dashboard
- `GET /api/stats` - Statistics API

## 🚀 Deployment Options

### Development Server (Current)
```bash
python web_app.py
# Access at http://127.0.0.1:8080
```

### Production Deployment (Recommended)
```bash
# Using Gunicorn
pip install gunicorn
gunicorn --bind 0.0.0.0:8080 web_app:app

# Using uWSGI
pip install uwsgi
uwsgi --http 0.0.0.0:8080 --wsgi-file web_app.py --callable app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "web_app:app"]
```

## 📱 Mobile Testing

### Testing on Physical Devices
1. Ensure your computer and mobile device are on the same network
2. Use the network IP address: http://192.168.1.10:8080
3. Test all functions on various screen sizes
4. Test PWA installation process

### Browser Developer Tools
1. Open Chrome DevTools
2. Toggle Device Toolbar (Ctrl/Cmd + Shift + M)
3. Test various device sizes and orientations
4. Test touch interactions and PWA features

## 🔧 Customization

### Styling
- Edit `/static/` files for custom CSS
- Modify Bootstrap variables for theme changes
- Update colors in `base.html` style section

### Features
- Add new routes in `web_app.py`
- Create new templates in `/templates/`
- Extend database functions as needed

## 🐛 Troubleshooting

### Common Issues
1. **Port Already in Use**: Change port in `web_app.py`
2. **Database Errors**: Delete `maintenance.db` to reset
3. **Template Errors**: Check file paths and template syntax
4. **Mobile Display Issues**: Test CSS media queries

### Debug Mode
The app runs in debug mode by default:
- Automatic reloading on code changes
- Detailed error messages
- Debug toolbar available

## 📞 Support

For issues related to:
- **Original App**: Reference `14-9.py` documentation
- **Web App**: Check Flask and Bootstrap documentation
- **Mobile Issues**: Test on actual devices and browsers
- **PWA Features**: Verify manifest.json and service worker

## 🔄 Migration from Desktop App

### Data Compatibility
- Uses same SQLite database
- Identical user accounts and roles
- Same business logic and workflows

### Feature Parity
- All original features implemented
- Enhanced mobile user experience
- Additional web-specific features

### Migration Steps
1. Backup existing `maintenance.db`
2. Run web app (uses same database)
3. Test all functionality
4. Train users on web interface

---

**🎯 Your maintenance management system is now available as a modern, mobile-friendly web application!**

Access it at: **http://127.0.0.1:8080** or **http://192.168.1.10:8080**