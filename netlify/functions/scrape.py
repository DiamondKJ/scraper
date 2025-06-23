import json
import os
import re
import time
import pandas as pd
import praw
from datetime import datetime # Import datetime for ISO format


# --- Reddit API Credentials (from environment variables) ---
# For local, ensure these are set in your shell before running Flask
CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
USERNAME = os.environ.get('REDDIT_USERNAME')
PASSWORD = os.environ.get('REDDIT_PASSWORD') # Or app password if 2FA is on
USER_AGENT = os.environ.get('REDDIT_USER_AGENT', 'NeuroPsychiatryResearchApp/1.0 by DiamondKJ125')

reddit = None
try:
    if CLIENT_ID and CLIENT_SECRET and USERNAME and PASSWORD:
        reddit = praw.Reddit(client_id=CLIENT_ID,
                            client_secret=CLIENT_SECRET,
                            user_agent=USER_AGENT,
                            username=USERNAME,
                            password=PASSWORD)
        print("PRAW client initialized.")
    else:
        print("Reddit API credentials are not fully set as environment variables. Scraping will fail.")
except Exception as e:
    print(f"Error initializing PRAW client: {e}")
    reddit = None

# --- Basic Text Cleaning Function ---
def clean_text(text):
    if isinstance(text, str):
        text = text.replace('\n', ' ').replace('\r', ' ')
        text = re.sub(r'\[.*?\]\(.*?\)','', text) # Remove markdown links [text](url)
        text = re.sub(r'&amp;', '&', text) # Decode HTML entities like &amp;
        text = re.sub(r'\s+', ' ', text).strip() # Replace multiple spaces with single space
    else:
        text = ''
    return text

# --- Scraping Logic ---
def scrape_reddit_posts_and_comments(subreddits, search_terms, limit_per_search_term=5, total_post_limit=10):
    """
    Scrapes Reddit posts and their comments, returning structured data.
    """
    if not reddit:
        return {"error": "Reddit API not initialized. Check your environment variables and PRAW setup."}

    data = []
    items_collected = 0

    for subreddit_name in subreddits:
        if items_collected >= total_post_limit:
            break
        try:
            subreddit = reddit.subreddit(subreddit_name)
            for term in search_terms:
                if items_collected >= total_post_limit:
                    break
                print(f"Searching r/{subreddit_name} for '{term}'...")
                for submission in subreddit.search(term, limit=limit_per_search_term):
                    if submission.stickied:
                        continue

                    post_info = {
                        'platform': 'Reddit',
                        'subreddit': subreddit.display_name,
                        'post_id': submission.id,
                        'post_title': clean_text(submission.title),
                        'post_text': clean_text(submission.selftext),
                        'score': submission.score,
                        'num_comments': submission.num_comments,
                        'url': submission.url,
                        'created_utc': datetime.fromtimestamp(submission.created_utc).isoformat(), # Use datetime for ISO
                        'search_term_used': term,
                        'comments': []
                    }

                    # Limit comments to avoid excessive data
                    submission.comments.replace_more(limit=0) # Get all top-level comments
                    # submission.comments.replace_more(limit=None) # Get ALL comments including replies, can be slow
                    comment_count = 0
                    for comment in submission.comments.list():
                        if isinstance(comment, praw.models.Comment):
                            post_info['comments'].append({
                                'comment_id': comment.id,
                                'comment_text': clean_text(comment.body),
                                'comment_score': comment.score,
                                'comment_created_utc': datetime.fromtimestamp(comment.created_utc).isoformat()
                            })
                            comment_count += 1
                            if comment_count >= 5: # Limit to max 5 comments per post for a reasonable local demo
                                break
                    data.append(post_info)
                    items_collected += 1
                    time.sleep(0.5) # Small delay to be polite to Reddit API

                time.sleep(1) # Delay between search terms
        except praw.exceptions.PRAWException as pe:
            print(f"PRAW error during scraping for r/{subreddit_name}: {pe}")
            return {"error": f"Scraping error for r/{subreddit_name}: {pe}"}
        except Exception as e:
            print(f"An unexpected error occurred during scraping for r/{subreddit_name}: {e}")
            return {"error": f"An unexpected error occurred: {e}"}
        time.sleep(2) # Delay between subreddits

    return data

# This part runs if you execute scrape.py directly (e.g., for testing)
if __name__ == '__main__':
    # Example local test run:
    test_subreddits = ["Nootropics"]
    test_keywords = ["peptides"]
    print("Running a local test scrape...")
    results = scrape_reddit_posts_and_comments(test_subreddits, test_keywords, limit_per_search_term=2, total_post_limit=5)
    print(json.dumps(results, indent=2))
    if "error" in results:
        print(f"Local test failed with error: {results['error']}")
    else:
        print(f"Local test successful. Scraped {len(results)} posts.")