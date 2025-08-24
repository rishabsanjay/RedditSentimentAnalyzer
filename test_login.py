import praw
import openai
import os

# Your Reddit credentials
REDDIT_CLIENT_ID = "xWXLpNpX1_dVdHBFzzA0_Q"
REDDIT_CLIENT_SECRET = "Pox6ud_xVyJiUiEzheI5bYnuguVkfg"
REDDIT_USER_AGENT = "My-Sentiment-Analyzer by u/rishabsanjayy"
REDDIT_USERNAME = "rishabsanjayy"
REDDIT_PASSWORD = "Rish2005"

# Connect to Reddit
try:
    print("Attempting to log in to Reddit...")
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD
    )
    print("Login successful! The script is working.")
    
    # Optional: Get your username to confirm
    print(f"Logged in as user: {reddit.user.me()}")

except Exception as e:
    print("\nAn error occurred during login. Please check your credentials.")
    print(f"Error details: {e}")
