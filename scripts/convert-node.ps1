# Install required modules
Install-PackageProvider -Name NuGet -Force
Install-Module -Name Selenium -Force

# Import modules
Import-Module Selenium

# Download Chrome WebDriver
$driverPath = "C:\WebDriver"
New-Item -Path $driverPath -ItemType Directory -Force
Invoke-WebRequest "https://chromedriver.storage.googleapis.com/LATEST_RELEASE" -OutFile "$driverPath\version.txt"
$version = Get-Content "$driverPath\version.txt"
Invoke-WebRequest "https://chromedriver.storage.googleapis.com/$version/chromedriver_win32.zip" -OutFile "$driverPath\chromedriver.zip"
Expand-Archive -Path "$driverPath\chromedriver.zip" -DestinationPath $driverPath -Force

# Start Chrome
$chromeOptions = New-Object OpenQA.Selenium.Chrome.ChromeOptions
$chromeOptions.AddArgument("--headless")
$driver = New-Object OpenQA.Selenium.Chrome.ChromeDriver($driverPath, $chromeOptions)

# Main automation script
try {
    # Open website
    $driver.Navigate().GoToUrl("https://v2rayse.com/node-convert")
    Start-Sleep -Seconds 5

    # Click first button
    $button1 = $driver.FindElement([OpenQA.Selenium.By]::XPath("//*[@id='__nuxt']/div/div/main/div/div/div/div[3]/div/div[2]/button/span[3]/i"))
    $button1.Click()
    Start-Sleep -Seconds 2

    # Click second button
    $button2 = $driver.FindElement([OpenQA.Selenium.By]::XPath("//*[@id='v-menu-125']/div/div/div[3]/div[3]/div[2]/div/button/span[3]/i"))
    $button2.Click()
    Start-Sleep -Seconds 2

    # Select middle option
    $option = $driver.FindElement([OpenQA.Selenium.By]::XPath("//*[@id='v-menu-125']/div/div/div[3]/div[2]/div[2]/div/div/div[1]/div/div[3]/div/div/span/font/font/font"))
    $option.Click()
    Start-Sleep -Seconds 2

    # Click confirm button
    $confirmBtn = $driver.FindElement([OpenQA.Selenium.By]::XPath("//*[@id='v-menu-125']/div/div/div[3]/div[2]/div[2]/div/div/div[2]/button/span[3]/i"))
    $confirmBtn.Click()
    Start-Sleep -Seconds 2

    # Enter URL
    $inputField = $driver.FindElement([OpenQA.Selenium.By]::XPath("//*[@id='VVwmHIqu2LR0babO']"))
    $inputField.SendKeys("https://raw.githubusercontent.com/e-schamberger/free/refs/heads/main/config/vless.json")
    Start-Sleep -Seconds 1

    # Click conversion buttons
    $convertBtn1 = $driver.FindElement([OpenQA.Selenium.By]::XPath("/html/body/div[3]/div[2]/div[2]/div/div[3]/div/div[2]/button/span[3]/font/font/font"))
    $convertBtn1.Click()
    Start-Sleep -Seconds 3

    $convertBtn2 = $driver.FindElement([OpenQA.Selenium.By]::XPath("/html/body/div[3]/div[2]/div[2]/div/div[2]/div/div[2]/button[2]/span[3]/i"))
    $convertBtn2.Click()
    Start-Sleep -Seconds 3

    # Select third option
    $thirdOption = $driver.FindElement([OpenQA.Selenium.By]::XPath("//*[@id='__nuxt']/div/div/main/div/div/div/div[3]/div/div[1]/div/div[1]/div/div[3]/div/div/span"))
    $thirdOption.Click()
    Start-Sleep -Seconds 2

    # Generate result
    $generateBtn = $driver.FindElement([OpenQA.Selenium.By]::XPath("//*[@id='__nuxt']/div/div/main/div/div/div/div[3]/div/div[1]/div/div[2]/div/div/button/span[4]/font/font/font"))
    $generateBtn.Click()
    Start-Sleep -Seconds 5

    # Get result text
    $resultModal = $driver.FindElement([OpenQA.Selenium.By]::XPath("/html/body/div[3]/div/div[2]/div/div[2]/div/div[1]/div/div/div/div/div/textarea"))
    $resultText = $resultModal.GetAttribute("value")

    # Save to file
    $resultText | Out-File -FilePath ".\result.txt" -Encoding utf8

}
finally {
    $driver.Quit()
}
