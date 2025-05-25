from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# ตั้งค่า options สำหรับ Chrome
options = Options()
options.add_argument('--headless')  # รัน Chrome ในโหมดไม่แสดงหน้าต่าง
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# สร้าง instance ของ Chrome WebDriver
driver = webdriver.Chrome(options=options)

# เปิดหน้าเว็บ
url = 'https://findstudentship.eef.or.th/scholarship?grade=ทุกระดับ&cost=ทุนทั้งหมด&genre=ทุนให้เปล่า'
driver.get(url)

# รอให้ JavaScript โหลดข้อมูลเสร็จ (ปรับเวลาได้ตามความเหมาะสม)
time.sleep(5)

# ดึง HTML หลังจากที่ JavaScript โหลดข้อมูลเสร็จ
html = driver.page_source

# ปิดเบราว์เซอร์
driver.quit()

# ใช้ BeautifulSoup เพื่อวิเคราะห์ HTML
soup = BeautifulSoup(html, 'html.parser')

# ค้นหาแท็กที่มี class="mb-5"
elements = soup.find_all(class_='mb-5')

# แสดงผลลัพธ์
for element in elements:
    print(element.get_text(strip=True))
