const express = require('express');
const { IgApiClient } = require('instagram-private-api');
const axios = require('axios');

const app = express();
const ig = new IgApiClient();

// --- الإعدادات ---
const GROQ_API_KEY = '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';
const IG_USERNAME = 'siham07.07.dz';
const IG_PASSWORD = 'Walid@2009';

// صفحة الويب لمراقبة البوت
app.get('/', (req, res) => {
    res.send('<h1 style="text-align:center;margin-top:50px;">🚀 البوت شغال بـ Groq وراهو يرد في الإنستا!</h1>');
});

// وظيفة جلب الرد من Groq (ChatGPT البديل)
async function getGroqResponse(userText) {
    try {
        const response = await axios.post('https://api.groq.com/openai/v1/chat/completions', {
            model: "llama-3.3-70b-versatile",
            messages: [
                { role: "system", content: "أنت مساعد جزائري مرح، رد دائماً بلهجة جزائرية (دارجة) قصيرة ومفهومة." },
                { role: "user", content: userText }
            ]
        }, {
            headers: {
                'Authorization': `Bearer ${GROQ_API_KEY}`,
                'Content-Type': 'application/json'
            }
        });
        return response.data.choices[0].message.content;
    } catch (err) {
        console.error("خطأ في Groq:", err.message);
        return "صحيت خويا، واش كاين؟";
    }
}

// وظيفة البوت الأساسية
async function startInstagramBot() {
    console.log("جاري تسجيل الدخول لإنستغرام...");
    ig.state.generateDevice(IG_USERNAME);
    await ig.account.login(IG_USERNAME, IG_PASSWORD);
    console.log("✅ متصل الآن بـ " + IG_USERNAME);

    setInterval(async () => {
        try {
            const inbox = await ig.feed.directInbox().items();
            for (const thread of inbox) {
                if (thread.read_state > 0) { // هناك رسالة غير مقروءة
                    const lastMsg = thread.last_permanent_item;
                    // تأكد أن الرسالة نصية وليست من البوت نفسه
                    if (lastMsg.item_type === 'text' && lastMsg.user_id !== ig.state.cookieUserId) {
                        console.log(`📩 رسالة جديدة: ${lastMsg.text}`);
                        
                        // جلب الرد الذكي
                        const reply = await getGroqResponse(lastMsg.text);
                        
                        // إرسال الرد وتحديد الرسالة كمقروءة
                        const threadEntity = ig.entity.directThread(thread.thread_id);
                        await threadEntity.broadcastText(reply);
                        await ig.directThread.markItemSeen(thread.thread_id, lastMsg.item_id);
                        
                        console.log(`📤 تم الرد: ${reply}`);
                    }
                }
            }
        } catch (e) {
            // تجاهل أخطاء الشبكة البسيطة
        }
    }, 15000); // فحص كل 15 ثانية
}

// تشغيل السيرفر والبوت
app.listen(3000, () => {
    console.log("سيرفر الويب جاهز!");
    startInstagramBot().catch(err => {
        console.error("فشل تسجيل الدخول:", err.message);
        if(err.message.includes("challenge_required")) {
            console.log("⚠️ إنستغرام يطلب تأكيد الهوية (Verification). افتح التطبيق وأكد الدخول.");
        }
    });
});