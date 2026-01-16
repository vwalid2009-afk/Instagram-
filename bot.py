import os
import time
from threading import Thread
from flask import Flask
from instagrapi import Client
import google.generativeai as genai

# --- 1. إعداد خادم صغير لبقاء البوت يعمل 24 ساعة ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive! Bot is running..."

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# --- 2. إعداد الذكاء الاصطناعي (Gemini) ---
GEMINI_API_KEY = os.environ.get('AIzaSyBby1cMPsuVcSuG4KOxhBABXxoay17VACg')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- 3. إعداد إنستغرام ---
USERNAME = os.environ.get('siham07.07.dz')
PASSWORD = os.environ.get('Walid@2009b')
cl = Client()

def start_bot():
    keep_alive() # تشغيل السيرفر لضمان البقاء متصلاً
    
    print("جاري تسجيل الدخول إلى إنستغرام...")
    try:
        cl.login(USERNAME, PASSWORD)
        print("تم الاتصال بنجاح! البوت يراقب الرسائل الآن...")
    except Exception as e:
        print(f"خطأ في الدخول: {e}")
        return

    while True:
        try:
            # البحث عن رسائل غير مقروءة (Unseen)
            threads = cl.direct_threads(unseen=True)
            
            for thread in threads:
                thread_id = thread.id
                # الحصول على آخر رسالة في المحادثة
                messages = cl.direct_messages(thread_id, amount=1)
                if not messages:
                    continue
                    
                last_msg = messages[0]
                
                # التأكد أنها رسالة نصية وليست من البوت نفسه
                if last_msg.item_type == 'text' and last_msg.user_id != cl.user_id:
                    user_query = last_msg.text
                    print(f"رسالة جديدة من {last_msg.user_id}: {user_query}")

                    # توليد رد باستعمال جيميناي
                    # ملاحظة: يمكنك تغيير "البرومبت" ليكون الرد بلهجة معينة
                    prompt = f"أجب على هذه الرسالة بلهجة جزائرية خفيفة وودودة: {user_query}"
                    response = model.generate_content(prompt)
                    bot_reply = response.text

                    # إرسال الرد
                    cl.direct_send(bot_reply, thread_ids=[thread_id])
                    print(f"تم الرد: {bot_reply}")
                    
                    # وضع علامة "مقروء" لكي لا يعيد الرد عليها
                    cl.direct_thread_mark_as_seen(thread_id)

            # انتظر دقيقة قبل الفحص التالي لتجنب الحظر
            time.sleep(60)
            
        except Exception as e:
            print(f"حدث خطأ أثناء التشغيل: {e}")
            time.sleep(30) # انتظر قليلاً وأكمل

if __name__ == "__main__":
    start_bot()
