#!/bin/bash

# 🚀 One-Click Deployment Script for Maintenance Management System
# This script helps you deploy your app to GitHub and hosting platforms

echo "🚀 Maintenance Management System - Deployment Script"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "web_app.py" ]; then
    print_error "web_app.py not found. Please run this script from the project directory."
    exit 1
fi

print_info "Starting deployment process..."

# Step 1: Initialize Git repository (if not already done)
if [ ! -d ".git" ]; then
    print_info "Initializing Git repository..."
    git init
    print_status "Git repository initialized"
else
    print_status "Git repository already exists"
fi

# Step 2: Add and commit files
print_info "Adding files to Git..."
git add .
git status

echo
read -p "📝 Enter commit message (or press Enter for default): " commit_message
if [ -z "$commit_message" ]; then
    commit_message="Deploy: Maintenance Management System"
fi

git commit -m "$commit_message"
print_status "Files committed to Git"

# Step 3: Ask for GitHub repository URL
echo
print_info "GitHub Repository Setup"
echo "Please create a repository on GitHub first: https://github.com/new"
echo
read -p "🔗 Enter your GitHub repository URL (e.g., https://github.com/username/repo.git): " repo_url

if [ -n "$repo_url" ]; then
    # Remove existing origin if it exists
    git remote remove origin 2>/dev/null || true
    
    # Add new origin
    git remote add origin "$repo_url"
    
    # Push to GitHub
    print_info "Pushing to GitHub..."
    git branch -M main
    
    if git push -u origin main; then
        print_status "Code pushed to GitHub successfully!"
        
        # Extract username and repo name for later use
        username=$(echo "$repo_url" | sed -n 's/.*github\.com[/:]\([^/]*\)\/.*/\1/p')
        repo_name=$(echo "$repo_url" | sed -n 's/.*\/\([^.]*\)\.git.*/\1/p')
        
        if [ -z "$repo_name" ]; then
            repo_name=$(echo "$repo_url" | sed -n 's/.*\/\([^/]*\)\/?$/\1/p')
        fi
        
        print_status "Repository: https://github.com/$username/$repo_name"
    else
        print_error "Failed to push to GitHub. Please check your repository URL and permissions."
    fi
else
    print_warning "Skipping GitHub push. You can do this manually later."
fi

# Step 4: Deployment options
echo
print_info "🌐 Deployment Options"
echo "1. Heroku (Free tier available)"
echo "2. Railway (Modern platform)"
echo "3. Render (Free hosting)"
echo "4. GitHub Codespaces (Development)"
echo "5. Skip deployment for now"
echo

read -p "Choose deployment option (1-5): " deploy_option

case $deploy_option in
    1)
        print_info "🚀 Heroku Deployment"
        echo "Follow these steps:"
        echo "1. Install Heroku CLI: https://devcenter.heroku.com/articles/heroku-cli"
        echo "2. Run: heroku login"
        echo "3. Run: heroku create your-app-name"
        echo "4. Run: heroku config:set SECRET_KEY=\"$(openssl rand -base64 32)\""
        echo "5. Run: git push heroku main"
        echo "6. Run: heroku open"
        echo
        echo "Your app will be available at: https://your-app-name.herokuapp.com"
        ;;
    2)
        print_info "🚀 Railway Deployment"
        echo "Follow these steps:"
        echo "1. Go to: https://railway.app"
        echo "2. Sign up with GitHub"
        echo "3. Click 'New Project' → 'Deploy from GitHub repo'"
        echo "4. Select your repository: $username/$repo_name"
        echo "5. Railway will automatically deploy your app"
        echo
        echo "Your app will be available at: https://your-app-name.railway.app"
        ;;
    3)
        print_info "🚀 Render Deployment"
        echo "Follow these steps:"
        echo "1. Go to: https://render.com"
        echo "2. Sign up with GitHub"
        echo "3. Click 'New +' → 'Web Service'"
        echo "4. Connect your repository: $username/$repo_name"
        echo "5. Configure:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: gunicorn web_app:app"
        echo "6. Click 'Create Web Service'"
        echo
        echo "Your app will be available at: https://your-app-name.onrender.com"
        ;;
    4)
        print_info "🚀 GitHub Codespaces"
        echo "Follow these steps:"
        echo "1. Go to your GitHub repository"
        echo "2. Click 'Code' → 'Codespaces' → 'Create codespace on main'"
        echo "3. Wait for the environment to load"
        echo "4. In the terminal, run: python web_app.py"
        echo "5. Click 'Open in Browser' when prompted"
        echo "6. Share the URL for mobile access"
        ;;
    5)
        print_info "Deployment skipped. You can deploy later using the DEPLOYMENT_GUIDE.md"
        ;;
    *)
        print_warning "Invalid option. Please run the script again."
        ;;
esac

# Step 5: Final instructions
echo
print_status "🎉 Deployment script completed!"
echo
print_info "📱 Mobile Access Instructions:"
echo "1. Once deployed, your app will have a public URL"
echo "2. Share this URL with mobile users"
echo "3. Users can install it as a PWA (Add to Home Screen)"
echo "4. Default login credentials:"
echo "   - admin / pass123"
echo "   - engineer / pass123"
echo "   - technician / pass123"
echo "   - store / pass123"
echo "   - branch / pass123"
echo
print_info "📚 Documentation:"
echo "- Deployment Guide: DEPLOYMENT_GUIDE.md"
echo "- Web App README: WEB_APP_README.md"
echo "- Original README: README.md"
echo
print_info "🔧 Next Steps:"
echo "1. Test your deployed application"
echo "2. Update user credentials for security"
echo "3. Configure custom domain (optional)"
echo "4. Set up monitoring and backups"
echo

print_status "Happy deploying! 🚀"