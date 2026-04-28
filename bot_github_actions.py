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

# --- مدونات الأدوات المشهورة الرسمية ---
RSS_TOOLS = {
    "ChatGPT / OpenAI": "https://openai.com/news/rss.xml",
    "Claude / Anthropic": "https://www.anthropic.com/rss.xml",
    "Google Gemini": "https://blog.google/technology/ai/rss/",
    "DeepSeek": "https://api.deepseek.com/news/rss.xml",
    "Perplexity": "https://blog.perplexity.ai/rss",
    "Midjourney": "https://updates.midjourney.com/rss",
    "Runway": "https://runwayml.com/blog/rss.xml",
    "Stability AI": "https://stability.ai/news/rss.xml",
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "Mistral AI": "https://mistral.ai/news/rss.xml",
}

# --- أخبار الأتمتة ---
RSS_AUTOMATION = {
    "n8n": "https://blog.n8n.io/rss.xml",
    "Make (Integromat)": "https://www.make.com/en/blog/rss.xml",
    "Zapier": "https://zapier.com/blog/feeds/latest/",
    "LangChain": "https://blog.langchain.dev/rss/",
    "AutoGPT": "https://agpt.co/blog/rss.xml",
}

# --- أخبار عالمية مفلترة ---
RSS_GLOBAL = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://theverge.com/ai-artificial-intelligence/rss/index.xml",
    "https://www.artificialintelligence-news.com/feed/",
    "https://syncedreview.com/feed/",
    "https://www.technologyreview.com/feed/",
    "https://towardsdatascience.com/feed",
    "https://analyticsindiamag.com/feed/",
    "https://www.wired.com/feed/category/ideas/latest/rss",
    "https://bdtechtalks.com/feed/",
]

# --- أخبار عربية مفلترة ---
RSS_ARABIC = [
    "https://aitnews.com/feed/",
    "https://www.tech-wd.com/wd/category/ai/feed/",
    "https://www.arageek.com/feed",
    "https://dotmsr.com/feed",
    "https://www.arabicera.com/feed/",
    "https://3arb.net/feed/",
    "https://www.gulf-techno.com/feed/",
    "https://www.masrawy.com/tech/rss",
    "https://www.digital-x.net/feed/",
    "https://www.techradar.com/rss",
]

# --- كلمات مفتاحية للفلترة ---
AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "chatgpt", "claude", "gemini", "llm", "gpt", "model", "tool",
    "automation", "workflow", "api", "feature", "update", "launch",
    "release", "new", "مجاني", "ذكاء", "اصطناعي", "أداة", "تحديث",
    "ميزة", "إطلاق", "نموذج", "أتمتة", "مجانية", "برمجة",
    "n8n", "zapier", "make", "midjourney", "runway", "sora", "deepseek",
    "perplexity", "ollama", "stable diffusion", "python", "freelance"
]

# --- مواضيع GitHub ---
GITHUB_TOPICS = [
    "topic:llm stars:>500",
    "topic:ai-tools stars:>500",
    "topic:automation stars:>500",
    "topic:chatbot stars:>500",
    "topic:n8n stars:>200",
    "topic:ollama stars:>200",
    "topic:stable-diffusion stars:>500",
    "topic:langchain stars:>300",
    "topic:python-ai stars:>300",
    "topic:free-ai-tools stars:>200",
]

DB_FILE = "sent_articles.txt"

def load_sent():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return set(line.strip() for line in f)
    return set()

def save_sent(link):
    with open(DB_FILE, "a") as f:
        f.write(link + "\n")

def translate(text):
    try:
        if not text: return ""
        return GoogleTranslator(source='auto', target='ar').translate(text[:400])
    except:
        return text

def send(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }, timeout=30)
        print(f"✅ Sent: {r.status_code}")
        time.sleep(1)
    except Exception as e:
        print(f"❌ Error: {e}")

def clean(text):
    if not text: return ""
    text = re.sub('<[^<]+?>', '', text)
    return text.strip()[:300]

def is_relevant(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in AI_KEYWORDS)

# ==========================================
# 1. تحديثات الأدوات المشهورة
# ==========================================
def fetch_tools_news():
    print("\n🔧 جلب تحديثات الأدوات المشهورة...")
    sent = load_sent()
    for tool_name, feed_url in RSS_TOOLS.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:
                if entry.link not in sent:
                    title_ar = translate(entry.title)
                    summary_ar = translate(clean(entry.get('summary', '')))
                    msg = (
                        f"🔧 *تحديث جديد — {tool_name}*\n\n"
                        f"📌 *{title_ar}*\n\n"
                        f"📝 {summary_ar}...\n\n"
                        f"🔗 [اقرأ التفاصيل]({entry.link})"
                    )
                    send(msg)
                    save_sent(entry.link)
                    time.sleep(2)
        except Exception as e:
            print(f"Error {tool_name}: {e}")

# ==========================================
# 2. أخبار الأتمتة
# ==========================================
def fetch_automation_news():
    print("\n⚙️ جلب أخبار الأتمتة...")
    sent = load_sent()
    for tool_name, feed_url in RSS_AUTOMATION.items():
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:2]:
                if entry.link not in sent:
                    title_ar = translate(entry.title)
                    summary_ar = translate(clean(entry.get('summary', '')))
                    msg = (
                        f"⚙️ *أتمتة جديدة — {tool_name}*\n\n"
                        f"📌 *{title_ar}*\n\n"
                        f"📝 {summary_ar}...\n\n"
                        f"🔗 [اقرأ التفاصيل]({entry.link})"
                    )
                    send(msg)
                    save_sent(entry.link)
                    time.sleep(2)
        except Exception as e:
            print(f"Error {tool_name}: {e}")

