# analyze_data.py

import pandas as pd
import re
import os
import sys

# --- Adjust the import path to find classifier.py ---
current_dir = os.path.dirname(__file__)
functions_dir = os.path.join(current_dir, 'netlify', 'functions')
sys.path.insert(0, functions_dir)

from classifier import classify_fatigue_comment

print("Starting data analysis and classification (Option B: Loosened Filtering, Corrected Columns)...")

# --- Define Targeted Keyword Lists ---
PEPTIDE_KEYWORDS = [
    "peptide", "peptides", "noopept", "modafinil", "semaglutide", "tirzepatide",
    "bpc-157", "tb-500", "cjc-1295", "ipamorelin", "dsip", "epitalon",
    "ghrp", "melanotan", "sarms", "cortexin", "dihexa", "cerebrolysin", "selank",
    "bpc", "thymosin", "nmn", "nr", "creatine", "choline", "alpha-gpc",
    "agmatine", "pramiracetam", "aniracetam", "follistatin", "melanotan", "ipamorelin",
    "gaba", "dopamine", "serotonin", "acetylcholine", "mk-677", "ghk-cu", "motc" # Added more
]

COGNITIVE_KEYWORDS = [
    "cognitive", "brain fog", "focus", "concentration", "memory", "mental clarity",
    "thinking", "mental energy", "alertness", "cognition", "neuroplasticity",
    "learning", "attention", "mental performance", "mind", "mentally",
    "sharpness", "clarity", "brain power", "mental slump", "slow thinking",
    "recall", "retention", "executive function", "neuro", "brain", "acuity",
    "cognition", "mental alertness" # Added more
]

FEELING_EXPERIENCE_KEYWORDS = [
    "feel", "feeling", "felt", "experience", "experienced", "noticed", "my thoughts",
    "how do you feel", "did anyone else", "impacts me", "effects on me", "my symptoms",
    "i'm wondering", "i think", "i believe", "my take", "my experience", "personal account",
    "improved", "worsened", "helped", "hurt", "effect", "struggle", "benefit", "side effect",
    "drained", "exhausted", "tired", "fatigue", "burnt out", "my mood", "anxiety", "stress",
    "depression", "irritable", "sleepy", "awake", "energy", "energetic", "lethargic",
    "opinion", "feedback", "thoughts", "my state", "well-being", "mood swings", "brain dead",
    "exhaustion", "weariness", "listless", "sluggish", "depressed", "stressed", "anxious",
    "frustrated", "overwhelmed", "boosted", "uplifted", "calm", "relaxed" # Added more
]

# --- Helper function for robust keyword checking ---
def contains_any_keyword(text, keywords, debug_name=""):
    if pd.isna(text) or not str(text).strip(): # Check for NaN and empty strings
        return False
    text_lower = str(text).lower()
    found_keywords = [keyword for keyword in keywords if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower)]
    # if found_keywords:
    #     print(f"DEBUG: Found {debug_name} keywords: {found_keywords} in text snippet: '{text_lower[:100]}...'")
    return bool(found_keywords)

# --- Load Existing Data ---
try:
    posts_df = pd.read_csv('cleaned_posts.csv') #
    comments_df = pd.read_csv('cleaned_comments.csv') #
    print(f"Loaded {len(posts_df)} posts from cleaned_posts.csv")
    print(f"Loaded {len(comments_df)} comments from cleaned_comments.csv")

    # --- Debugging: Check actual column names and content ---
    print("\n--- DEBUG: Posts DataFrame Info ---")
    posts_df.info()
    print("\n--- DEBUG: First 5 Post Titles and Bodies (cleaned) ---")
    # Corrected column names here
    print(posts_df[['post_title_cleaned', 'post_text_cleaned']].head().to_string())
    print("\n--- DEBUG: Comments DataFrame Info ---")
    comments_df.info()
    print("\n--- DEBUG: First 5 Comment Texts (cleaned) ---")
    # Assuming 'comment_text_cleaned' based on the pattern
    print(comments_df['comment_text_cleaned'].head().to_string())


except FileNotFoundError:
    print("Error: cleaned_posts.csv or cleaned_comments.csv not found.") #
    print("Please ensure these files are in the same directory as analyze_data.py or provide the correct path.")
    sys.exit(1)


# --- Pre-process posts: Create a dictionary for quick lookup by post_id ---
# Use the correct cleaned column names for posts
posts_df['full_post_text'] = posts_df.apply(
    lambda row: str(row.get('post_title_cleaned', '')).strip() + ' ' + str(row.get('post_text_cleaned', '')).strip(), axis=1
)
post_lookup = posts_df.set_index('post_id')['full_post_text'].to_dict()

# Debugging: Check a sample of the full_post_text
# for i, (post_id, text) in enumerate(list(post_lookup.items())[:5]):
#    print(f"DEBUG Post Context {post_id}: '{text[:100]}...'")


