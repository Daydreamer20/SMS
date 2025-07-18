# Production deployment script for Windows
param(
    [string]$Environment = "production",
    [switch]$Build = $false,
    [switch]$HealthCheck = $false
)

Write-Host "🚀 Starting production deployment..." -ForegroundColor Green

# Set error action preference
$ErrorActionPreference = "Stop"

# Configuration
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DockerComposeFile = "$ProjectRoot\docker-compose.prod.yml"
$EnvFile = "$ProjectRoot\.env.production"

# Check if environment file exists
if (-not (Test-Path $EnvFile)) {
    Write-Host "❌ Environment file not found: $EnvFile" -ForegroundColor Red
    Write-Host "Please create the .env.production file with required variables." -ForegroundColor Yellow
    exit 1
}

# Load environment variables
Write-Host "📋 Loading environment variables..." -ForegroundColor Blue
Get-Content $EnvFile | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

# Build images if requested
if ($Build) {
    Write-Host "🔨 Building production images..." -ForegroundColor Blue
    docker-compose -f $DockerComposeFile build --no-cache
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Build failed!" -ForegroundColor Red
        exit 1
    }
}

# Stop existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Blue
docker-compose -f $DockerComposeFile down

# Start services
Write-Host "🚀 Starting production services..." -ForegroundColor Blue
docker-compose -f $DockerComposeFile up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

# Wait for services to be ready
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Blue
Start-Sleep -Seconds 30

# Health check if requested
if ($HealthCheck) {
    Write-Host "🏥 Running health checks..." -ForegroundColor Blue
    
    # Check backend health
    try {
        $backendHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
        if ($backendHealth.status -eq "healthy") {
            Write-Host "✅ Backend is healthy" -ForegroundColor Green
        } else {
            Write-Host "❌ Backend health check failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Backend is not responding" -ForegroundColor Red
    }
    
    # Check frontend
    try {
        $frontendResponse = Invoke-WebRequest -Uri "http://localhost:80/health" -TimeoutSec 10
        if ($frontendResponse.StatusCode -eq 200) {
            Write-Host "✅ Frontend is healthy" -ForegroundColor Green
        } else {
            Write-Host "❌ Frontend health check failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Frontend is not responding" -ForegroundColor Red
    }
}

# Show running containers
Write-Host "📊 Running containers:" -ForegroundColor Blue
docker-compose -f $DockerComposeFile ps

Write-Host "🎉 Production deployment completed!" -ForegroundColor Green
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:80" -ForegroundColor Cyan
Write-Host "Health Check: http://localhost:8000/health" -ForegroundColor Cyan