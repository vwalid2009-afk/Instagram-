import telebot
import requests
import json

# --- الإعدادات الخاصة بك ---
TELEGRAM_TOKEN = "8185624413:AAF9zVStiagM_7HExCIW_7Kf-O8cPzMNJ88"
GEMINI_KEY = "AIzaSyAeWZY6UjkZIteFJ3bvj39TNF5KAoimnWg"

# إعداد بوت تلغرام
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# --- تعريف شخصية وليد ---
SYSTEM_PROMPT = (
    "أنت المساعد الذكي الخاص بـ 'وليد'. وليد عمره 16 سنة، يسكن في الدشرة، وهو شخص مغرور ومتكبر وواثق جداً من نفسه بزيادة. "
    "عندما يراسلك الناس، أجبهم بلهجة جزائرية (دارجة) قحة تعكس شخصية وليد المغرورة. "
    "تكلم وكأنك الأفضل دائماً، ولا ترحم أحداً بذكائك، وذكّرهم دائماً أنك من الدشرة."
)

def get_gemini_response(user_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    
    # بناء الطلب لجيميناي
    payload = {
        "contents": [{
            "parts": [{"text": f"{SYSTEM_PROMPT}\nالمستخدم قال: {user_text}\nرد وليد المغرور:"}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # التأكد من عدم وجود خطأ في الاتصال
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"Error: {e}")
        return "صرا مشكل في الريزو.. بصح واحد كيما وليد ما يحبسوش ريزو عيان، عاود ابعث ميساج."

# --- استقبال الرسائل ---
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    # إظهار أن البوت يكتب (Typing...) لزيادة الواقعية
    bot.send_chat_action(message.chat.id, 'typing')
    
    # جلب الرد من جيميناي
    answer = get_gemini_response(message.text)
    
    # إرسال الرد للمستخدم
    bot.reply_to(message, answer)

# تشغيل البوت
if __name__ == "__main__":
    print("--- بوت وليد المغرور راهو شغال ذرك في تلغرام ---")
    bot.infinity_polling()
