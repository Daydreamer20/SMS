# Database backup script for production
param(
    [string]$BackupType = "full",  # full, incremental
    [string]$RetentionDays = "30",
    [switch]$Compress = $true
)

# Configuration
$BackupDir = "backups"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogFile = "$BackupDir\backup_$Timestamp.log"

# Create backup directory if it doesn't exist
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force
}

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $LogEntry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

Write-Log "Starting backup process - Type: $BackupType"

# Load environment variables
$EnvFile = ".env.production"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
} else {
    Write-Log "Environment file not found: $EnvFile" "ERROR"
    exit 1
}

# Database backup
$DbHost = $env:DB_HOST
$DbPort = $env:DB_PORT
$DbUser = $env:DB_USER
$DbName = $env:DB_NAME
$DbPassword = $env:DB_PASSWORD

$BackupFileName = "$BackupDir\sms_db_backup_$Timestamp.sql"

Write-Log "Creating database backup: $BackupFileName"

# Set PGPASSWORD environment variable
$env:PGPASSWORD = $DbPassword

try {
    # Create database dump
    $pgDumpArgs = @(
        "--host=$DbHost",
        "--port=$DbPort",
        "--username=$DbUser",
        "--dbname=$DbName",
        "--verbose",
        "--clean",
        "--no-owner",
        "--no-privileges",
        "--file=$BackupFileName"
    )
    
    & pg_dump @pgDumpArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Database backup completed successfully"
        
        # Compress backup if requested
        if ($Compress) {
            Write-Log "Compressing backup file"
            Compress-Archive -Path $BackupFileName -DestinationPath "$BackupFileName.zip" -Force
            Remove-Item $BackupFileName
            $BackupFileName = "$BackupFileName.zip"
            Write-Log "Backup compressed: $BackupFileName"
        }
        
        # Get backup file size
        $BackupSize = (Get-Item $BackupFileName).Length
        $BackupSizeMB = [math]::Round($BackupSize / 1MB, 2)
        Write-Log "Backup size: $BackupSizeMB MB"
        
    } else {
        Write-Log "Database backup failed with exit code: $LASTEXITCODE" "ERROR"
        exit 1
    }
} catch {
    Write-Log "Database backup failed: $($_.Exception.Message)" "ERROR"
    exit 1
} finally {
    # Clear password from environment
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
}

# Application files backup
Write-Log "Creating application files backup"
$AppBackupFile = "$BackupDir\sms_app_backup_$Timestamp.zip"

try {
    $FilesToBackup = @(
        ".env.production",
        "docker-compose.prod.yml",
        "logs",
        "docker\nginx",
        "docker\postgres"
    )
    
    $ExistingFiles = $FilesToBackup | Where-Object { Test-Path $_ }
    
    if ($ExistingFiles.Count -gt 0) {
        Compress-Archive -Path $ExistingFiles -DestinationPath $AppBackupFile -Force
        Write-Log "Application files backup completed: $AppBackupFile"
    } else {
        Write-Log "No application files found to backup" "WARNING"
    }
} catch {
    Write-Log "Application files backup failed: $($_.Exception.Message)" "ERROR"
}

# Cleanup old backups
Write-Log "Cleaning up old backups (retention: $RetentionDays days)"
$CutoffDate = (Get-Date).AddDays(-[int]$RetentionDays)

Get-ChildItem -Path $BackupDir -File | Where-Object {
    $_.CreationTime -lt $CutoffDate -and $_.Name -match "backup_"
} | ForEach-Object {
    Write-Log "Removing old backup: $($_.Name)"
    Remove-Item $_.FullName -Force
}

# Backup verification
Write-Log "Verifying backup integrity"
if (Test-Path $BackupFileName) {
    if ($Compress -and $BackupFileName.EndsWith(".zip")) {
        try {
            $Archive = [System.IO.Compression.ZipFile]::OpenRead($BackupFileName)
            $Archive.Dispose()
            Write-Log "Backup archive is valid"
        } catch {
            Write-Log "Backup archive verification failed: $($_.Exception.Message)" "ERROR"
            exit 1
        }
    }
    Write-Log "Backup verification completed successfully"
} else {
    Write-Log "Backup file not found for verification" "ERROR"
    exit 1
}

Write-Log "Backup process completed successfully"
Write-Log "Database backup: $BackupFileName"
if (Test-Path $AppBackupFile) {
    Write-Log "Application backup: $AppBackupFile"
}

# Summary
Write-Host "`n=== Backup Summary ===" -ForegroundColor Green
Write-Host "Backup Type: $BackupType" -ForegroundColor Cyan
Write-Host "Database Backup: $BackupFileName" -ForegroundColor Cyan
if (Test-Path $AppBackupFile) {
    Write-Host "Application Backup: $AppBackupFile" -ForegroundColor Cyan
}
Write-Host "Log File: $LogFile" -ForegroundColor Cyan
Write-Host "Backup completed at: $(Get-Date)" -ForegroundColor Green