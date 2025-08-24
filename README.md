# Reddit Sentiment Analyzer

A real-time sentiment analysis dashboard for Reddit posts.  
Built with **Python, Flask, PRAW, OpenAI API, and Socket.IO**.

## Features
- Streams new Reddit submissions live (from `r/stocks+investing+tech`)
- Uses OpenAI GPT model to classify sentiment (`Positive`, `Negative`, `Neutral`)
- Displays results on a real-time web dashboard
- Easy to run locally with Python

## Demo
When you run it, visit: [http://localhost:8000](http://localhost:8000)  
You’ll see new posts and their sentiment badges updating live.

## Setup

### 1. Clone Repo
```bash
git clone https://github.com/yourusername/reddit-sentiment-analyzer.git
cd reddit-sentiment-analyzer

2. Install Dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

3. Environment Variables
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
USER_AGENT=My-Sentiment-Analyzer by u/yourusername
OPENAI_API_KEY=sk-xxxx

python app.py
Go to http://localhost:8000.
