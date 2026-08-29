import time
import httpx
from bs4 import BeautifulSoup
import random

# --- আপনার টেলিগ্রাম টোকেন এবং চ্যাট আইডি বসানো আছে ---
TELEGRAM_BOT_TOKEN = "8887958648:AAFxD9U3XzmR4G-dKKNBbfuRRaWqS9ORyb4"  
TELEGRAM_CHAT_ID = "8039516027"      

# ডুপ্লিকেট প্রতিরোধের মেমোরি (একই সাইট বারবার আসবে না)
seen_domains = set()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def send_telegram_alert(domain):
    """শর্ত মিলে গেলে সরাসরি আপনার টেলিগ্রামে নোটিফিকেশন পাঠানোর ফাংশন"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    message = f"🚨 **নতুন ভেরিফাইড সাইট পাওয়া গেছে!**\n\n🌐 ডোমেইন: `{domain}`\n🔗 লিংক: https://{domain}"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = httpx.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"[📲 টেলিগ্রামে পাঠানো হয়েছে]: {domain}", flush=True)
    except Exception as e:
        print(f"[!] টেলিগ্রাম সেন্ড এরর: {e}", flush=True)

def check_single_site(domain):
    """সাইট লাইভ কি না এবং সাইনআপ ও ফোন ভেরিফিকেশন অপশন আছে কি না চেক করা"""
    for proto in ["https", "http"]:
        try:
            url = f"{proto}://{domain}"
            response = httpx.get(url, timeout=3, follow_redirects=True, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text().lower()
                
                # সাইনআপ বা রেজিস্টার কিওয়ার্ড চেক
                has_signup = any(k in page_text for k in ['signup', 'register', 'sign up', 'create account', 'get started'])
                # ফোন বা ওটিপি কিওয়ার্ড চেক
                has_phone = any(k in page_text for k in ['phone', 'mobile', 'sms', 'otp', 'verification', 'verify'])
                
                # ফরম ফিল্ডের ভেতর ফোন বা ওটিপি ইনপুট আছে কি না
                for inp in soup.find_all('input'):
                    inp_str = str(inp).lower()
                    if any(p in inp_str for p in ['phone', 'mobile', 'otp', 'tel', 'sms']):
                        has_phone = True
                        break
                
                if has_signup and has_phone:
                    return True
        except:
            continue
    return False

def generate_domain_stream():
    """ধীরে ধীরে চেক করার জন্য রেন্ডম ডোমেইন প্যাটার্ন জেনারেট করা"""
    base_words = ["shop", "store", "app", "tech", "hub", "zone", "pro", "cloud", "net", "digital", "media", "portal", "auth", "secure", "member", "user", "client"]
    tlds = [".com", ".net", ".org", ".io", ".co", ".xyz"]
    
    while True:
        w1 = random.choice(base_words)
        w2 = random.choice(base_words)
        tld = random.choice(tlds)
        if w1 != w2:
            yield f"{w1}{w2}{tld}"
            yield f"{w1}-{w2}{tld}"
            yield f"portal-{w1}{tld}"

def main():
    print("🤖 ব্যাকগ্রাউন্ড বট ওয়ার্কার চালু হয়েছে...", flush=True)
    domain_stream = generate_domain_stream()
    print("🚀 লাইভ সাইট স্ক্যানিং শুরু হয়েছে...", flush=True)
    
    while True:
        try:
            domain = next(domain_stream)
            
            # ডুপ্লিকেট চেক
            if domain in seen_domains:
                continue
            seen_domains.add(domain)
            
            # লাইভ ও ভেরিফিকেশন চেক
            if check_single_site(domain):
                print(f"[✔] টার্গেট ভেরিফাইড: {domain}", flush=True)
                send_telegram_alert(domain)
            else:
                print(f"[-] বাদ: {domain}", flush=True)
                
            # প্রতি ১০ সেকেন্ড পরপর একটি করে চেক (নিরাপদ ও স্থায়ী স্পিড)
            time.sleep(10)
            
        except Exception as e:
            print(f"[!] লুপ এরর: {e}", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    main()
