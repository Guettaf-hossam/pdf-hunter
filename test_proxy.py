import os
import requests
from dotenv import load_dotenv

load_dotenv()

# استخدمنا المنفذ 10001 كما في إيميل إسحاق ولوحة التحكم
PROXY_USER = os.getenv("TEST_PROXY_USER", "")
PROXY_PASS = os.getenv("PROXY_PASS", "")
PROXY_HOST = os.getenv("PROXY_HOST", "") # تأكد من أن هذا هو الرابط الصحيح في لوحتك (أحيانا يكون pr.anyip.io)
PROXY_PORT = os.getenv("TEST_PROXY_PORT", "") 

proxy_url = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
proxies = {"http": proxy_url, "https": proxy_url}

print(f"Testing proxy on port {PROXY_PORT}...")
try:
    response = requests.get("https://api.ipify.org", proxies=proxies, timeout=10)
    print(f"🌍 Success! IP seen by the world: {response.text}")
except Exception as e:
    print(f"❌ Connection Failed: {e}")