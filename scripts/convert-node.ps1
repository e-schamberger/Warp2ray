# Ensure TLS 1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Install NuGet provider
if (-not (Get-PackageProvider -Name NuGet -ErrorAction SilentlyContinue -ListAvailable)) {
    Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -ForceBootstrap | Out-Null
}

# Install Selenium module
if (-not (Get-Module -ListAvailable -Name Selenium)) {
    Install-Module -Name Selenium -Force -SkipPublisherCheck -AllowClobber
}

Import-Module Selenium

# Find Chrome installation path
$chromePath = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $chromePath) {
    Write-Host "Chrome not found! Installing Chrome..."
    $chromeInstaller = "$env:TEMP\chrome_installer.exe"
    Invoke-WebRequest "https://dl.google.com/chrome/install/latest/chrome_installer.exe" -OutFile $chromeInstaller
    Start-Process -FilePath $chromeInstaller -ArgumentList "/silent /install" -Wait
    Remove-Item $chromeInstaller
    $chromePath = "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
}

Write-Host "Using Chrome at: $chromePath"

# Get Chrome version
$chromeVersion = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($chromePath).ProductVersion
$chromeMajorVersion = $chromeVersion.Split('.')[0]
Write-Host "Chrome version: $chromeVersion"

# Get matching ChromeDriver version
$chromeDriverVersion = (Invoke-WebRequest -Uri "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$chromeMajorVersion" -UseBasicParsing).Content
Write-Host "Matching ChromeDriver version: $chromeDriverVersion"

# Download and setup ChromeDriver
$chromeDriverDir = "$env:TEMP\chromedriver"
New-Item -Path $chromeDriverDir -ItemType Directory -Force | Out-Null
$chromeDriverZipUrl = "https://chromedriver.storage.googleapis.com/$chromeDriverVersion/chromedriver_win32.zip"
$chromeDriverZipPath = "$chromeDriverDir\chromedriver.zip"

Invoke-WebRequest -Uri $chromeDriverZipUrl -OutFile $chromeDriverZipPath
Expand-Archive -Path $chromeDriverZipPath -DestinationPath $chromeDriverDir -Force
$env:PATH = "$chromeDriverDir;$env:PATH"

# Configure Chrome options
$chromeOptions = New-Object OpenQA.Selenium.Chrome.ChromeOptions
$chromeOptions.BinaryLocation = $chromePath
$chromeOptions.AddArgument("--headless")
$chromeOptions.AddArgument("--disable-gpu")
$chromeOptions.AddArgument("--no-sandbox")
$chromeOptions.AddArgument("--disable-dev-shm-usage")
$chromeOptions.AddArgument("--window-size=1920,1080")
$chromeOptions.AddArgument("--start-maximized")
$chromeOptions.AddArgument("--log-level=3")

try {
    Write-Host "Starting ChromeDriver..."
    $driver = New-Object OpenQA.Selenium.Chrome.ChromeDriver($chromeDriverDir, $chromeOptions)
    Write-Host "ChromeDriver started successfully"

    # Automation steps (same as before)
    $driver.Navigate().GoToUrl("https://v2rayse.com/node-convert")
    Start-Sleep -Seconds 10

    # ... rest of your automation code ...

    # Get result text
    $resultModal = $driver.FindElement([OpenQA.Selenium.By]::TagName("textarea"))
    $resultText = $resultModal.GetAttribute("value")

    # Save to file
    $resultText | Out-File -FilePath "converted-node.txt" -Encoding utf8
    Write-Host "Result saved to converted-node.txt"
}
catch {
    Write-Host "Error encountered: $_"
    $driver.GetScreenshot().SaveAsFile("$env:TEMP\selenium_error.png")
    Write-Host "Screenshot saved to $env:TEMP\selenium_error.png"
    exit 1
}
finally {
    if ($driver) {
        $driver.Quit()
        Write-Host "ChromeDriver closed"
    }
}
