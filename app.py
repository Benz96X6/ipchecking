from flask import Flask, request
import requests
from datetime import datetime
import pytz
from user_agents import parse  # เพิ่มบรรทัดนี้

app = Flask(__name__)

# เปลี่ยนเป็น Discord Webhook URL ของคุณ
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1453051676423618590/-mvVCRBnzPKALk_3WqPx8AKL8vssSXBvOUIicvCfJieCl7EHmgQ_4qqIiJbKcxu1HyaW"

# ตั้ง timezone เป็นไทย
tz = pytz.timezone('Asia/Bangkok')

def get_client_ip():
    """ดึง IP จริง แม้อยู่หลัง Cloudflare หรือ proxy"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def send_to_discord(ip, user_agent_str, page, timestamp):
    # Parse User-Agent เพื่อดึง device info
    ua = parse(user_agent_str)
    device_model = ua.device.family  # เช่น iPhone, Samsung Galaxy
    os = ua.os.family  # เช่น iOS, Android
    browser = ua.browser.family  # เช่น Chrome, Safari
    
    # ถ้าต้องการ detail มากขึ้น (model เฉพาะ) ใช้ ua.device.model แต่ไม่เสมอไป
    full_device = f"{device_model} ({os})" if device_model != 'Other' else os

    message = (
        "**มีคนเข้าเว็บไซต์!**\n"
        f"**IP:** `{ip}`\n"
        f"**เวลา:** {timestamp}\n"
        f"**หน้า:** {page}\n"
        f"**อุปกรณ์:** {full_device}\n"
        f"**เบราว์เซอร์:** {browser}\n"
        f"**User-Agent:** {user_agent_str[:100]}..."  # ตัดสั้น ๆ เพื่อไม่ให้ยาวเกิน
    )
    
    data = {"content": message}
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        if response.status_code != 204:
            print(f"ส่ง Discord ไม่สำเร็จ: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error ส่ง Discord: {e}")

@app.route('/')
def home():
    ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    page = request.path or '/'
    timestamp = datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
    
    # ส่งไป Discord
    send_to_discord(ip, user_agent, page, timestamp)
    
    # แสดงหน้าเว็บธรรมดา
    return """
    <h1>ยินดีต้อนรับ!</h1>
    <p>เว็บนี้กำลัง track ผู้เยี่ยมชมอย่างเงียบ ๆ นะจ๊ะ 😏</p>
        """

# ถ้าอยาก track ทุกหน้า
@app.route('/<path:path>')
def catch_all(path):
    ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    page = '/' + path
    timestamp = datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
    
    send_to_discord(ip, user_agent, page, timestamp)
    
    return "หน้าไม่พบ หรือคุณสามารถ redirect ไปหน้าเว็บจริงของคุณได้ที่นี่", 200

if __name__ == '__main__':
    # รันบน localhost พอร์ต 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
