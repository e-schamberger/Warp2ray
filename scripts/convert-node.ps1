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

# Get latest stable Chrome version
$cftData = Invoke-RestMethod -Uri "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json"
$stableVersion = $cftData.milestones.PSObject.Properties | 
    Where-Object { $_.Name -ne 'dev' } | 
    Sort-Object { [int]$_.Name } -Descending | 
    Select-Object -First 1 -ExpandProperty Value

$chromeVersion = $stableVersion.version
Write-Host "Latest stable Chrome version: $chromeVersion"

# Download Chrome for Testing
$chromeDir = "$env:TEMP\chrome"
New-Item -Path $chromeDir -ItemType Directory -Force | Out-Null
$chromeZipUrl = ($stableVersion.downloads.chrome | Where-Object platform -eq 'win64').url
$chromeZipPath = "$chromeDir\chrome.zip"

Write-Host "Downloading Chrome for Testing from: $chromeZipUrl"
Invoke-WebRequest -Uri $chromeZipUrl -OutFile $chromeZipPath
Expand-Archive -Path $chromeZipPath -DestinationPath $chromeDir -Force
$chromePath = (Get-ChildItem -Path $chromeDir -Filter "chrome.exe" -Recurse | Select-Object -First 1).FullName
Write-Host "Chrome path: $chromePath"

# Download ChromeDriver
$chromeDriverDir = "$env:TEMP\chromedriver"
New-Item -Path $chromeDriverDir -ItemType Directory -Force | Out-Null
$chromeDriverZipUrl = ($stableVersion.downloads.chromedriver | Where-Object platform -eq 'win64').url
$chromeDriverZipPath = "$chromeDriverDir\chromedriver.zip"

Write-Host "Downloading ChromeDriver from: $chromeDriverZipUrl"
Invoke-WebRequest -Uri $chromeDriverZipUrl -OutFile $chromeDriverZipPath
Expand-Archive -Path $chromeDriverZipPath -DestinationPath $chromeDriverDir -Force

# Find chromedriver.exe
$chromeDriverExe = Get-ChildItem -Path $chromeDriverDir -Filter "chromedriver.exe" -Recurse | Select-Object -First 1
if (-not $chromeDriverExe) {
    Write-Host "ERROR: chromedriver.exe not found in $chromeDriverDir"
    exit 1
}

$chromeDriverPath = $chromeDriverExe.DirectoryName
Write-Host "ChromeDriver path: $chromeDriverPath"
$env:PATH = "$chromeDriverPath;$env:PATH"

# Configure Chrome options
$chromeOptions = New-Object OpenQA.Selenium.Chrome.ChromeOptions
$chromeOptions.BinaryLocation = $chromePath
$chromeOptions.AddArgument("--headless=new")
$chromeOptions.AddArgument("--disable-gpu")
$chromeOptions.AddArgument("--no-sandbox")
$chromeOptions.AddArgument("--disable-dev-shm-usage")
$chromeOptions.AddArgument("--window-size=1920,1080")
$chromeOptions.AddArgument("--start-maximized")
$chromeOptions.AddArgument("--log-level=3")

