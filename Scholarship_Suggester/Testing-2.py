from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import time

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
    titles = []

    while True:
        link_elements = driver.find_elements(By.XPATH, "//div[contains(text(),'ไปยังแหล่งทุน')]")
        total = len(link_elements)
        print(f"พบทั้งหมด {total} ทุน")

        for i in range(len(titles), total):
            try:
                link_elements = driver.find_elements(By.XPATH, "//div[contains(text(),'ไปยังแหล่งทุน')]")
                driver.execute_script("arguments[0].click();", link_elements[i])
                time.sleep(5)

                # ดึงหน้า detail แล้วเก็บ <h1>
                detail_html = driver.page_source
                detail_soup = BeautifulSoup(detail_html, 'html.parser')
                title = detail_soup.find(class_="lg:w-5/6 m-auto mt-12 markdowner fMaitree ")

                if title:
                    titles.append(title.prettify())
                # else:
                #     titles.append("(ไม่พบหัวข้อ)")

                driver.back()  # กลับไปยังหน้า list
                time.sleep(3)
                print(len(titles), "ทุนที่ดึงข้อมูลแล้ว")

            except IndexError:
                print("องค์ประกอบหายไปจาก DOM หลัง back กลับมา รีโหลดลูป")
                break  # ออกจากลูปในกรณีองค์ประกอบหาย
        else:
            break  # ถ้าลูปทำจบครบทุกตัวโดยไม่ break → ออกลูป while

    print("ผลลัพธ์:")
    print(titles)
    # for i, t in enumerate(titles, 1):
    #     print(f"{i}. {t}")

finally:
    driver.quit()
