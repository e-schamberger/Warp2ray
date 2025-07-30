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
    Write-Host "Installing Chrome..."
    $chromeInstaller = "$env:TEMP\chrome_installer.exe"
    Invoke-WebRequest "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/120.0.6099.109/win64/chrome-installer.exe" -OutFile $chromeInstaller
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

    # Open website
    $driver.Navigate().GoToUrl("https://v2rayse.com/node-convert")
    Write-Host "Opened website"
    Start-Sleep -Seconds 10

    # Click first button
    $button1 = $driver.FindElement([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-content-copy')]]"))
    $button1.Click()
    Write-Host "Clicked first button"
    Start-Sleep -Seconds 5

    # Click second button
    $button2 = $driver.FindElement([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-dots-vertical')]]"))
    $button2.Click()
    Write-Host "Clicked second button"
    Start-Sleep -Seconds 5

    # Select middle option
    $option = $driver.FindElement([OpenQA.Selenium.By]::XPath("//div[contains(text(), 'VLESS')]"))
    $option.Click()
    Write-Host "Selected VLESS option"
    Start-Sleep -Seconds 3

    # Click confirm button
    $confirmBtn = $driver.FindElement([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-check')]]"))
    $confirmBtn.Click()
    Write-Host "Clicked confirm button"
    Start-Sleep -Seconds 3

    # Enter URL
    $inputField = $driver.FindElement([OpenQA.Selenium.By]::XPath("//input"))
    $inputField.SendKeys("https://raw.githubusercontent.com/e-schamberger/free/refs/heads/main/config/vless.json")
    Write-Host "Entered URL"
    Start-Sleep -Seconds 3

    # Click conversion buttons
    $convertBtn1 = $driver.FindElement([OpenQA.Selenium.By]::XPath("(//button[.//i[contains(@class, 'mdi-content-copy')]])[last()]"))
    $convertBtn1.Click()
    Write-Host "Clicked first conversion button"
    Start-Sleep -Seconds 8

    $convertBtn2 = $driver.FindElement([OpenQA.Selenium.By]::XPath("(//button[.//i[contains(@class, 'mdi-arrow-right-bold-hexagon-outline')]])[2]"))
    $convertBtn2.Click()
    Write-Host "Clicked second conversion button"
    Start-Sleep -Seconds 8

    # Select third option
    $thirdOption = $driver.FindElement([OpenQA.Selenium.By]::XPath("(//div[@class='v-list-item__title'])[3]"))
    $thirdOption.Click()
    Write-Host "Selected third option"
    Start-Sleep -Seconds 5

    # Generate result
    $generateBtn = $driver.FindElement([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-download')]]"))
    $generateBtn.Click()
    Write-Host "Clicked generate button"
    Start-Sleep -Seconds 8

    # Get result text
    $resultModal = $driver.FindElement([OpenQA.Selenium.By]::TagName("textarea"))
    $resultText = $resultModal.GetAttribute("value")
    Write-Host "Retrieved result text"

    # Save to file
    $resultText | Out-File -FilePath "converted-node.txt" -Encoding utf8
    Write-Host "Result saved to converted-node.txt"
}
catch {
    Write-Host "Error encountered: $_"
    # Take screenshot for debugging
    try {
        $screenshot = $driver.GetScreenshot()
        $screenshot.SaveAsFile("$env:TEMP\selenium_error.png")
        Write-Host "Screenshot saved to $env:TEMP\selenium_error.png"
    }
    catch {
        Write-Host "Failed to capture screenshot: $_"
    }
    exit 1
}
finally {
    if ($driver) {
        $driver.Quit()
        Write-Host "ChromeDriver closed"
    }
}
