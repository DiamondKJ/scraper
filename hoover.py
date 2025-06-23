import pandas as pd
import re # For regular expressions to clean text

# --- Load the saved data ---
try:
    reddit_posts_df = pd.read_csv('reddit_peptides_cognitive_raw.csv')
    reddit_comments_df = pd.read_csv('reddit_peptides_cognitive_comments.csv')
    print("CSV files loaded successfully into DataFrames.")
except FileNotFoundError:
    print("Error: Make sure 'reddit_peptides_cognitive_raw.csv' and 'reddit_peptides_cognitive_comments.csv' are in the same directory.")
    exit()

# --- Displaying Data for Better Readability ---

print("\n--- Reddit Posts DataFrame (reddit_peptides_cognitive_raw.csv) ---")
# Set pandas options to display more text without truncation
pd.set_option('display.max_colwidth', None) # Display full content of columns
pd.set_option('display.width', 1000) # Ensure enough width for wider output

# Display some useful columns for initial inspection
# We'll drop the 'comments' column for this view as it's a nested list and can clutter
print(reddit_posts_df[['subreddit', 'post_title', 'post_text', 'score', 'num_comments', 'created_utc', 'search_term_used']].head())

print("\n--- Reddit Comments DataFrame (reddit_peptides_cognitive_comments.csv) ---")
print(reddit_comments_df[['subreddit', 'post_title', 'comment_text', 'comment_score', 'comment_created_utc']].head())


# --- Basic Text Cleaning Function ---
# This function will remove common markdown, newlines, and potentially URLs
def clean_text(text):
    if isinstance(text, str): # Ensure it's a string before processing
        text = text.replace('\n', ' ') # Replace newlines with spaces
        text = text.replace('\r', ' ') # Replace carriage returns
        text = re.sub(r'\[.*?\]\(.*?\)','', text) # Remove markdown links [text](url)
        text = re.sub(r'&amp;', '&', text) # Decode HTML entities like &amp;
        text = re.sub(r'\s+', ' ', text).strip() # Replace multiple spaces with single space
    else:
        text = '' # Handle non-string values (e.g., NaN)
    return text

# --- Apply Cleaning to Relevant Text Columns ---
print("\nApplying basic text cleaning...")
reddit_posts_df['post_title_cleaned'] = reddit_posts_df['post_title'].apply(clean_text)
reddit_posts_df['post_text_cleaned'] = reddit_posts_df['post_text'].apply(clean_text)
reddit_comments_df['comment_text_cleaned'] = reddit_comments_df['comment_text'].apply(clean_text)

# --- Display Cleaned Data (first 5 rows of cleaned columns) ---
print("\n--- Cleaned Reddit Posts (sample) ---")
print(reddit_posts_df[['subreddit', 'post_title_cleaned', 'post_text_cleaned']].head())

print("\n--- Cleaned Reddit Comments (sample) ---")
print(reddit_comments_df[['subreddit', 'post_title', 'comment_text_cleaned']].head())


# --- Save Cleaned Data to New CSVs (Optional but Recommended) ---
# It's good practice to save cleaned data separately so you always have the raw original.
cleaned_posts_filename = 'reddit_peptides_cognitive_cleaned_posts.csv'
cleaned_comments_filename = 'reddit_peptides_cognitive_cleaned_comments.csv'

# Select only the relevant columns to save, including the new cleaned ones
# For posts, exclude the raw 'comments' list which is hard to use in a flat CSV
reddit_posts_df_to_save = reddit_posts_df.drop(columns=['comments', 'post_title', 'post_text'])
reddit_comments_df_to_save = reddit_comments_df.drop(columns=['comment_text'])


reddit_posts_df_to_save.to_csv(cleaned_posts_filename, index=False)
reddit_comments_df_to_save.to_csv(cleaned_comments_filename, index=False)

print(f"\nCleaned posts data saved to '{cleaned_posts_filename}'")
print(f"Cleaned comments data saved to '{cleaned_comments_filename}'")

# --- Basic Data Exploration (Getting a feel for the data) ---
print("\n--- Basic Data Exploration ---")
print(f"Total Posts: {len(reddit_posts_df)}")
print(f"Total Comments: {len(reddit_comments_df)}")
print("\nTop 5 Subreddits by Post Count:")
print(reddit_posts_df['subreddit'].value_counts().head())
print("\nTop 5 Search Terms by Post Count:")
print(reddit_posts_df['search_term_used'].value_counts().head())
print("\nPost Score Distribution (Posts DataFrame):")
print(reddit_posts_df['score'].describe())
print("\nComment Score Distribution (Comments DataFrame):")
print(reddit_comments_df['comment_score'].describe())

# Check for empty posts or comments after cleaning
print(f"\nPosts with empty cleaned text: {reddit_posts_df['post_text_cleaned'].apply(lambda x: x.strip() == '').sum()}")
print(f"Comments with empty cleaned text: {reddit_comments_df['comment_text_cleaned'].apply(lambda x: x.strip() == '').sum()}")