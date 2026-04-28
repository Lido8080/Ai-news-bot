import feedparser
import requests
import time
import re
import os
import datetime
from deep_translator import GoogleTranslator

# --- الإعدادات ---
TOKEN = "8665699009:AAFodvJuv5aw6yifWs1I7EBd5ZXhiF4VOHI"
CHAT_ID = "1934770017"

# --- 10 مصادر عالمية ---
RSS_FEEDS_EN = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.artificialintelligence-news.com/feed/",
    "https://theverge.com/ai-artificial-intelligence/rss/index.xml",
    "https://openai.com/news/rss.xml",
    "https://www.wired.com/feed/category/ideas/latest/rss",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.technologyreview.com/feed/",
    "https://syncedreview.com/feed/",
    "https://analyticsindiamag.com/feed/",
    "https://towardsdatascience.com/feed",
]

# --- 10 مصادر عربية ---
RSS_FEEDS_AR = [
    "https://aitnews.com/feed/",
    "https://www.tech-wd.com/wd/category/ai/feed/",
    "https://3arb.net/feed/",
    "https://www.arabicera.com/feed/",
    "https://dotmsr.com/feed",
    "https://www.masrawy.com/tech/rss",
    "https://www.youm7.com/rss/Section/تكنولوجيا-وعلوم",
    "https://www.gulf-techno.com/feed/",
    "https://www.arageek.com/feed",
    "https://www.digitaltrends.com/feed/",
]

# --- أدوات الذكاء الاصطناعي ---
AI_TOOLS = {
    "🎨 أدوات تصميم الصور": [
        ("Midjourney", "https://www.midjourney.com", "توليد صور احترافية"),
        ("DALL-E 3", "https://openai.com/dall-e-3", "توليد صور من OpenAI"),
        ("Stable Diffusion", "https://stability.ai", "مجاني ومفتوح المصدر"),
        ("Adobe Firefly", "https://firefly.adobe.com", "تصميم احترافي مجاني"),
        ("Canva AI", "https://www.canva.com/ai-image-generator", "سهل ومجاني"),
    ],
    "🎬 أدوات تصميم الفيديو": [
        ("Runway", "https://runwayml.com", "توليد فيديو احترافي"),
        ("Pika Labs", "https://pika.art", "تحويل النص لفيديو مجاناً"),
        ("Sora", "https://sora.com", "أحدث أداة من OpenAI"),
        ("Kling AI", "https://klingai.com", "توليد فيديو مجاني"),
        ("HeyGen", "https://www.heygen.com", "فيديوهات بالذكاء الاصطناعي"),
    ],
    "🤖 أدوات ذكاء اصطناعي مجانية": [
        ("ChatGPT", "https://chat.openai.com", "محادثة وكتابة مجانية"),
        ("Claude", "https://claude.ai", "محادثة وتحليل مجاني"),
        ("Gemini", "https://gemini.google.com", "ذكاء اصطناعي Google مجاني"),
        ("Perplexity", "https://www.perplexity.ai", "بحث بالذكاء الاصطناعي"),
        ("Hugging Face", "https://huggingface.co/spaces", "آلاف الأدوات المجانية"),
    ],
}

DB_FILE = "sent_articles.txt"

def load_sent_articles():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return set(line.strip() for line in f)
    return set()

def save_sent_article(link):
    with open(DB_FILE, "a") as f:
        f.write(link + "\n")

def translate_text(text):
    try:
        if not text: return ""
        return GoogleTranslator(source='auto', target='ar').translate(text[:500])
    except:
        return text

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=30)
        print(f"Sent: {r.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def clean_html(text):
    if not text: return ""
    return re.sub('<[^<]+?>', '', text)

def fetch_news():
    sent = load_sent_articles()

    # أخبار عالمية
    for feed_url in RSS_FEEDS_EN:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:2]:
                if entry.link not in sent:
                    title = translate_text(entry.title)
                    summary = translate_text(clean_html(entry.get('summary', ''))[:200])
                    send_message(f"🌍 *خبر عالمي في الذكاء الاصطناعي*\n\n📌 *{title}*\n\n📝 {summary}...\n\n🔗 [المصدر]({entry.link})")
                    save_sent_article(entry.link)
                    time.sleep(2)
        except Exception as e:
            print(f"Error {feed_url}: {e}")

    # أخبار عربية
    for feed_url in RSS_FEEDS_AR:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:2]:
                if entry.link not in sent:
                    summary = clean_html(entry.get('summary', ''))[:200]
                    send_message(f"🌐 *خبر عربي في الذكاء الاصطناعي*\n\n📌 *{entry.title}*\n\n📝 {summary}...\n\n🔗 [المصدر]({entry.link})")
                    save_sent_article(entry.link)
                    time.sleep(2)
        except Exception as e:
            print(f"Error {feed_url}: {e}")

def fetch_github_repos():
    sent = load_sent_articles()
    try:
        url = "https://api.github.com/search/repositories"
        params = {"q": "topic:artificial-intelligence stars:>1000 pushed:>2024-01-01", "sort": "updated", "order": "desc", "per_page": 5}
        headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "AI-News-Bot"}
        r = requests.get(url, params=params, headers=headers, timeout=30)
        if r.status_code == 200:
            for repo in r.json().get("items", []):
                repo_url = repo.get("html_url", "")
                if repo_url and repo_url not in sent:
                    desc = translate_text(repo.get("description", "") or "لا يوجد وصف")
                    stars = repo.get("stargazers_count", 0)
                    lang = repo.get("language", "غير محدد")
                    send_message(f"⭐ *مشروع ذكاء اصطناعي على GitHub*\n\n📦 *{repo['name']}*\n\n📝 {desc}\n\n⭐ النجوم: *{stars:,}*\n💻 اللغة: {lang}\n\n🔗 [فتح المشروع]({repo_url})")
                    save_sent_article(repo_url)
                    time.sleep(2)
    except Exception as e:
        print(f"GitHub error: {e}")

def send_ai_tools():
    sent = load_sent_articles()
    today = f"ai_tools_{datetime.date.today().isoformat()}"
    if today in sent:
        return
    for category, tools in AI_TOOLS.items():
        msg = f"*{category}*\n\n"
        for name, url, desc in tools:
            msg += f"• [{name}]({url}) — {desc}\n"
        send_message(msg)
        time.sleep(2)
    save_sent_article(today)

def main():
    print("=== تشغيل البوت ===")
    fetch_news()
    fetch_github_repos()
    send_ai_tools()
    print("=== انتهى ===")

if __name__ == "__main__":
    main()
