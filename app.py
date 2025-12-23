from flask import Flask, request
import requests
from datetime import datetime
import pytz

app = Flask(__name__)

# เปลี่ยนเป็น Discord Webhook URL ของคุณ
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1453051676423618590/-mvVCRBnzPKALk_3WqPx8AKL8vssSXBvOUIicvCfJieCl7EHmgQ_4qqIiJbKcxu1HyaW"

# ตั้ง timezone เป็นไทย
tz = pytz.timezone('Asia/Bangkok')

def get_client_ip():
    """ดึง IP จริง แม้อยู่หลัง Cloudflare หรือ proxy"""
    if request.headers.get('X-Forwarded-For'):
        # X-Forwarded-For อาจมีหลาย IP (comma separated) ตัวแรกคือ IP จริง
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def send_to_discord(ip, user_agent, page, timestamp):
    message = (
        "**มีคนเข้าเว็บไซต์!**\n"
        f"**IP:** `{ip}`\n"
        f"**เวลา:** {timestamp}\n"
        f"**หน้า:** {page}\n"
        f"**เบราว์เซอร์:** {user_agent}"
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
    
    # ส่งไป Discord (ทำแบบ asynchronous ใน production จะดีกว่า แต่ตัวอย่างนี้เรียบง่าย)
    send_to_discord(ip, user_agent, page, timestamp)
    
    # แสดงหน้าเว็บธรรมดา (คุณเปลี่ยนเป็น HTML สวย ๆ ได้)
    return """
    <h1>ยินดีต้อนรับ!</h1>
    <p>เว็บนี้กำลัง track ผู้เยี่ยมชมอย่างเงียบ ๆ 😏</p>
    <p></p>
    """

# ถ้าอยาก track ทุกหน้า ไม่ใช่แค่ /
@app.route('/<path:path>')
def catch_all(path):
    ip = get_client_ip()
    user_agent = request.headers.get('User-Agent', 'Unknown')
    page = '/' + path
    timestamp = datetime.now(tz).strftime('%d/%m/%Y %H:%M:%S')
    
    send_to_discord(ip, user_agent, page, timestamp)
    
    return "หน้าไม่พบ หรือคุณสามารถ redirect ไปหน้าเว็บจริงของคุณได้ที่นี่", 200

if __name__ == '__main__':
    # รันบน localhost พอร์ต 5000 (เปลี่ยน host เป็น 0.0.0.0 ถ้าจะให้คนอื่นเข้าถึง)
    app.run(host='0.0.0.0', port=5000, debug=True)
