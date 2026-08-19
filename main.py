import os
import json
import requests
import feedparser
from datetime import datetime
import pytz

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://venturebeat.com/category/ai/feed/",
    "https://news.ycombinator.com/rss"
]

def fetch_articles():
    articles = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                title = entry.get('title', '')
                link = entry.get('link', '')
                summary = entry.get('summary', '') or entry.get('description', '')
                if title and link:
                    # Clean up HTML tags if present
                    clean_summary = summary.replace('<p>', '').replace('</p>', '')[:200]
                    articles.append(f"Title: {title}\nSummary: {clean_summary}\nLink: {link}")
        except Exception as e:
            print(f"Error reading {url}: {e}")
    return "\n\n".join(articles[:15])

def summarize_with_gemini(raw_text):
    ist = pytz.timezone('Asia/Kolkata')
    today_str = datetime.now(ist).strftime('%A, %B %d, %Y')
   
    prompt = f"""You are an elite Tech & AI Analyst. Analyze the following articles collected this morning:
{raw_text}
Format the output into a beautifully structured, easy-to-read Telegram briefing. Follow this exact layout:
🌅 *DAILY TECH & AI BRIEFING*
📅 {today_str}
━━━━━━━━━━━━━━━━━━━
🔥 *TOP 3 BREAKTHROUGHS*
1️⃣ *[Short Catchy Headline]*
• *Impact:* [1-2 concise sentences explaining what happened and why it matters].
• 🔗 [Read Source](url)
2️⃣ *[Short Catchy Headline]*
• *Impact:* [1-2 concise sentences explaining what happened and why it matters].
• 🔗 [Read Source](url)
3️⃣ *[Short Catchy Headline]*
• *Impact:* [1-2 concise sentences explaining what happened and why it matters].
• 🔗 [Read Source](url)
━━━━━━━━━━━━━━━━━━━
⚡ *DEVELOPER & ECOSYSTEM TRENDS*
• *[Trend 1 Name]:* [1-sentence takeaway or tooling update].
• *[Trend 2 Name]:* [1-sentence takeaway or framework release].
• *[Trend 3 Name]:* [1-sentence takeaway].
━━━━━━━━━━━━━━━━━━━
💡 *WHAT YOU MIGHT HAVE MISSED*
• *[Niche Topic 1]:* [1-2 sentence under-the-radar insight or key takeaway].
• *[Niche Topic 2]:* [1-2 sentence under-the-radar insight or key takeaway].
━━━━━━━━━━━━━━━━━━━
Rules:
- Add double line breaks between sections and items for clean spacing on mobile.
- Embed article links cleanly as [Read Source](url) instead of showing long raw URLs.
- Avoid large blocks of unbroken text.
"""
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
   
    resp = requests.post(api_url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data['candidates'][0]['content']['parts'][0]['text']

def send_telegram(text):
    tg_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    resp = requests.post(tg_url, json=payload, timeout=15)
    resp.raise_for_status()

if __name__ == "__main__":
    print("Fetching RSS feeds...")
    raw_articles = fetch_articles()
   
    if not raw_articles:
        print("No articles fetched.")
        exit(1)
       
    print("Summarizing with Gemini...")
    summary = summarize_with_gemini(raw_articles)
   
    print("Sending to Telegram...")
    send_telegram(summary)
    print("Briefing successfully delivered to Telegram!")
