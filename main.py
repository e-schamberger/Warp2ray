from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# تنظیمات کروم برای GitHub Actions
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

try:
    # راه اندازی خودکار درایور
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    # 1. دریافت محتوای RAW
    raw_url = "https://raw.githubusercontent.com/e-schamberger/free/refs/heads/main/config/vless.json"  # این را اصلاح کنید
    raw_content = requests.get(raw_url).text

    # 2. ورود به سایت
    driver.get("https://v2rayse.com/node-convert")
    
    # 3. تعامل با صفحه
    input_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//textarea'))
    input_box.clear()
    input_box.send_keys(raw_content)
    
    # بقیه مراحل تبدیل...
    # (کدهای مربوط به دکمه‌ها و عملیات تبدیل را اینجا قرار دهید)

    # ذخیره نتیجه
    with open("output.txt", "w") as f:
        f.write("نتیجه تبدیل اینجا قرار می‌گیرد")

except Exception as e:
    print(f"خطا: {str(e)}")
    if 'driver' in locals():
        driver.save_screenshot("error.png")
finally:
    if 'driver' in locals():
        driver.quit()