try {
    Write-Host "Starting ChromeDriver..."
    $driver = New-Object OpenQA.Selenium.Chrome.ChromeDriver($chromeDriverPath, $chromeOptions)
    Write-Host "ChromeDriver started successfully"

    # Open website
    $driver.Navigate().GoToUrl("https://v2rayse.com/node-convert")
    Write-Host "Opened website"
    
    # Wait for page to load completely
    $wait = New-Object OpenQA.Selenium.Support.UI.WebDriverWait($driver, (New-TimeSpan -Seconds 30))
    $wait.Until([Func[OpenQA.Selenium.IWebDriver, Boolean]]{
        param($d)
        try {
            $d.FindElement([OpenQA.Selenium.By]::XPath("//h1[contains(text(),'V2ray Node Convert')]"))
            return $true
        }
        catch {
            return $false
        }
    })
    Write-Host "Page loaded successfully"
    Start-Sleep -Seconds 3

    # More reliable element finding with retries
    function Find-ElementWithRetry {
        param(
            [Parameter(Mandatory=$true)]
            [OpenQA.Selenium.By]$By,
            [int]$Retries = 3,
            [int]$Delay = 2
        )
        $attempt = 0
        while ($attempt -lt $Retries) {
            try {
                $element = $driver.FindElement($By)
                return $element
            }
            catch {
                $attempt++
                if ($attempt -ge $Retries) {
                    throw
                }
                Start-Sleep -Seconds $Delay
            }
        }
    }

    # Click first button - updated selector
    try {
        $button1 = Find-ElementWithRetry -By ([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-content-copy')]]")) -Retries 5
        $button1.Click()
        Write-Host "Clicked first button"
        Start-Sleep -Seconds 2
    }
    catch {
        # Try alternative selector
        $button1 = Find-ElementWithRetry -By ([OpenQA.Selenium.By]::XPath("//button[contains(@class, 'v-btn') and .//i[contains(@class, 'mdi')]]")) -Retries 5
        $button1.Click()
        Write-Host "Clicked first button (using alternative selector)"
        Start-Sleep -Seconds 2
    }

    # Click second button
    $button2 = Find-ElementWithRetry -By ([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-dots-vertical')]]")) -Retries 5
    $button2.Click()
    Write-Host "Clicked second button"
    Start-Sleep -Seconds 2

    # Select middle option
    $option = Find-ElementWithRetry -By ([OpenQA.Selenium.By]::XPath("//div[contains(text(), 'VLESS')]")) -Retries 5
    $option.Click()
    Write-Host "Selected VLESS option"
    Start-Sleep -Seconds 2

    # Click confirm button
    $confirmBtn = Find-ElementWithRetry -By ([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-check')]]")) -Retries 5
    $confirmBtn.Click()
    Write-Host "Clicked confirm button"
    Start-Sleep -Seconds 2

    # Enter URL
    $inputField = Find-ElementWithRetry -By ([OpenQA.Selenium.By]::XPath("//input")) -Retries 5
    $inputField.Clear()
    $inputField.SendKeys("https://raw.githubusercontent.com/e-schamberger/free/refs/heads/main/config/vless.json")
    Write-Host "Entered URL"
    Start-Sleep -Seconds 2

    # Click conversion buttons - updated selectors
    $convertBtn1 = Find-ElementWithRetry -By ([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-content-copy') and not(ancestor::div[contains(@class, 'v-menu')]]")) -Retries 5
    $convertBtn1.Click()
    Write-Host "Clicked first conversion button"
    Start-Sleep -Seconds 5

    $convertBtn2 = Find-ElementWithRetry -By ([OpenQA.Selenium.By]::XPath("(//button[.//i[contains(@class, 'mdi-arrow-right-bold-hexagon-outline')])[2]")) -Retries 5
    $convertBtn2.Click()
    Write-Host "Clicked second conversion button"
    Start-Sleep -Seconds 5

    # Select third option
    $thirdOption = Find-ElementWithRetry -By ([OpenQA.Selenium.By]::XPath("(//div[contains(@class, 'v-list-item__title')])[3]")) -Retries 5
    $thirdOption.Click()
    Write-Host "Selected third option"
    Start-Sleep -Seconds 3

    # Generate result
    $generateBtn = Find-ElementWithRetry -By ([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-download')]]")) -Retries 5
    $generateBtn.Click()
    Write-Host "Clicked generate button"
    Start-Sleep -Seconds 5

    # Get result text
    $resultModal = Find-ElementWithRetry -By ([OpenQA.Selenium.By]::TagName("textarea")) -Retries 5
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
        $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $screenshotPath = "$env:TEMP\selenium_error_$timestamp.png"
        $driver.GetScreenshot().SaveAsFile($screenshotPath)
        Write-Host "Screenshot saved to $screenshotPath"
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
