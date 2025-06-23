import os # <--- THIS IS CRUCIAL: Make sure this line is at the very top
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# This is the corrected import path for scrape.py
# It assumes your file structure is: scraper/netlify/functions/scrape.py
# Make sure you have empty __init__.py files in both netlify/ and netlify/functions/
from netlify.functions.scrape import scrape_reddit_posts_and_comments

# Initialize Flask app
# Use os.path.join and os.path.dirname(__file__) to create absolute paths
# This reliably tells Flask where your 'frontend' folder is, fixing 404 errors for CSS/JS
app = Flask(__name__,
            static_folder=os.path.join(os.path.dirname(__file__), 'frontend'),
            template_folder=os.path.join(os.path.dirname(__file__), 'frontend'))

CORS(app) # Enable CORS for all routes (important for frontend to talk to backend locally)

@app.route('/')
def index():
    """Serves the main HTML page."""
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def perform_scrape():
    """Handles the scraping request from the frontend."""
    try:
        data = request.json
        subreddits_input = data.get('subreddits', '')
        keywords_input = data.get('keywords', '')
        test_run = data.get('test_run', False) # Boolean flag from the frontend checkbox

        if not subreddits_input or not keywords_input:
            return jsonify({"status": "error", "message": "Missing 'subreddits' or 'keywords' in request"}), 400

        subreddits = [s.strip() for s in subreddits_input.split(',') if s.strip()]
        keywords = [k.strip() for k in keywords_input.split(',') if k.strip()]

        if not subreddits or not keywords:
            return jsonify({"status": "error", "message": "Please provide valid subreddits and keywords"}), 400

        # Adjust limits based on the 'test_run' flag
        if test_run:
            print("Performing a quick local demo run (fewer results)...")
            limit_per_search_term = 1  # Get only 1 submission per search term
            total_post_limit = 5      # Max 5 posts overall
        else:
            print("Performing a full local scrape...")
            limit_per_search_term = 10 # Default to 10 submissions per search term
            total_post_limit = 50      # Default to 50 total posts (adjust as needed for longer runs)

        # Call the scraping function from scrape.py
        scraped_results = scrape_reddit_posts_and_comments(
            subreddits, keywords,
            limit_per_search_term=limit_per_search_term,
            total_post_limit=total_post_limit
        )

        # Handle potential errors returned by the scraping function
        if isinstance(scraped_results, dict) and "error" in scraped_results:
            return jsonify({"status": "error", "message": scraped_results["error"]}), 500

        # Separate posts and comments for easier display on frontend
        posts_for_frontend = []
        comments_for_frontend = []

        for post in scraped_results:
            post_copy = post.copy()
            post_comments = post_copy.pop('comments') # Extract comments from post_copy
            posts_for_frontend.append(post_copy)

            for comment in post_comments:
                comment_copy = comment.copy()
                comment_copy['post_id'] = post['post_id']
                comment_copy['post_title'] = post['post_title']
                comment_copy['subreddit'] = post['subreddit']
                comments_for_frontend.append(comment_copy)

        return jsonify({
            "status": "success",
            "posts": posts_for_frontend,
            "comments": comments_for_frontend
        })

    except Exception as e:
        print(f"Error in Flask /scrape route: {e}")
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    # Reminder: Set your Reddit API credentials as environment variables
    # in your terminal BEFORE running this script:
    # export REDDIT_CLIENT_ID='your_client_id'
    # export REDDIT_CLIENT_SECRET='your_secret'
    # export REDDIT_USERNAME='your_username'
    # export REDDIT_PASSWORD='your_password' (or app password if 2FA)
    # export REDDIT_USER_AGENT='MyLocalRedditApp/1.0 by YourRedditUsername'

    app.run(debug=True, port=8080) # Run Flask in debug mode on port 8080