# PowerShell script to install Python, Node.js, and necessary dependencies

# Define paths and URLs
$pythonInstallerUrl = "https://www.python.org/ftp/python/3.10.5/python-3.10.5-amd64.exe"
$nodeInstallerUrl = "https://nodejs.org/dist/v16.13.1/node-v16.13.1-x64.msi"
$pythonInstallerPath = "$env:TEMP\python-installer.exe"
$nodeInstallerPath = "$env:TEMP\node-installer.msi"

# Function to download files
Function Download-File {
    param (
        [string]$url,
        [string]$output
    )
    Invoke-WebRequest -Uri $url -OutFile $output
}

# Step 1: Download and install Python
Write-Host "Downloading Python installer..."
Download-File -url $pythonInstallerUrl -output $pythonInstallerPath
Write-Host "Installing Python..."
Start-Process -FilePath $pythonInstallerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait

# Step 2: Download and install Node.js
Write-Host "Downloading Node.js installer..."
Download-File -url $nodeInstallerUrl -output $nodeInstallerPath
Write-Host "Installing Node.js..."
Start-Process -FilePath $nodeInstallerPath -ArgumentList "/quiet" -Wait

# Step 3: Install Python dependencies
$requirementsFilePath = "requirements.txt"
Write-Host "Installing Python dependencies..."
pip install -r $requirementsFilePath

# Step 4: Install Node.js dependencies
$frontendDir = "client"
Write-Host "Installing Node.js dependencies..."
cd $frontendDir
npm install

Write-Host "Setup complete."