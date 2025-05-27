from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import time
import json

def parse_scholarship_detail(soup: BeautifulSoup) -> dict:
    def get_text_after_heading(heading_text):
        heading = soup.find(lambda tag: tag.name == "h2" and heading_text in tag.text)
        if not heading:
            return None
        next_tag = heading.find_next_sibling()
        if not next_tag:
            return None
        if next_tag.name == "p":
            return next_tag.get_text(strip=True)
        elif next_tag.name in ["ol", "ul"]:
            return [li.get_text(strip=True) for li in next_tag.find_all("li")]
        return None

    data = {}
    data["ทุนการศึกษา"] = get_text_after_heading("ชื่อทุนการศึกษา")
    data["หน่วยงานให้ทุน"] = get_text_after_heading("หน่วยงานให้ทุนการศึกษา")
    data["คำอธิบาย"] = get_text_after_heading("คำอธิบาย")
    data["คุณสมบัติผู้รับทุน"] = get_text_after_heading("คุณสมบัติผู้รับทุน")
    data["การสนับสนุนด้านทุนการศึกษา"] = get_text_after_heading("การสนับสนุนด้านทุนการศึกษา")
    data["ขั้นตอนการขอรับทุน"] = get_text_after_heading("ขั้นตอนการขอรับทุน")
    data["วันเปิดรับสมัคร"] = get_text_after_heading("วันเปิดรับสมัคร")

    # ดึงข้อมูลติดต่อแหล่งทุน (ลิงก์, เบอร์โทร ฯลฯ)
    contact_heading = soup.find(lambda tag: tag.name == "h2" and "ติดต่อแหล่งทุน" in tag.text)
    contact_info = []
    if contact_heading:
        next_tag = contact_heading.find_next_sibling()
        while next_tag and next_tag.name in ["p", "a", "h2"]:
            # ดึงลิงก์
            if next_tag.name == "a":
                href = next_tag.get("href")
                if href:
                    contact_info.append(href)
            # ดึงลิงก์ใน p
            elif next_tag.name == "p":
                links = next_tag.find_all("a")
                for a in links:
                    href = a.get("href")
                    if href:
                        contact_info.append(href)
                # ดึงข้อความใน p (เช่นเบอร์โทร)
                text = next_tag.get_text(strip=True)
                if text:
                    contact_info.append(text)
            next_tag = next_tag.find_next_sibling()
    data["ติดต่อแหล่งทุน"] = contact_info if contact_info else None

    return data

# ตั้งค่า options สำหรับ Chrome
options = Options()
options.add_argument('--headless')  # รัน Chrome แบบไม่แสดงหน้าต่าง
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')

# สร้าง instance ของ Chrome WebDriver
driver = webdriver.Chrome(options=options)

try:
    # เปิดหน้าเว็บ list ทุน
    url = 'https://findstudentship.eef.or.th/scholarship?grade=ทุกระดับ&cost=ทุนทั้งหมด&genre=ทุนให้เปล่า'
    driver.get(url)

    # รอให้หน้าเว็บโหลด
    time.sleep(3)

    # # คลิก "ดูเพิ่มเติม" ซ้ำๆ จนกว่าจะไม่มีให้คลิก
    # click_next_limit = 1
    # click_times = 0
    # while True:
    #     try:
    #         load_more_button = WebDriverWait(driver, 5).until(
    #             EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'ดูเพิ่มเติม')]"))
    #         )
    #         driver.execute_script("arguments[0].click();", load_more_button)
    #         time.sleep(2)
    #         click_times += 1
    #         print(f"Clicked 'ดูเพิ่มเติม' {click_times} times")
    #     except (TimeoutException, ElementClickInterceptedException):
    #         break
    #     if click_times >= click_next_limit:
    #         print("Reached click limit, stopping.")
    #         break

    # รอให้เนื้อหาหลังโหลดเพิ่มเติมเสร็จ
    time.sleep(2)

    # เก็บ list ของลิงก์ 'ไปยังแหล่งทุน'
    Datas = []

    while True:
        link_elements = driver.find_elements(By.XPATH, "//div[contains(text(),'ไปยังแหล่งทุน')]")
        total = len(link_elements)
        print(f"พบทั้งหมด {total} ทุน")

        for i in range(len(Datas), total):
            try:
                link_elements = driver.find_elements(By.XPATH, "//div[contains(text(),'ไปยังแหล่งทุน')]")
                driver.execute_script("arguments[0].click();", link_elements[i])
                time.sleep(5)

                # ดึงหน้า detail แล้วเก็บ <h1>
                detail_html = driver.page_source
                detail_soup = BeautifulSoup(detail_html, 'html.parser')
                data = parse_scholarship_detail(detail_soup)

                Datas.append(data)

                driver.back()  # กลับไปยังหน้า list
                time.sleep(3)
                print(len(Datas), "ทุนที่ดึงข้อมูลแล้ว")

            except IndexError:
                print("องค์ประกอบหายไปจาก DOM หลัง back กลับมา รีโหลดลูป")
                break  # ออกจากลูปในกรณีองค์ประกอบหาย
        else:
            break  # ถ้าลูปทำจบครบทุกตัวโดยไม่ break → ออกลูป while

    print("ผลลัพธ์:")
    print(Datas)

finally:
    driver.quit()
