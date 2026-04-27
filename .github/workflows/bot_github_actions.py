import feedparser
import requests
import time
import logging
import re
import os
from deep_translator import GoogleTranslator

# --- الإعدادات ---
# ملاحظة: سنستخدم "Secrets" في GitHub لحماية التوكن، أو نضعه هنا مباشرة كما طلبت
TOKEN = "8665699009:AAFodvJuv5aw6yifWs1I7EBd5ZXhiF4VOHI"
CHAT_ID = "1934770017"

RSS_FEEDS = [
    "https://www.wired.com/feed/category/ideas/latest/rss",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.artificialintelligence-news.com/feed/",
    "https://theverge.com/ai-artificial-intelligence/rss/index.xml",
    "https://openai.com/news/rss.xml"
]

# ملف لتخزين الأخبار المرسلة (سيتم حفظه في GitHub)
DB_FILE = "sent_articles.txt"

def load_sent_articles():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return set(line.strip() for line in f)
    return set()

def save_sent_article(link):
    with open(DB_FILE, "a") as f:
        f.write(link + "\n")

def translate_text(text, target_lang='ar'):
    try:
        if not text: return ""
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except:
        return text

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=30)
    except Exception as e:
        print(f"Error: {e}")

def clean_html(raw_html):
    if not raw_html: return ""
    return re.sub('<[^<]+?>', '', raw_html)

def main():
    sent_articles = load_sent_articles()
    print("Checking for new AI news...")
    
    new_found = False
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            # نأخذ آخر خبرين فقط من كل مصدر في كل فحص (لأن الفحص متكرر)
            for entry in feed.entries[:2]:
                if entry.link not in sent_articles:
                    title_ar = translate_text(entry.title)
                    summary_en = clean_html(entry.get('summary', entry.get('description', '')))[:200]
                    summary_ar = translate_text(summary_en)
                    
                    message = (
                        f"🆕 *خبر جديد في الذكاء الاصطناعي*\n\n"
                        f"📌 *{title_ar}*\n\n"
                        f"📝 {summary_ar}...\n\n"
                        f"🔗 [المصدر الأصلي]({entry.link})"
                    )
                    send_telegram_message(message)
                    save_sent_article(entry.link)
                    new_found = True
                    time.sleep(2)
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")
    
    if not new_found:
        print("No new news found this time.")

if __name__ == "__main__":
    main()