# ==========================================
# 3. أخبار عالمية مفلترة
# ==========================================
def fetch_global_news():
    print("\n🌍 جلب الأخبار العالمية المفلترة...")
    sent = load_sent()
    for feed_url in RSS_GLOBAL:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:
                if entry.link not in sent and is_relevant(entry.title + entry.get('summary', '')):
                    title_ar = translate(entry.title)
                    summary_ar = translate(clean(entry.get('summary', '')))
                    msg = (
                        f"🌍 *خبر عالمي مفيد*\n\n"
                        f"📌 *{title_ar}*\n\n"
                        f"📝 {summary_ar}...\n\n"
                        f"🔗 [اقرأ التفاصيل]({entry.link})"
                    )
                    send(msg)
                    save_sent(entry.link)
                    time.sleep(2)
        except Exception as e:
            print(f"Error {feed_url}: {e}")

# ==========================================
# 4. أخبار عربية مفلترة
# ==========================================
def fetch_arabic_news():
    print("\n🌐 جلب الأخبار العربية المفلترة...")
    sent = load_sent()
    for feed_url in RSS_ARABIC:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:3]:
                if entry.link not in sent and is_relevant(entry.title + entry.get('summary', '')):
                    summary = clean(entry.get('summary', ''))
                    msg = (
                        f"🌐 *خبر عربي مفيد*\n\n"
                        f"📌 *{entry.title}*\n\n"
                        f"📝 {summary}...\n\n"
                        f"🔗 [اقرأ التفاصيل]({entry.link})"
                    )
                    send(msg)
                    save_sent(entry.link)
                    time.sleep(2)
        except Exception as e:
            print(f"Error {feed_url}: {e}")

# ==========================================
# 5. مشاريع وأدوات GitHub
# ==========================================
def fetch_github_projects():
    print("\n⭐ جلب مشاريع GitHub...")
    sent = load_sent()
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "AI-News-Bot"}

    for topic_query in GITHUB_TOPICS:
        try:
            params = {
                "q": f"{topic_query} pushed:>2024-01-01",
                "sort": "updated",
                "order": "desc",
                "per_page": 3
            }
            r = requests.get("https://api.github.com/search/repositories",
                           params=params, headers=headers, timeout=30)
            if r.status_code == 200:
                for repo in r.json().get("items", []):
                    url = repo.get("html_url", "")
                    if url and url not in sent:
                        name = repo.get("name", "")
                        desc = translate(repo.get("description", "") or "لا يوجد وصف")
                        stars = repo.get("stargazers_count", 0)
                        lang = repo.get("language", "غير محدد")
                        topics = ", ".join(repo.get("topics", [])[:3])
                        msg = (
                            f"⭐ *مشروع مفيد على GitHub*\n\n"
                            f"📦 *{name}*\n\n"
                            f"📝 {desc}\n\n"
                            f"⭐ النجوم: *{stars:,}*\n"
                            f"💻 اللغة: {lang}\n"
                            f"🏷️ المواضيع: {topics}\n\n"
                            f"🔗 [فتح المشروع]({url})"
                        )
                        send(msg)
                        save_sent(url)
                        time.sleep(2)
            time.sleep(3)  # تفادي حد GitHub API
        except Exception as e:
            print(f"GitHub error {topic_query}: {e}")

# ==========================================
# 6. دروس Python وفرص العمل (مرة يومياً)
# ==========================================
def fetch_learning_and_jobs():
    sent = load_sent()
    today = f"learning_{datetime.date.today().isoformat()}"
    if today in sent:
        return
    print("\n📚 جلب دروس وفرص العمل...")

    LEARNING_FEEDS = [
        ("https://realpython.com/atom.xml", "📚 درس Python"),
        ("https://www.freecodecamp.org/news/tag/python/rss/", "📚 درس مجاني"),
        ("https://towardsdatascience.com/feed", "📊 ذكاء اصطناعي تعليمي"),
    ]

    JOBS_FEEDS = [
        ("https://weworkremotely.com/categories/remote-ai-jobs.rss", "💼 فرصة عمل عن بعد"),
        ("https://remoteok.com/remote-ai-jobs.rss", "💼 وظيفة AI عن بعد"),
    ]

    all_feeds = LEARNING_FEEDS + JOBS_FEEDS
    for feed_url, label in all_feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:1]:
                if entry.link not in sent:
                    title_ar = translate(entry.title)
                    summary_ar = translate(clean(entry.get('summary', '')))
                    msg = (
                        f"{label}\n\n"
                        f"📌 *{title_ar}*\n\n"
                        f"📝 {summary_ar}...\n\n"
                        f"🔗 [افتح الرابط]({entry.link})"
                    )
                    send(msg)
                    save_sent(entry.link)
                    time.sleep(2)
        except Exception as e:
            print(f"Error learning {feed_url}: {e}")

    save_sent(today)

# ==========================================
# التشغيل الرئيسي
# ==========================================
def main():
    print("=" * 40)
    print("🤖 بدء تشغيل بوت الذكاء الاصطناعي")
    print(f"⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 40)

    fetch_tools_news()       # تحديثات الأدوات المشهورة
    fetch_automation_news()  # أخبار الأتمتة
    fetch_global_news()      # أخبار عالمية مفلترة
    fetch_arabic_news()      # أخبار عربية مفلترة
    fetch_github_projects()  # مشاريع وأدوات GitHub
    fetch_learning_and_jobs() # دروس وفرص عمل (يومياً)

    print("\n✅ انتهى التشغيل بنجاح!")

if __name__ == "__main__":
    main()
