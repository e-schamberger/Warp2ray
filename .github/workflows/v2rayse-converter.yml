import os
import time
import requests
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# تنظیمات لاگ‌گیری
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('v2rayse_converter')

def get_raw_configs():
    """دریافت لینک‌ها از فایل links.txt و دانلود محتوا"""
    logger.info("دریافت کانفیگ‌های خام شروع شد")
    
    # اطمینان از وجود پوشه inputs
    os.makedirs("inputs", exist_ok=True)
    
    if not os.path.exists("inputs/links.txt"):
        logger.warning("فایل inputs/links.txt یافت نشد. ایجاد فایل نمونه...")
        with open("inputs/links.txt", "w") as f:
            f.write("https://raw.githubusercontent.com/lagzian/new-configs-collector/main/countries/hr/mixed\n")
        logger.info("فایل inputs/links.txt با محتوای نمونه ایجاد شد")
    
    configs = []
    
    try:
        with open("inputs/links.txt", "r") as f:
            links = [l.strip() for l in f.readlines() if l.strip()]
        
        logger.info(f"تعداد {len(links)} لینک در فایل یافت شد")
        
        for i, url in enumerate(links):
            try:
                logger.info(f"دانلود لینک {i+1}/{len(links)}: {url}")
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                
                content = response.text
                configs.append(content)
                logger.info(f"دانلود موفق! اندازه محتوا: {len(content)} کاراکتر")
                
            except Exception as e:
                logger.error(f"خطا در دانلود {url}: {str(e)}")
    
    except Exception as e:
        logger.error(f"خطا در خواندن فایل links.txt: {str(e)}")
    
    return configs

def convert_with_v2rayse(config_text):
    """استفاده از سایت v2rayse.com برای تبدیل کانفیگ"""
    logger.info("شروع فرآیند تبدیل با v2rayse.com")
    
    driver = None
    try:
        # تنظیمات مرورگر
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # ایجاد درایور
        logger.info("راه‌اندازی مرورگر کروم...")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # رفتن به صفحه تبدیل
        logger.info("بارگذاری صفحه v2rayse.com")
        driver.get("https://v2rayse.com/node-convert")
        
        # پیدا کردن فیلد ورودی
        logger.info("یافتن فیلد ورودی...")
        input_area = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "input"))
        )
        
        # وارد کردن محتوا
        logger.info("وارد کردن محتوای کانفیگ...")
        input_area.clear()
        input_area.send_keys(config_text)
        
        # انتخاب فرمت خروجی
        logger.info("انتخاب فرمت خروجی به عنوان سینگ‌باکس...")
        format_select = driver.find_element(By.ID, "outtype")
        format_select.send_keys("singbox")
        
        # کلیک بر روی دکمه تبدیل
        logger.info("کلیک بر روی دکمه تبدیل...")
        convert_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Convert')]")
        convert_btn.click()
        
        # منتظر ماندن برای تکمیل تبدیل
        logger.info("منتظر ماندن برای تکمیل تبدیل...")
        time.sleep(5)
        
        # دریافت نتیجه تبدیل
        logger.info("دریافت نتیجه تبدیل...")
        output_area = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "output"))
        )
        result = output_area.get_attribute("value")
        
        if not result:
            logger.warning("هیچ خروجی از تبدیل دریافت نشد")
            # گرفتن اسکرین‌شات برای دیباگ
            driver.save_screenshot("conversion_error.png")
            logger.info("اسکرین‌شات از صفحه ذخیره شد: conversion_error.png")
        
        return result
        
    except Exception as e:
        logger.error(f"خطا در فرآیند تبدیل: {str(e)}")
        # گرفتن اسکرین‌شات در صورت خطا
        if driver:
            driver.save_screenshot("selenium_error.png")
            logger.info("اسکرین‌شات از خطا ذخیره شد: selenium_error.png")
        return None
        
    finally:
        if driver:
            logger.info("بستن مرورگر...")
            driver.quit()

def save_results(results):
    """ذخیره نتایج تبدیل در فایل‌های خروجی"""
    if not results:
        logger.warning("هیچ نتیجه‌ای برای ذخیره وجود ندارد")
        return
        
    # ایجاد پوشه خروجی
    os.makedirs("outputs", exist_ok=True)
    
    count = 0
    for i, result in enumerate(results):
        if not result:
            logger.warning(f"نتیجه برای کانفیگ {i+1} خالی است، ذخیره نشد")
            continue
            
        output_file = f"outputs/converted_{i+1}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result)
        
        count += 1
        logger.info(f"نتیجه در {output_file} ذخیره شد")
    
    logger.info(f"تعداد {count} فایل خروجی ذخیره شد")

def main():
    """تابع اصلی اجرای فرآیند"""
    logger.info("شروع فرآیند تبدیل کانفیگ‌ها")
    
    # دریافت کانفیگ‌های خام
    raw_configs = get_raw_configs()
    
    if not raw_configs:
        logger.error("هیچ کانفیگی برای پردازش یافت نشد")
        return
        
    logger.info(f"تعداد {len(raw_configs)} کانفیگ برای تبدیل دریافت شد")
    
    # تبدیل هر کانفیگ
    converted_results = []
    for i, config in enumerate(raw_configs):
        logger.info(f"تبدیل کانفیگ {i+1}/{len(raw_configs)}...")
        result = convert_with_v2rayse(config)
        converted_results.append(result)
    
    # ذخیره نتایج
    save_results(converted_results)
    logger.info("فرآیند تبدیل کامل شد")

if __name__ == "__main__":
    main()
