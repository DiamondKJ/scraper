import praw
import pandas as pd
import time
import os

# --- Reddit API Credentials ---
# IMPORTANT SECURITY NOTE:
# It's best practice NOT to hardcode sensitive information like passwords directly in your script.
# For a personal research project, environment variables are a good alternative.
# If you're sharing this code, make sure to instruct others to set these.
# How to set environment variables:
# On Linux/macOS: export REDDIT_CLIENT_ID='your_id'
# On Windows (Command Prompt): set REDDIT_CLIENT_ID=your_id
# On Windows (PowerShell): $env:REDDIT_CLIENT_ID='your_id'

# From your screenshot:
CLIENT_ID = "A0dXsqY6DtfVcKOm_pDvaA" # This is your 'web app' ID from the screenshot
CLIENT_SECRET = 'oSmEG0EBtqDCMPeVF2FR8UdJCsLF3g' # This is your 'secret' from the screenshot

# Your Reddit username is DiamondKJ125
USERNAME = 'DiamondKJ125'
# You will need to input your Reddit password.
# For security, consider prompting for it or using environment variables as suggested above.
# For now, I'll use a placeholder. NEVER hardcode your password if sharing the script.
# PASSWORD = os.environ.get('REDDIT_PASSWORD') # Recommended: get from environment variable
PASSWORD = 'girnat123' # REPLACE THIS WITH YOUR ACTUAL REDDIT PASSWORD

# A descriptive user agent is required by Reddit's API.
# It helps them identify who is making requests and contact you if there are issues.
# Use something unique and informative.
USER_AGENT = 'NeuroPsychiatryResearchBot/1.0 by DiamondKJ125 (research project)'

# --- Initialize PRAW ---
try:
    reddit = praw.Reddit(client_id=CLIENT_ID,
                        client_secret=CLIENT_SECRET,
                        user_agent=USER_AGENT,
                        username=USERNAME,
                        password=PASSWORD)
    print("PRAW successfully initialized with your Reddit credentials.")
except Exception as e:
    print(f"Error initializing PRAW. Please check your credentials: {e}")
    print("Ensure you've replaced 'YOUR_REDDIT_PASSWORD_HERE' with your actual password.")
    # Exit if initialization fails, as we can't proceed without it.
    exit()

def scrape_reddit(subreddits, search_terms, limit_per_search_term=500):
    """
    Scrapes Reddit posts and their top comments based on subreddits and search terms.

    Args:
        subreddits (list): A list of subreddit names (e.g., ['Nootropics', 'supplements']).
        search_terms (list): A list of keywords to search for within each subreddit.
        limit_per_search_term (int): Maximum number of submissions to retrieve for each
                                      search term within each subreddit.

    Returns:
        pandas.DataFrame: A DataFrame containing the scraped data.
    """
    data = []
    print(f"Starting Reddit scraping for {len(subreddits)} subreddits and {len(search_terms)} search terms.")

    for subreddit_name in subreddits:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            print(f"\n--- Scraping r/{subreddit_name} ---")

            for term in search_terms:
                print(f"  Searching for posts containing: '{term}' (limit: {limit_per_search_term} per search term)...")
                # Using subreddit.search() allows you to target specific keywords.
                # You can also use subreddit.hot(), subreddit.new(), subreddit.top() if preferred.
                count = 0
                for submission in subreddit.search(term, limit=limit_per_search_term):
                    if submission.stickied: # Skip pinned posts often used for rules/announcements
                        continue

                    # Store post details
                    post_info = {
                        'platform': 'Reddit',
                        'subreddit': subreddit.display_name,
                        'post_id': submission.id, # Unique ID for the post
                        'post_title': submission.title,
                        'post_text': submission.selftext, # The body of the text post
                        'score': submission.score, # Upvotes minus downvotes
                        'num_comments': submission.num_comments,
                        'url': submission.url,
                        'created_utc': pd.to_datetime(submission.created_utc, unit='s'), # Convert timestamp to datetime
                        'search_term_used': term, # Which search term found this post
                        'comments': [] # Initialize an empty list to store comments
                    }

                    # Fetch comments for the submission
                    # .replace_more(limit=0) is crucial to expand 'More comments' links
                    # .list() flattens the comment tree into a list
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments.list():
                        if isinstance(comment, praw.models.Comment): # Ensure it's a real comment object
                            post_info['comments'].append({
                                'comment_id': comment.id,
                                'comment_text': comment.body,
                                'comment_score': comment.score,
                                'comment_created_utc': pd.to_datetime(comment.created_utc, unit='s')
                            })
                    data.append(post_info)
                    count += 1
                    # Small delay after processing each submission to be polite to the API
                    time.sleep(0.5)

                print(f"  Finished searching for '{term}'. Found {count} relevant submissions.")
                # Add a slightly longer delay between different search terms within the same subreddit
                time.sleep(2)

        except praw.exceptions.PRAWException as pe:
            print(f"  PRAW error while scraping r/{subreddit_name}: {pe}")
            print("  This might be due to rate limits or invalid subreddit name.")
        except Exception as e:
            print(f"  An unexpected error occurred while scraping r/{subreddit_name}: {e}")

        # Add a longer delay between subreddits to be extra cautious with rate limits
        time.sleep(5)

    print("\n--- Reddit Scraping Complete ---")
    return pd.DataFrame(data)

