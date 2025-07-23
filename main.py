from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# تنظیمات کروم
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

try:
    # راه‌اندازی درایور
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # 1. دریافت محتوای RAW
    raw_content = requests.get("https://raw.githubusercontent.com/your-account/your-file.txt").text
    
    # 2. ورود به سایت
    driver.get("https://v2rayse.com/node-convert")
    
    # 3. پیدا کردن کادر ورودی (نسخه اصلاح‌شده)
    input_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//textarea'))
    )  # پرانتز بسته شد
    
    input_box.clear()
    input_box.send_keys(raw_content)
    
    # 4. ذخیره نتیجه
    with open("output.txt", "w") as f:
        f.write("Result will be here")
    
    print("عملیات با موفقیت انجام شد")

except Exception as e:
    print(f"خطا: {str(e)}")
    if 'driver' in locals():
        driver.save_screenshot("error.png")
finally:
    if 'driver' in locals():
        driver.quit()
