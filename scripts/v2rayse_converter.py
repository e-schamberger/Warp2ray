import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_raw_configs():
    """دریافت لینک‌ها از فایل links.txt و دانلود محتوا"""
    configs = []
    
    if not os.path.exists("inputs/links.txt"):
        print("Error: inputs/links.txt not found!")
        return []
    
    with open("inputs/links.txt", "r") as f:
        links = [l.strip() for l in f.readlines() if l.strip()]
    
    for url in links:
        try:
            print(f"Downloading {url}...")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            configs.append(response.text)
            print(f"Downloaded {len(response.text)} characters")
        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")
    
    return configs

def convert_with_v2rayse(config_text):
    """استفاده از سایت v2rayse.com برای تبدیل کانفیگ"""
    try:
        # تنظیمات مرورگر
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # ایجاد درایور
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # رفتن به صفحه تبدیل
        driver.get("https://v2rayse.com/node-convert")
        
        # پیدا کردن فیلد ورودی و وارد کردن محتوا
        input_area = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "input"))
        )
        input_area.clear()
        input_area.send_keys(config_text)
        
        # انتخاب فرمت خروجی به عنوان سینگ‌باکس
        format_select = driver.find_element(By.ID, "outtype")
        format_select.send_keys("singbox")
        
        # کلیک بر روی دکمه تبدیل
        convert_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Convert')]")
        convert_btn.click()
        
        # منتظر ماندن برای تکمیل تبدیل
        time.sleep(5)
        
        # دریافت نتیجه تبدیل
        output_area = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "output"))
        )
        result = output_area.get_attribute("value")
        
        # بستن مرورگر
        driver.quit()
        
        return result
        
    except Exception as e:
        print(f"Conversion error: {str(e)}")
        return None

def save_results(results):
    """ذخیره نتایج تبدیل در فایل‌های خروجی"""
    for i, result in enumerate(results):
        if not result:
            continue
            
        output_file = f"outputs/converted_{i+1}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Saved converted config to {output_file}")

def main():
    """تابع اصلی اجرای فرآیند"""
    # دریافت کانفیگ‌های خام
    raw_configs = get_raw_configs()
    if not raw_configs:
        print("No configs to process")
        return
        
    # تبدیل هر کانفیگ
    converted_results = []
    for config in raw_configs:
        print("Converting config...")
        result = convert_with_v2rayse(config)
        converted_results.append(result)
    
    # ذخیره نتایج
    save_results(converted_results)

if __name__ == "__main__":
    main()