# --- Define Your Scraping Parameters ---
# Consider a wider range of subreddits that might discuss cognitive enhancement or related topics.
# Examples: 'CognitiveEnhancement', 'StackAdvice', 'drugs (if relevant to your ethical guidelines and focus on user experience, but be very cautious)',
# 'BrainHealth', 'MentalHealth', etc. Ensure they are relevant to peptides.
subreddits_to_scrape = [
    'Nootropics',
    'supplements',
    'Biohackers',
    'Peptides', # If a dedicated peptide subreddit exists and is active
    'longevity', # May discuss peptides for general health including cognitive
    'BrainHealth',
    # 'AskScience' - might have more formal discussions, less personal experience
]

# Refine your search terms to capture specific discussions around peptides and cognition.
search_terms = [
    'peptides cognitive',
    'nootropics peptides',
    'memory peptides',
    'focus peptides',
    'brain peptides',
    'peptides for concentration',
    'peptides mental clarity',
    'cortexin', # Example of a specific peptide
    'dihexa',
    'bpc 157 cognitive', # BPC-157 is widely discussed, might have cognitive mentions
    'cerebrolysin',
    'selank',
    'semaglutide cognitive' # Newer peptides also being explored for CNS effects
]

# --- Run the Scraper ---
print("Initiating Reddit data collection...")
reddit_data_df = scrape_reddit(subreddits_to_scrape, search_terms, limit_per_search_term=200) # Reduced limit for initial test

# --- Display and Save Results ---
if not reddit_data_df.empty:
    print(f"\nSuccessfully scraped {len(reddit_data_df)} Reddit posts (with comments).")
    print("First 5 rows of the DataFrame:")
    print(reddit_data_df.head())

    print("\nColumns in the DataFrame:")
    print(reddit_data_df.columns)

    # You can expand the 'comments' list column into separate rows if you want to analyze comments independently
    # For now, it's stored as a list of dictionaries within each row.

    # Save the raw data
    output_filename = 'reddit_peptides_cognitive_raw.csv'
    reddit_data_df.to_csv(output_filename, index=False)
    print(f"\nRaw Reddit data saved to '{output_filename}'")

    # If you want to expand comments into separate rows for easier analysis:
    print("\nProcessing comments for separate analysis...")
    all_comments = []
    for index, row in reddit_data_df.iterrows():
        post_id = row['post_id']
        post_title = row['post_title']
        subreddit = row['subreddit']
        search_term_used = row['search_term_used']

        if row['comments']:
            for comment in row['comments']:
                comment_data = {
                    'platform': 'Reddit',
                    'subreddit': subreddit,
                    'post_id': post_id,
                    'post_title': post_title,
                    'comment_id': comment['comment_id'],
                    'comment_text': comment['comment_text'],
                    'comment_score': comment['comment_score'],
                    'comment_created_utc': comment['comment_created_utc'],
                    'search_term_used': search_term_used
                }
                all_comments.append(comment_data)
        else:
            # Include posts that have no comments, or handle them as a separate case if needed
            pass # Or add a row with empty comment info if you want to explicitly track no-comment posts

    if all_comments:
        comments_df = pd.DataFrame(all_comments)
        print(f"Extracted {len(comments_df)} individual comments.")
        print("First 5 rows of the comments DataFrame:")
        print(comments_df.head())
        comments_output_filename = 'reddit_peptides_cognitive_comments.csv'
        comments_df.to_csv(comments_output_filename, index=False)
        print(f"Comments data saved to '{comments_output_filename}'")
    else:
        print("No comments were extracted based on the current scraping parameters.")


else:
    print("No data was scraped from Reddit. Check your parameters and network connection.")
