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

# Start Chrome in headless mode
$chromeOptions = New-Object OpenQA.Selenium.Chrome.ChromeOptions
$chromeOptions.AddArgument("--headless")
$chromeOptions.AddArgument("--disable-gpu")
$chromeOptions.AddArgument("--no-sandbox")
$chromeOptions.AddArgument("--window-size=1920,1080")

$driver = New-Object OpenQA.Selenium.Chrome.ChromeDriver($chromeOptions)

try {
    # Open website
    $driver.Navigate().GoToUrl("https://v2rayse.com/node-convert")
    Start-Sleep -Seconds 10

    # Click first button
    $button1 = $driver.FindElement([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-content-copy')]]"))
    $button1.Click()
    Start-Sleep -Seconds 3

    # Click second button
    $button2 = $driver.FindElement([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-dots-vertical')]]"))
    $button2.Click()
    Start-Sleep -Seconds 3

    # Select middle option
    $option = $driver.FindElement([OpenQA.Selenium.By]::XPath("//div[contains(text(), 'VLESS')]"))
    $option.Click()
    Start-Sleep -Seconds 2

    # Click confirm button
    $confirmBtn = $driver.FindElement([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-check')]]"))
    $confirmBtn.Click()
    Start-Sleep -Seconds 2

    # Enter URL
    $inputField = $driver.FindElement([OpenQA.Selenium.By]::XPath("//input"))
    $inputField.SendKeys("https://raw.githubusercontent.com/e-schamberger/free/refs/heads/main/config/vless.json")
    Start-Sleep -Seconds 2

    # Click conversion buttons
    $convertBtn1 = $driver.FindElement([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-content-copy')]]"))
    $convertBtn1.Click()
    Start-Sleep -Seconds 5

    $convertBtn2 = $driver.FindElement([OpenQA.Selenium.By]::XPath("(//button[.//i[contains(@class, 'mdi-arrow-right-bold-hexagon-outline')]])[2]"))
    $convertBtn2.Click()
    Start-Sleep -Seconds 5

    # Select third option
    $thirdOption = $driver.FindElement([OpenQA.Selenium.By]::XPath("(//div[@class='v-list-item__title'])[3]"))
    $thirdOption.Click()
    Start-Sleep -Seconds 2

    # Generate result
    $generateBtn = $driver.FindElement([OpenQA.Selenium.By]::XPath("//button[.//i[contains(@class, 'mdi-download')]]"))
    $generateBtn.Click()
    Start-Sleep -Seconds 5

    # Get result text
    $resultModal = $driver.FindElement([OpenQA.Selenium.By]::TagName("textarea"))
    $resultText = $resultModal.GetAttribute("value")

    # Save to file
    $resultText | Out-File -FilePath "converted-node.txt" -Encoding utf8
}
finally {
    $driver.Quit()
}
