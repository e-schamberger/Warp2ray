# Ensure TLS 1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Install NuGet provider
if (-not (Get-PackageProvider -Name NuGet -ErrorAction SilentlyContinue -ListAvailable)) {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -ForceBootstrap | Out-Null
}

# Install Selenium module
if (-not (Get-Module -ListAvailable -Name Selenium)) {
    Set-PSRepository -Name PSGallery -InstallationPolicy Trusted
    Install-Module -Name Selenium -Force -SkipPublisherCheck -AllowClobber
}

Import-Module Selenium

# Start Chrome in headless mode
$chromeOptions = New-Object OpenQA.Selenium.Chrome.ChromeOptions
$chromeOptions.AddArgument("--headless")
$chromeOptions.AddArgument("--disable-gpu")
$chromeOptions.AddArgument("--no-sandbox")
$chromeOptions.AddArgument("--disable-dev-shm-usage")
$chromeOptions.AddArgument("--window-size=1920,1080")
$chromeOptions.AddArgument("--start-maximized")

try {
    # Use ChromeDriver from PATH
    $driver = New-Object OpenQA.Selenium.Chrome.ChromeDriver($chromeOptions)
    Write-Host "ChromeDriver started successfully"

    # Open website
    $driver.Navigate().GoToUrl("https://v2rayse.com/node-convert")
    Start-Sleep -Seconds 10

    # Click first button
    $button1 = $driver.FindElement([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-content-copy')]]"))
    $button1.Click()
    Start-Sleep -Seconds 5

    # Click second button
    $button2 = $driver.FindElement([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-dots-vertical')]]"))
    $button2.Click()
    Start-Sleep -Seconds 5

    # Select middle option
    $option = $driver.FindElement([OpenQA.Selenium.By]::XPath("//div[contains(text(), 'VLESS')]"))
    $option.Click()
    Start-Sleep -Seconds 3

    # Click confirm button
    $confirmBtn = $driver.FindElement([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-check')]]"))
    $confirmBtn.Click()
    Start-Sleep -Seconds 3

    # Enter URL
    $inputField = $driver.FindElement([OpenQA.Selenium.By]::XPath("//input"))
    $inputField.SendKeys("https://raw.githubusercontent.com/e-schamberger/free/refs/heads/main/config/vless.json")
    Start-Sleep -Seconds 3

    # Click conversion buttons
    $convertBtn1 = $driver.FindElement([OpenQA.Selenium.By]::XPath("(//button[.//i[contains(@class, 'mdi-content-copy')]])[last()]"))
    $convertBtn1.Click()
    Start-Sleep -Seconds 8

    $convertBtn2 = $driver.FindElement([OpenQA.Selenium.By]::XPath("(//button[.//i[contains(@class, 'mdi-arrow-right-bold-hexagon-outline')]])[2]"))
    $convertBtn2.Click()
    Start-Sleep -Seconds 8

    # Select third option
    $thirdOption = $driver.FindElement([OpenQA.Selenium.By]::XPath("(//div[@class='v-list-item__title'])[3]"))
    $thirdOption.Click()
    Start-Sleep -Seconds 5

    # Generate result
    $generateBtn = $driver.FindElement([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-download')]]"))
    $generateBtn.Click()
    Start-Sleep -Seconds 8

    # Get result text
    $resultModal = $driver.FindElement([OpenQA.Selenium.By]::TagName("textarea"))
    $resultText = $resultModal.GetAttribute("value")

    # Save to file
    $resultText | Out-File -FilePath "converted-node.txt" -Encoding utf8
    Write-Host "Result saved to converted-node.txt"
}
catch {
    Write-Host "Error encountered: $_"
    exit 1
}
finally {
    if ($driver) {
        $driver.Quit()
        Write-Host "ChromeDriver closed"
    }
}
