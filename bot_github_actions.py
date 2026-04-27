import feedparser
import requests
import time
import logging
import re
import os
from deep_translator import GoogleTranslator

# --- الإعدادات ---
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
        # ✅ إضافة: طباعة نتيجة الإرسال للتشخيص عند الخطأ
        response = requests.post(url, json=payload, timeout=30)
        print(f"Telegram response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

def clean_html(raw_html):
    if not raw_html: return ""
    return re.sub('<[^<]+?>', '', raw_html)

def get_github_ai_repos():
    """جلب أحدث مشاريع الذكاء الاصطناعي على GitHub بنجوم عالية"""
    try:
        # نبحث عن مشاريع AI أُنشئت مؤخراً وعليها نجوم عالية
        url = "https://api.github.com/search/repositories"
        params = {
            "q": "topic:artificial-intelligence stars:>1000 pushed:>2024-01-01",
            "sort": "updated",
            "order": "desc",
            "per_page": 5
        }
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-News-Bot"
        }
        response = requests.get(url, params=params, headers=headers, timeout=30)
        print(f"GitHub API status: {response.status_code}")
        if response.status_code == 200:
            items = response.json().get("items", [])
            print(f"Found {len(items)} repos")
            return items
        else:
            print(f"GitHub API error: {response.text}")
    except Exception as e:
        print(f"Error fetching GitHub repos: {e}")
    return []

def main():
    sent_articles = load_sent_articles()
    print("Checking for new AI news...")
    
    new_found = False

    # --- قسم الأخبار ---
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
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

    # --- قسم مشاريع GitHub ---
    print("Checking for top AI GitHub repos...")
    repos = get_github_ai_repos()
    for repo in repos:
        repo_url = repo.get("html_url", "")
        if repo_url and repo_url not in sent_articles:
            name = repo.get("name", "")
            description_en = repo.get("description", "") or ""
            stars = repo.get("stargazers_count", 0)
            language = repo.get("language", "غير محدد")
            description_ar = translate_text(description_en[:200]) if description_en else "لا يوجد وصف"

            message = (
                f"⭐ *مشروع ذكاء اصطناعي رائج على GitHub*\n\n"
                f"📦 *{name}*\n\n"
                f"📝 {description_ar}\n\n"
                f"⭐ النجوم: *{stars:,}*\n"
                f"💻 اللغة: {language}\n\n"
                f"🔗 [فتح المشروع]({repo_url})"
            )
            send_telegram_message(message)
            save_sent_article(repo_url)
            new_found = True
            time.sleep(2)

    if not new_found:
        print("No new content found this time.")

if __name__ == "__main__":
    main()
