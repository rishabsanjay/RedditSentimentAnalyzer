import time
import logging
from threading import Thread

import praw
from flask import Flask, render_template_string
from flask_socketio import SocketIO
from openai import OpenAI

REDDIT_CLIENT_ID = "PQs6--Hvmims28DBQS-mIg"
REDDIT_CLIENT_SECRET = "Gyr5pXJ7HMs23wwP65e9RMEim6Yg2w"
USER_AGENT = "My-Sentiment-Analyzer by u/rishabsanjayy"
SUBREDDIT = "stocks+investing+tech"

OPENAI_API_KEY = (
    "sk-proj-U2lrCM9wBmwGJCUQasgP_PRz5Dz8rt5NotHh9slXjoebNS1crKeusOrE2ms1L5_"
    "SDqd2dNsmQtT3BlbkFJ6gvgH60p7a034FnrsL5EiN77HDieu4mWGb2lKRs2HQKf_"
    "TLaYd9xkB9enzB11f0PoO7arvq_YA"
)

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=USER_AGENT,
)
reddit.read_only = True

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
app.config["SECRET_KEY"] = "replace-this-when-you-deploy"
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

OPENAI_QPS = 1.5
_last_call = [0.0]

def rate_limited():
    now = time.time()
    min_interval = 1.0 / OPENAI_QPS
    wait = _last_call[0] + min_interval - now
    if wait > 0:
        time.sleep(wait)
    _last_call[0] = time.time()

def get_sentiment(text: str) -> str:
    try:
        rate_limited()
        prompt = (
            "Classify the sentiment of the text with ONE word: "
            "Positive, Negative, or Neutral.\n\nText: " + text[:3000]
        )
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3,
            temperature=0,
        )
        out = (resp.choices[0].message.content or "").strip()
        low = out.lower()
        if low.startswith("pos"):
            return "Positive"
        if low.startswith("neg"):
            return "Negative"
        return "Neutral"
    except Exception:
        return "Neutral"

seen = set()
MAX_SEEN = 5000

def stream_submissions():
    logging.info(f"Starting real-time sentiment analysis on r/{SUBREDDIT} ...")
    subreddit = reddit.subreddit(SUBREDDIT)
    for submission in subreddit.stream.submissions(skip_existing=True):
        try:
            if getattr(submission, "stickied", False):
                continue
            if getattr(submission, "over_18", False):
                continue
            sid = getattr(submission, "id", None)
            if not sid or sid in seen:
                continue
            if len(seen) > MAX_SEEN:
                seen.clear()
            seen.add(sid)
            title = getattr(submission, "title", "") or ""
            if not title.strip():
                continue
            sentiment = get_sentiment(title)
            socketio.emit(
                "new_post",
                {
                    "title": title,
                    "url": f"https://www.reddit.com{submission.permalink}",
                    "sentiment": sentiment,
                },
            )
        except Exception as e:
            logging.exception(f"Stream error: {e}")
            time.sleep(2)

TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Reddit Sentiment — r/{{sub}}</title>
  <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
  <style>
    :root { color-scheme: light dark; }
    body { font-family: -apple-system, system-ui, Segoe UI, Roboto, sans-serif; margin: 24px; }
    #feed { display: grid; gap: 10px; }
    .row { padding: 12px 14px; border: 1px solid #ddd; border-radius: 10px; }
    .badge { padding: 2px 10px; border-radius: 999px; font-size: 12px; margin-left: 8px; }
    .pos { background: #e6ffed; color: #065f46; }
    .neg { background: #ffe6e6; color: #9b1c1c; }
    .neu { background: #eef2ff; color: #3730a3; }
    a { color: inherit; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <h2>r/{{sub}} — Live Sentiment</h2>
  <div id="feed"></div>
  <script>
    const socket = io();
    const feed = document.getElementById('feed');
    function badgeClass(s) {
      const x = (s||'').toLowerCase();
      if (x.startsWith('pos')) return 'badge pos';
      if (x.startsWith('neg')) return 'badge neg';
      return 'badge neu';
    }
    socket.on('new_post', (d) => {
      const div = document.createElement('div');
      div.className = 'row';
      div.innerHTML = `
        <a href="${d.url}" target="_blank" rel="noopener">${d.title}</a>
        <span class="${badgeClass(d.sentiment)}">${d.sentiment}</span>
      `;
      feed.prepend(div);
    });
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(TEMPLATE, sub=SUBREDDIT)

if __name__ == "__main__":
    Thread(target=stream_submissions, daemon=True).start()
    socketio.run(app, host="0.0.0.0", port=8000)
