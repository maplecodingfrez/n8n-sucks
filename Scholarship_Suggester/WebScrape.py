from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# ตั้งค่า Chrome
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

driver = webdriver.Chrome(options=options)

try:
    url = 'https://findstudentship.eef.or.th/scholarship?grade=ทุกระดับ&cost=ทุนทั้งหมด&genre=ทุนให้เปล่า'
    driver.get(url)

    # กดปุ่ม "ดูเพิ่มเติม" ซ้ำเรื่อย ๆ จนไม่มีให้กดแล้ว
    max_click = 10
    last_count = 0
    while True:
        # หา "ไปยังแหล่งทุน" ที่แสดงทั้งหมดก่อนกด
        buttons = driver.find_elements(By.XPATH, "//div[contains(text(),'ไปยังแหล่งทุน')]")
        current_count = len(buttons)

        try:
            # พยายามกดปุ่มดูเพิ่มเติม
            load_more = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'ดูเพิ่มเติม')]"))
            )
            driver.execute_script("arguments[0].scrollIntoView();", load_more)
            load_more.click()
            print("กดปุ่ม 'ดูเพิ่มเติม'")
            time.sleep(2)  # รอข้อมูลโหลด
        except:
            print("ไม่มีปุ่ม 'ดูเพิ่มเติม' แล้ว")
            break

        # ถ้ากดแล้วไม่มีรายการใหม่เพิ่ม แสดงว่าโหลดครบแล้ว
        buttons = driver.find_elements(By.XPATH, "//div[contains(text(),'ไปยังแหล่งทุน')]")
        if len(buttons) == current_count:
            print("ไม่มีรายการใหม่เพิ่มแล้ว")
            break

        last_count += 1
        if last_count >= max_click:
            print("ถึงจำนวนการกดสูงสุดแล้ว")
            break

    print(f"\nรายการทั้งหมดที่เจอ: {len(buttons)}")

    # ดึงชื่อทุนทั้งหมดจาก list page โดยไม่ต้องคลิก
    page_html = driver.page_source
    soup = BeautifulSoup(page_html, 'html.parser')

    # ดึงชื่อทุนจาก div h2
    title_divs = soup.find_all('h2')
    scholarship_titles = [t.get_text(strip=True) for t in title_divs if t.get_text(strip=True)]

finally:
    driver.quit()

# แสดงผล
print("\nรายชื่อทุนทั้งหมด:")
for idx, title in enumerate(scholarship_titles, 1):
    print(f"{idx}. {title}")
