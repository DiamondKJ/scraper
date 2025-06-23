# final_analysis.py (Version 5 - Inclusive for All Categories + De-duplication)

import pandas as pd
import sys

# Set pandas to display wider columns so you can read the text
pd.set_option('display.max_colwidth', 200)

print("--- Starting Final Analysis (Processing Both Posts and Comments for ALL Categories) ---")

# This is the minimum confidence score a classification must have to be included.
CONFIDENCE_THRESHOLD = 0.70

# ==============================================================================
# --- Section 1: Analyzing the POSTS File ---
# ==============================================================================

print("\n\n--- Analyzing POSTS File ---")

try:
    classified_posts_df = pd.read_csv('classified_relevant_posts_option_b.csv')
    
    # --- NEW: Remove duplicate posts based on post_id ---
    initial_post_count = len(classified_posts_df)
    classified_posts_df.drop_duplicates(subset=['post_id'], keep='first', inplace=True)
    deduplicated_post_count = len(classified_posts_df)
    print(f"Loaded and de-duplicated posts: {initial_post_count} -> {deduplicated_post_count} unique posts.")

    # Apply the confidence score filter to all posts
    high_confidence_posts = classified_posts_df[
        classified_posts_df['classification_confidence'] >= CONFIDENCE_THRESHOLD
    ].copy()

    print(f"Found {len(high_confidence_posts)} high-confidence posts across all categories (Threshold >= {CONFIDENCE_THRESHOLD}).")

    if not high_confidence_posts.empty:
        print("\n--- Sample of HIGHLY RELEVANT POSTS (Confidence >= " + str(CONFIDENCE_THRESHOLD) + ") ---")
        print(high_confidence_posts[[
            'post_title_cleaned',
            'fatigue_classification',
            'classification_confidence'
        ]].head(10).to_string())

        # Save the final, high-quality dataset of posts
        final_posts_filename = 'FINAL_HIGH_CONFIDENCE_posts.csv'
        high_confidence_posts.sort_values(by='classification_confidence', ascending=False).to_csv(final_posts_filename, index=False)
        print(f"\nSaved the final, high-quality posts dataset to '{final_posts_filename}'")
    else:
        print("\nNo high-confidence posts were found.")

except FileNotFoundError:
    print("\nError: 'classified_relevant_posts_option_b.csv' not found.")
    print("This file is expected. Please ensure analyze_data.py ran correctly.")


# ==============================================================================
# --- Section 2: Analyzing the COMMENTS File (FOR THE NETLIFY APP) ---
# ==============================================================================

print("\n\n--- Analyzing COMMENTS File ---")

try:
    classified_comments_df = pd.read_csv('classified_relevant_comments_option_b.csv')

    # --- NEW: Remove duplicate comments based on comment_id ---
    initial_comment_count = len(classified_comments_df)
    classified_comments_df.drop_duplicates(subset=['comment_id'], keep='first', inplace=True)
    deduplicated_comment_count = len(classified_comments_df)
    print(f"Loaded and de-duplicated comments: {initial_comment_count} -> {deduplicated_comment_count} unique comments.")

    # Apply the confidence filter to EVERY comment.
    high_confidence_all_categories = classified_comments_df[
        classified_comments_df['classification_confidence'] >= CONFIDENCE_THRESHOLD
    ].copy()

    print(f"\nFound {len(high_confidence_all_categories)} high-confidence comments across ALL categories (Threshold >= {CONFIDENCE_THRESHOLD}).")

    if not high_confidence_all_categories.empty:
        # Display a sample of what we found to confirm it includes multiple categories
        print("\n--- Sample of High-Confidence Comments Found ---")
        print(high_confidence_all_categories[['comment_text_cleaned', 'fatigue_classification', 'classification_confidence']].head(10).to_string())

        # --- Create the JSON file for Netlify deployment ---
        print("\n--- Creating JSON file for Netlify deployment ---")
        json_output_filename = 'netlify/functions/comments.json'
        
        # Save the de-duplicated and filtered dataframe
        high_confidence_all_categories.to_json(json_output_filename, orient='records', indent=2)
        print(f"Successfully created '{json_output_filename}' with {len(high_confidence_all_categories)} records.")
        print("This file is now ready for deployment.")
        
    else:
        print("\nNo high-confidence comments were found for ANY category.")

except FileNotFoundError:
    print("\nError: 'classified_relevant_comments_option_b.csv' not found.")
    print("This file is expected. Please ensure analyze_data.py ran correctly.")

print("\n\n--- Final Analysis Complete ---")