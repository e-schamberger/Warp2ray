from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os

# تنظیمات
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
service = Service(ChromeDriverManager().install())

try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 1. دریافت محتوا
    raw_content = requests.get("YOUR_RAW_URL").text
    
    # 2. عملیات تبدیل
    driver.get("https://v2rayse.com/node-convert")
    input_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//textarea'))
    input_box.clear()
    input_box.send_keys(raw_content)
    
    # کلیک دکمه‌های لازم
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Convert")]'))
    ).click()
    
    time.sleep(5)  # انتظار برای پردازش
    
    # 3. دریافت نتیجه
    result = WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.XPATH, '//div[contains(@class,"output")]'))
    ).text
    
    # 4. ذخیره‌سازی
    with open("output.txt", "w", encoding="utf-8") as f:
        f.write(result)
        print(f"Result saved ({len(result)} characters)")

except Exception as e:
    print(f"Error: {str(e)}")
    driver.save_screenshot("error.png")
    # ایجاد فایل خروجی خالی برای جلوگیری از خطای گیت
    with open("output.txt", "w") as f:
        f.write("")
finally:
    driver.quit()
