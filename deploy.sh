#!/bin/bash

# Maintenance Management System - Simple Deployment Script
# Clean and automated deployment for web application

# Colors and emojis
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying Maintenance Management System${NC}"
echo "=============================================="

# Git operations
echo -e "${YELLOW}📦 Preparing for deployment...${NC}"
git add .
git status

# Simple commit
read -p "💬 Commit message (or Enter for 'Update app'): " msg
msg=${msg:-"Update maintenance management app"}
git commit -m "$msg" || echo "Nothing to commit"

# GitHub push
if git remote get-url origin >/dev/null 2>&1; then
    echo -e "${YELLOW}📤 Pushing to GitHub...${NC}"
    git push origin main
    echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
    
    # Show repository URL
    repo_url=$(git remote get-url origin)
    echo -e "${GREEN}🔗 Repository: $repo_url${NC}"
else
    echo -e "${YELLOW}⚠️ No GitHub remote found. Add with:${NC}"
    echo "git remote add origin https://github.com/USERNAME/REPO.git"
fi

# Quick deployment options
echo -e "${BLUE}"
echo "🌐 Quick Deploy Options:"
echo "1. 🚂 Railway: https://railway.app (Deploy from GitHub)"
echo "2. 🆓 Render: https://render.com (Free hosting)"
echo "3. ☁️ Codespaces: Go to GitHub → Code → Codespaces"
echo ""
echo "📱 Mobile Access: Share the deployed URL"
echo "🔑 Login: admin/pass123, engineer/pass123, etc."
echo -e "${NC}"

echo -e "${GREEN}✅ Deployment preparation complete! 🎉${NC}"