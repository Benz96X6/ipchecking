from flask import Flask, request
import requests
from datetime import datetime
import os

app = Flask(__name__)

# อ่าน webhook จาก environment variable
DISCORD_WEBHOOK = os.getenv("https://discord.com/api/webhooks/1453051676423618590/-mvVCRBnzPKALk_3WqPx8AKL8vssSXBvOUIicvCfJieCl7EHmgQ_4qqIiJbKcxu1HyaW")
if not DISCORD_WEBHOOK:
    raise ValueError("กรุณาตั้งค่า DISCORD_WEBHOOK ใน environment variable")

def send_to_discord(message):
    data = {"content": message}
    try:
        requests.post(DISCORD_WEBHOOK, json=data, timeout=5)
    except Exception as e:
        print("ส่ง Discord ไม่สำเร็จ:", e)

def get_client_ip():
    # รองรับกรณีอยู่หลัง proxy / cloudflare
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    return request.remote_addr

@app.route("/")
def index():
    ip = get_client_ip()
    user_agent = request.headers.get("User-Agent", "unknown")
    time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    msg = (
        "🌐 มีผู้เข้าเว็บ\n"
        f"IP: {ip}\n"
        f"เวลา: {time}\n"
        f"User-Agent: {user_agent}"
    )

    send_to_discord(msg)

    return """
    <h1>Welcome</h1>
    <p>This website logs IP address for security and monitoring purposes.</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
