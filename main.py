from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import requests

# تنظیمات Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=chrome_options)

try:
    # 1. دریافت محتوای RAW
    raw_url = "https://raw.githubusercontent.com/your-account/your-repo/main/your-file.txt"
    raw_content = requests.get(raw_url).text

    # 2. ورود به سایت
    driver.get("https://v2rayse.com/node-convert")
    
    # 3. انتظار برای بارگذاری کامل صفحه
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//div[@id="__nuxt"]'))
    )
    time.sleep(2)  # اضافه کردن تأخیر اضافی

    # 4. پیدا کردن کادر ورودی با روش مطمئن‌تر
    input_box = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"input-area")]//textarea'))
    )
    
    # 5. اسکرول و تعامل با المان
    driver.execute_script("arguments[0].scrollIntoView(true);", input_box)
    time.sleep(1)
    input_box.clear()
    input_box.send_keys(raw_content)

    # ادامه عملیات...

except Exception as e:
    print(f"خطا: {str(e)}")
    driver.save_screenshot("error.png")
finally:
    driver.quit()
