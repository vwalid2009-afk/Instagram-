import os
import time
from threading import Thread
from flask import Flask
from instagrapi import Client
import google.generativeai as genai

# --- 1. إعداد Flask (Port 5000 للعمل على Replit) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive! Bot is running..."

def run_flask():
    # Replit يستخدم غالباً المنفذ 5000 أو 8080
    app.run(host='0.0.0.0', port=5000)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- 2. بيانات الاعتماد (التي زودتني بها) ---
GEMINI_API_KEY = "AIzaSyBby1cMPsuVcSuG4KOxhBABXxoay17VACg"
INSTA_USERNAME = "siham07.07.dz"
INSTA_PASSWORD = "Walid@2009b"

# إعداد جيميناي
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# إعداد إنستغرام
cl = Client()

def start_bot():
    keep_alive() # تشغيل خادم الويب للبقاء حياً
    
    print(f"جاري محاولة تسجيل الدخول للحساب: {INSTA_USERNAME}...")
    try:
        cl.login(INSTA_USERNAME, INSTA_PASSWORD)
        print("✅ تم تسجيل الدخول بنجاح! البوت يراقب الرسائل الآن...")
    except Exception as e:
        print(f"❌ خطأ في الدخول: {e}")
        return

    while True:
        try:
            # البحث عن رسائل غير مقروءة
            threads = cl.direct_threads(unseen=True)
            
            if threads:
                print(f"تم العثور على {len(threads)} محادثة جديدة.")
            
            for thread in threads:
                thread_id = thread.id
                # جلب آخر رسالة
                messages = cl.direct_messages(thread_id, amount=1)
                if not messages:
                    continue
                    
                last_msg = messages[0]
                
                # التأكد أنها رسالة نصية وليست من البوت
                if last_msg.item_type == 'text' and last_msg.user_id != cl.user_id:
                    user_query = last_msg.text
                    print(f"📩 رسالة من {INSTA_USERNAME}: {user_query}")

                    # طلب الرد من جيميناي
                    prompt = f"أجب على هذه الرسالة بلهجة جزائرية ودودة وقصيرة: {user_query}"
                    response = model.generate_content(prompt)
                    bot_reply = response.text

                    # إرسال الرد
                    cl.direct_send(bot_reply, thread_ids=[thread_id])
                    print(f"📤 تم الرد بـ: {bot_reply}")
                    
                    # وضع علامة مقروء
                    cl.direct_thread_mark_as_seen(thread_id)

            # انتظر دقيقة قبل الفحص التالي
            time.sleep(60)
            
        except Exception as e:
            print(f"⚠️ تنبيه: حدث خطأ بسيط أثناء التشغيل (سيحاول البوت الاستمرار): {e}")
            time.sleep(30)

if __name__ == "__main__":
    start_bot()
