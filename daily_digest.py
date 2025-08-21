import feedparser
import openai
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# === CONFIG ===
RSS_FEEDS = [
    "https://techcrunch.com/tag/artificial-intelligence/feed/",
    "https://www.wired.com/feed/category/science/ai/rss",
    "https://arxiv.org/rss/cs.AI",
    "https://venturebeat.com/category/ai/feed/",
    "https://www.nvidia.com/en-us/research/feed/",
    "https://news.mit.edu/rss/topic/artificial-intelligence2",
    "https://www.nature.com/subjects/artificial-intelligence.rss"
]

KEYWORDS = ["AI", "agent", "automation", "no-code", "low-code", "developer", "LLM", "frontier", "quantum"]

# OpenAI API key (store as GitHub secret)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Email settings (store sensitive info as GitHub secrets)
OUTLOOK_EMAIL = os.getenv("OUTLOOK_EMAIL")
OUTLOOK_PASSWORD = os.getenv("OUTLOOK_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

# === FUNCTIONS ===
def fetch_rss_items(feeds, keywords):
    items = []
    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get('title', '')
            summary = entry.get('summary', '')
            link = entry.get('link', '')
            if any(k.lower() in (title + summary).lower() for k in keywords):
                items.append({"title": title, "link": link})
    return items[:10]

def summarize_items(items):
    if not items:
        return "No relevant updates today."
    
    prompt = "You are 'Frontier Daily' — a daily digest for startup founders and investors.\n" \
             "Select the 2–3 most relevant updates in emerging tech (AI, agentic systems, no/low-code, developer platforms, quantum, frontier tech). " \
             "Summarise each in ≤2 sentences, founder-focused, practical, with the original link included.\n" \
             "End with one 'Explore further' suggestion (a tool or trend worth deeper look). " \
             "Tone: professional, concise, UK spelling.\n\n" \
             "News items:\n" + "\n".join([f"- {item['title']} — {item['link']}" for item in items])

    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=600
    )
    return response['choices'][0]['message']['content']

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = OUTLOOK_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(OUTLOOK_EMAIL, OUTLOOK_PASSWORD)
        server.send_message(msg)

# === MAIN ===
if __name__ == "__main__":
    items = fetch_rss_items(RSS_FEEDS, KEYWORDS)
    digest = summarize_items(items)
    subject = f"🛰️ Frontier Daily — {datetime.now().strftime('%Y-%m-%d')}"
    send_email(subject, digest)
    print("Digest sent successfully!")
