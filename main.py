from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# تنظیمات
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
service = Service(ChromeDriverManager().install())

try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 1. دریافت محتوا
    raw_content = requests.get("https://raw.githubusercontent.com/e-schamberger/free/refs/heads/main/config/vless.json").text
    
    # 2. عملیات تبدیل
    driver.get("https://v2rayse.com/node-convert")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//textarea'))
    ).send_keys(raw_content)
    
    # 3. دریافت نتیجه
    result = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.XPATH, '//div[contains(@class,"output")]'))
    ).text
    
    # 4. ذخیره‌سازی با چک‌های اضافه
    if result.strip():
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(result)
            print(f"ذخیره شد! حجم محتوا: {len(result)} کاراکتر")
    else:
        print("هشدار: محتوای خروجی خالی است!")
        driver.save_screenshot("empty_output.png")

except Exception as e:
    print(f"خطا: {str(e)}")
    driver.save_screenshot("error.png")
finally:
    driver.quit()
