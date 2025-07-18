# Railway Deployment Script for SMS Application
Write-Host "🚀 Deploying SMS Application to Railway..." -ForegroundColor Green

# Check if Railway CLI is installed
if (!(Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Railway CLI not found. Installing..." -ForegroundColor Yellow
    Write-Host "Please install Railway CLI first:"
    Write-Host "npm install -g @railway/cli" -ForegroundColor Cyan
    Write-Host "or"
    Write-Host "curl -fsSL https://railway.app/install.sh | sh" -ForegroundColor Cyan
    exit 1
}

Write-Host "✅ Railway CLI found" -ForegroundColor Green

# Login to Railway (if not already logged in)
Write-Host "🔐 Checking Railway authentication..." -ForegroundColor Blue
railway whoami
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please login to Railway:" -ForegroundColor Yellow
    railway login
}

# Create new Railway project
Write-Host "📦 Creating Railway project..." -ForegroundColor Blue
railway project new

# Deploy PostgreSQL Database
Write-Host "🗄️ Setting up PostgreSQL database..." -ForegroundColor Blue
railway add --database postgresql

# Set environment variables for the project
Write-Host "⚙️ Setting up environment variables..." -ForegroundColor Blue
Write-Host "You'll need to set these environment variables in Railway dashboard:" -ForegroundColor Yellow
Write-Host "- JWT_SECRET_KEY" -ForegroundColor Cyan
Write-Host "- CORS_ORIGINS" -ForegroundColor Cyan
Write-Host "- ENVIRONMENT=production" -ForegroundColor Cyan
Write-Host "- DEBUG=False" -ForegroundColor Cyan

# Deploy Backend
Write-Host "🔧 Deploying Backend..." -ForegroundColor Blue
Set-Location sms/backend
railway up --detach
Set-Location ../..

# Deploy Frontend
Write-Host "🎨 Deploying Frontend..." -ForegroundColor Blue
Set-Location sms/frontend
railway up --detach
Set-Location ../..

Write-Host "🎉 Deployment initiated! Check Railway dashboard for status." -ForegroundColor Green
Write-Host "🌐 Your services will be available at:" -ForegroundColor Blue
Write-Host "- Backend: https://your-backend-service.railway.app" -ForegroundColor Cyan
Write-Host "- Frontend: https://your-frontend-service.railway.app" -ForegroundColor Cyan

Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Set environment variables in Railway dashboard" -ForegroundColor White
Write-Host "2. Update CORS_ORIGINS with your frontend URL" -ForegroundColor White
Write-Host "3. Update REACT_APP_API_URL in frontend with backend URL" -ForegroundColor White