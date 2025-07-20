from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import requests

# تنظیمات Chrome برای اجرای بدون نمایش
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=chrome_options)

try:
    # 1. دریافت محتوای RAW از گیتهاب
    raw_url = "https://raw.githubusercontent.com/e-schamberger/free/refs/heads/main/config/vless.json"  # جایگزین کنید
    raw_content = requests.get(raw_url).text

    # 2. ورود به سایت
    driver.get("https://v2rayse.com/node-convert")
    time.sleep(3)

    # 3. پاک کردن و پر کردن کادر ورودی
    input_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@id="__nuxt"]//textarea | //div[@id="__nuxt"]//input'))
    )
    input_box.clear()
    input_box.send_keys(raw_content)

    # 4. انتخاب فرمت Singbox
    format_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Format") or contains(@class, "format-btn")]'))
    )
    format_btn.click()
    time.sleep(1)
    
    singbox_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "Singbox")]'))
    )
    singbox_option.click()

    # 5. کلیک روی دکمه تبدیل
    convert_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Convert") or contains(text(), "تبدیل")]'))
    )
    convert_btn.click()
    time.sleep(5)  # منتظر ماندن برای پردازش

    # 6. کپی نتیجه
    try:
        copy_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Copy") or contains(text(), "کپی")]'))
        )
        copy_btn.click()
    except:
        output_text = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "output-text")]'))
        ).text
        with open("output.txt", "w") as f:
            f.write(output_text)

finally:
    driver.quit()
