import pyautogui
import keyboard
import pytesseract
import os
import sys
import time
import random
from PIL import ImageGrab
import youtube_login
from commentyoutube import comments
from pyautogui import click
import openai
import base64
from dotenv import load_dotenv

# แก้ไข path ให้สามารถ import keyword_youtube ได้
sys.path.append(r"C:\Users\nicke\PycharmProjects\PythonProject\.venv\var")
import keyword_youtube

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def parse_credentials(data):
    """ แยกข้อมูลบัญชีจาก youtube_login.py พร้อมแสดง email, password, backup_email """
    credentials = []
    for line in data.strip().split("\n"):
        parts = line.split("|")
        if len(parts) >= 3:
            email = parts[0]
            password = parts[1]
            backup_email = parts[2]
            credentials.append((email, password, backup_email))
    return credentials


def parse_keyword(data):
    """ แยกคีย์เวิร์ดจาก keyword_youtube.py """
    keywords = [line.strip() for line in data.strip().split("\n") if line.strip()]
    return keywords

def parse_comment(data):
    return [line.strip() for line in data.strip().split("\n") if line.strip()]


class Mybot:

    def __init__(self):
        self.youtube_accounts = parse_credentials(youtube_login.data)
        self.current_email_index = 0
        self.keywords = parse_keyword(keyword_youtube.keywords)
        self.current_keyword_index = 0
        self.current_comment_index = 0
        self.comments = parse_comment(comments)
        pyautogui.FAILSAFE = False

        # Load API Key
        load_dotenv(dotenv_path="API_KEY.env")
        openai.api_key = os.getenv("OPENAI_API_KEY")

        # พิกัดข้อความ
        self.bbox_list = [
            (719, 509, 1184, 547),
            (719, 896, 1184, 935),
            (719, 508, 1184, 534),
            (719, 889, 1184, 912),
            (719, 487, 1184, 510),
            (719, 868, 1184, 890),
            (719, 485, 1186, 524),
            (719, 876, 1184, 898),
        ]
        self.target_texts = ["มาจอง2pg", "สล็อตpg", "แตก2หมื่น"]
        self.screenshot_folder = r"D:\\BlueStacks"


    def get_latest_screenshot(self):
        files = [os.path.join(self.screenshot_folder, f) for f in os.listdir(self.screenshot_folder) if f.endswith(".png")]
        return max(files, key=os.path.getctime) if files else None

    def ocr_image_gpt(self, filepath):
        with open(filepath, "rb") as f:
            base64_img = base64.b64encode(f.read()).decode("utf-8")

        prompt = f"""
        OCR ข้อความจากภาพ และตรวจว่ามีคำใดคำหนึ่งในนี้หรือไม่:
        {self.target_texts}
        ถ้ามีให้ตอบว่า \"✅ พบ\" พร้อมข้อความ OCR
        ถ้าไม่มีให้ตอบว่า \"❌ ไม่พบข้อความที่ต้องการ\"
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "ช่วย OCR ข้อความจากภาพนี้"},
                        {"type": "image_url", "image_url": f"data:image/png;base64,{base64_img}"}
                    ]
                }
            ],
            max_tokens=1000
        )
        return response['choices'][0]['message']['content']

    def process_ocr_from_blustacks(self):
        pyautogui.hotkey('ctrl', 'shift', 's')
        time.sleep(1.5)
        image_path = self.get_latest_screenshot()
        if not image_path:
            print("❌ ไม่พบภาพแคป")
            return False

        print(f"📷 ตรวจภาพ: {os.path.basename(image_path)}")
        result = self.ocr_image_gpt(image_path)
        print("🧠 ผล OCR:", result)

        os.remove(image_path)

        if "✅ พบ" in result:
            print("✅ พบข้อความ → คลิก และเข้าสู่ process_after_found")
            x1, y1, x2, y2 = self.bbox_list[0]
            pyautogui.click((x1 + x2) // 2, (y1 + y2) // 2)
            self.process_after_found()
            return True
        else:
            print("🔁 ไม่พบ → กด alt + down และวน OCR ต่อ")
            pyautogui.hotkey('alt', 'down')
            return False


    def get_next_keyword(self):
        """ ดึงคีย์เวิร์ดทีละตัว และวนกลับไปที่บรรทัดแรกเมื่อหมด """
        if not self.keywords:
            return None
        keyword = self.keywords[self.current_keyword_index]
        self.current_keyword_index = (self.current_keyword_index + 1) % len(self.keywords)
        return keyword

    def get_next_comment(self):
        if not self.comments:
            return None
        comment = self.comments[self.current_comment_index]
        self.current_comment_index = (self.current_comment_index + 1) % len(self.comments)
        return comment


    def main_process(self):
        print("\U0001F4E2 เริ่มทำงาน main_process()")

        time.sleep(5)
        #ค้นหา
        pyautogui.click(x=800, y=333)  # ค้นหา kw
        time.sleep(3)
        keyword = self.get_next_keyword()
        print(f"\U0001F50D กำลังค้นหา: {keyword}")
        keyboard.write(keyword, delay=0.5)
        pyautogui.press("enter")
        print("ขั้นตอนที่ 4 ใส่คีย์เวิร์ดเสร็จสิ้น")
        time.sleep(10)

        #คั้งค่าฟิวเตอร์
        pyautogui.click(x=1115, y=165) #ฟิวเตอร์
        time.sleep(5)
        pyautogui.click(x=815, y=222) #ตัวกรองค้นหา
        time.sleep(5)
        pyautogui.click(x=807, y=313)  # วันนี้
        print("ขั้นตอนที่ 5 setteing filter")
        time.sleep(5)

        scroll_count = 0
        max_scrolls = 100
        while scroll_count < max_scrolls:
            found = self.process_ocr_from_blustacks()
            if found:
                return True
            scroll_count += 1
        print("❌ ครบ 100 ครั้ง ยังไม่เจอข้อความ")
        return False

    def process_after_found(self):

        #comment
        time.sleep(random.uniform(250, 300))
        pyautogui.click(x=1172, y=506) #กดติดตาม
        time.sleep(3)
        pyautogui.click(x=702, y=554) #กดถูกใจ
        time.sleep(3)
        pyautogui.click(x=809, y=632) #กดดูคอมเม้น
        time.sleep(10)
        pyautogui.click(x=760, y=526) #กดช่องคอมเม้น
        time.sleep(5)

        comment = self.get_next_comment()
        print(f"💬 กำลังคอมเมนต์ลำดับที่ {self.current_comment_index}: {comment}")
        keyboard.write(comment, delay=0.5)
        print("✅ พิมพ์สำเร็จ")
        time.sleep(3)
        pyautogui.click(x=1153, y=695) #กดส่ง
        time.sleep(15)

        # ล็อกอินเมล
        pyautogui.click(x=1155, y=998)  # เข้า-gmail
        time.sleep(5)
        pyautogui.click(x=821, y=344)  # สลับบัญชี
        time.sleep(5)
        pyautogui.click(x=759, y=398) # ออกจากระบบ
        print("ขั้นตอนที่ 1 เสร็จสิ้น ออกจากเมล")
        time.sleep(15)

        # ขั้นตอนการลบบัญชีที่ค้าง
        pyautogui.click(x=1155, y=998)  # เข้า-gmail
        time.sleep(5)
        pyautogui.click(x=945, y=559) # ลงชื่อเข้าใช้
        time.sleep(15)
        pyautogui.click(x=815, y=650)  # นำบัญชีออก
        time.sleep(5)
        pyautogui,click(x=1136, y=581) # ลบบัญชี
        time.sleep(5)
        pyautogui.click(x=1128, y=636) # ยืนยันการลบบัญชี
        print("ขั้นตอนที่ 2 เสร็จสิ้น ลบเมลทิ้ง")
        time.sleep(15)

        # ขั้นตอนการเข้าสู่ระบบเพื่อดูคลิป
        pyautogui.click(x=804, y=554)
        email, password, backup_email = self.youtube_accounts[self.current_email_index]
        self.current_email_index = (self.current_email_index + 1) % len(self.youtube_accounts)
        # ✅ ใส่อีเมล
        print(f"\n📧 Email: {email}")
        keyboard.write(email)
        time.sleep(10)
        pyautogui.click(x=1111, y=777)  # ถัดไป
        time.sleep(10)
        # ✅ ใส่รหัสผ่านต่อท้าย
        print(f"🔒 Password: {password}")
        keyboard.write(password)
        time.sleep(10)
        pyautogui.click(x=1111, y=777)  # ถัดไป
        print(f"✅ ล็อกอินด้วยอีเมล: {email} และรหัสผ่าน: {password}")

        time.sleep(10)
        pyautogui.click(x=944, y=813) #ดำเนินการนี้ในภายหลัง
        print("ขั้นตอนที่ 3 เข้าสู่ระบบเสร็จสิ้น")
        time.sleep(30)

        #เปลี่ยน ip
        pyautogui.click(x=234, y=1057) #tab net
        time.sleep(5)
        pyautogui.click(x=978, y=368) #connect net
        time.sleep(5)
        pyautogui.click(x=770, y=501)  # connect net
        time.sleep(5)
        pyautogui.click(x=835, y=576)  # connect net
        time.sleep(5)
        pyautogui.click(x=930, y=698)  # login
        time.sleep(5)
        pyautogui.click(x=852, y=166) #กดตั้งค่า
        time.sleep(5)
        pyautogui.click(x=579, y=369) #system
        time.sleep(5)
        pyautogui.click(x=523, y=459) #รีเน็ต
        time.sleep(5)
        pyautogui.click(x=1372, y=346) #รีเนั็ต
        time.sleep(5)
        pyautogui.click(x=1076, y=603) #ยืนยัน
        time.sleep(60)
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(5)
        pyautogui.click(x=510, y=165)  # home
        time.sleep(5)
        pyautogui.click(x=982, y=369)
        time.sleep(5)
        pyautogui.click(x=770, y=501)  # connect net
        time.sleep(5)
        pyautogui.click(x=835, y=576)  # connect net
        time.sleep(5)
        pyautogui.click(x=930, y=698)  # login
        time.sleep(5)
        pyautogui.click(x=510, y=165)  # home
        print(ๅ/"restartnet")
        time.sleep(60)

        bbox = (918, 289, 1049, 314)
        # แคปหน้าจอบริเวณนั้น
        screenshot = ImageGrab.grab(bbox=bbox).convert("L")  # แปลงเป็นขาวดำ
        screenshot = screenshot.point(lambda x: 0 if x < 140 else 255)  # เพิ่ม contrast

        # OCR อ่านข้อความ
        text = pytesseract.image_to_string(screenshot, lang="eng")
        processed_text = text.replace(" ", "").replace("\n", "").strip()

        print(f"ข้อความที่ตรวจพบ: {processed_text}")

        # ถ้าพบคำว่า "Disconnected" ให้คลิก
        if "Disconnected" in processed_text:
            print("🔌 พบ Disconnected! กำลังกดคลิกเพื่อเชื่อมต่อใหม่...")
            pyautogui.click(x=982, y=369)  # แก้พิกัดคลิกตรงนี้ตามที่ต้องการ
            time.sleep(30)
        else:
            print("✅ ไม่พบ Disconnected, ดำเนินการต่อไป...")
            # ทำคำสั่งถัดไปได้ที่นี่

        pyautogui.click(x=808, y=1054)  # blue steacks
        time.sleep(30)



if __name__ == "__main__":
    bot = Mybot()
    while bot.current_email_index < len(bot.youtube_accounts):
        bot.main_process()