# --- Filter and Classify Posts (Looser filtering for posts: Peptide AND Cognitive) ---
print("\nFiltering and classifying posts...")
filtered_classified_posts = []
debug_post_count_peptide = 0
debug_post_count_cognitive = 0
debug_post_count_both = 0


for index, row in posts_df.iterrows():
    post_text = row['full_post_text']

    has_peptide = contains_any_keyword(post_text, PEPTIDE_KEYWORDS, "peptide")
    has_cognitive = contains_any_keyword(post_text, COGNITIVE_KEYWORDS, "cognitive")

    if has_peptide: debug_post_count_peptide += 1
    if has_cognitive: debug_post_count_cognitive += 1

    # Filter posts if they contain Peptide AND Cognitive keywords (feeling can be in comments)
    if has_peptide and has_cognitive:
        debug_post_count_both += 1
        # Apply classification for fatigue
        predicted_label, confidence_score = classify_fatigue_comment(post_text)

        post_data = row.to_dict()
        post_data['fatigue_classification'] = predicted_label
        post_data['classification_confidence'] = confidence_score
        filtered_classified_posts.append(post_data)

filtered_posts_df = pd.DataFrame(filtered_classified_posts)
print(f"DEBUG: Posts with any Peptide keyword: {debug_post_count_peptide}")
print(f"DEBUG: Posts with any Cognitive keyword: {debug_post_count_cognitive}")
print(f"Found {len(filtered_posts_df)} relevant posts (Peptide & Cognitive).") # This is debug_post_count_both


# --- Filter and Classify Comments (Stricter filtering on combined text: Peptide AND Cognitive AND Feeling) ---
print("\nFiltering and classifying comments...")
filtered_classified_comments = []
debug_comment_count_peptide = 0
debug_comment_count_cognitive = 0
debug_comment_count_feeling = 0
debug_comment_count_all_three = 0


for index, row in comments_df.iterrows():
    # Corrected column name for comment text
    comment_text = str(row.get('comment_text_cleaned', '')).strip()
    post_id = row.get('post_id') # Get the post_id for the current comment

    # Get the parent post's text. If post_id not found, treat as empty post context.
    parent_post_text = post_lookup.get(post_id, '')

    # Combine comment text with its parent post's text for more context
    combined_text = (comment_text + ' ' + parent_post_text).strip()

    has_peptide = contains_any_keyword(combined_text, PEPTIDE_KEYWORDS, "peptide (combined)")
    has_cognitive = contains_any_keyword(combined_text, COGNITIVE_KEYWORDS, "cognitive (combined)")
    has_feeling = contains_any_keyword(combined_text, FEELING_EXPERIENCE_KEYWORDS, "feeling (combined)")

    if has_peptide: debug_comment_count_peptide += 1
    if has_cognitive: debug_comment_count_cognitive += 1
    if has_feeling: debug_comment_count_feeling += 1

    # Filter comments if the combined text contains Peptide AND Cognitive AND Feeling/Experience keywords
    if has_peptide and has_cognitive and has_feeling:
        debug_comment_count_all_three += 1
        predicted_label, confidence_score = classify_fatigue_comment(comment_text)

        comment_data = row.to_dict()
        comment_data['fatigue_classification'] = predicted_label
        comment_data['classification_confidence'] = confidence_score
        filtered_classified_comments.append(comment_data)

filtered_comments_df = pd.DataFrame(filtered_classified_comments)
print(f"DEBUG: Comments (combined text) with any Peptide keyword: {debug_comment_count_peptide}")
print(f"DEBUG: Comments (combined text) with any Cognitive keyword: {debug_comment_count_cognitive}")
print(f"DEBUG: Comments (combined text) with any Feeling keyword: {debug_comment_count_feeling}")
print(f"Found {len(filtered_comments_df)} relevant comments (Peptide & Cognitive & Feeling, with post context).") # This is debug_comment_count_all_three


# --- Save Filtered and Classified Results ---
output_posts_filename = 'classified_relevant_posts_option_b.csv'
output_comments_filename = 'classified_relevant_comments_option_b.csv'

if not filtered_posts_df.empty:
    # Drop the temporary 'full_post_text' column before saving
    filtered_posts_df = filtered_posts_df.drop(columns=['full_post_text'], errors='ignore')
    filtered_posts_df.to_csv(output_posts_filename, index=False)
    print(f"\nFiltered and classified posts saved to '{output_posts_filename}'")
else:
    print("\nNo relevant posts found to save.")

if not filtered_comments_df.empty:
    filtered_comments_df.to_csv(output_comments_filename, index=False)
    print(f"Filtered and classified comments saved to '{output_comments_filename}'")
else:
    print("No relevant comments found to save.")

print("\nData analysis and classification complete.")