# netlify/functions/classifier.py
import os
from transformers import pipeline

# Load the zero-shot classification pipeline
# 'mnli' models are good for this as they are trained on Natural Language Inference
# You might try 'MoritzLaurer/deberta-v3-large-zeroshot' for potentially better performance
# but it's a larger model. Start with a common one.
# Make sure you have internet access for the first time you run this to download the model.
try:
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
except Exception as e:
    print(f"Error loading zero-shot classification model: {e}")
    print("Please ensure you have an active internet connection or the model is cached.")
    classifier = None # Set to None to indicate model loading failure

def classify_fatigue_comment(comment_text):
    if not classifier:
        return "Model_Load_Error", 0.0 # Return default error if model failed to load

    # Define your candidate labels clearly. These are what the model will try to predict.
    # Be descriptive but concise for the model.
    # Ensure these labels align with what you want for your dissertation analysis.
    candidate_labels = [
        "cognitive fatigue related to peptides",
        "physical fatigue related to peptides",
        "emotional fatigue related to peptides",
        "general peptide discussion, no fatigue mentioned",
        "fatigue mentioned, but not related to peptides",
        "irrelevant or other topic"
    ]

    # Perform the classification
    result = classifier(comment_text, candidate_labels)

    # The result is a dictionary with 'sequence', 'labels', and 'scores'
    # We want the label with the highest score
    predicted_label = result['labels'][0]
    confidence_score = result['scores'][0]

    return predicted_label, confidence_score

# Example Usage (for testing the classifier function independently)
if __name__ == "__main__":
    test_comments = [
        "My brain fog has been intense since I started this new peptide regimen, hard to focus.",
        "Feeling so much physical fatigue after my workout, considering a peptide for recovery.",
        "Peptide X made me feel less anxious and emotionally drained from my tough week.",
        "What are the best peptides for anti-aging?",
        "Just regular old tiredness, nothing special.",
        "Does anyone know about the side effects of melatonin?",
        "Been having trouble concentrating, wonder if it's just stress or something more.",
        "Ever since I started BPC-157, my knee pain has significantly reduced, but I still feel mentally drained at the end of the day.",
        "I'm so exhausted, I could sleep for a week."
    ]

    print("--- Running Classification Examples ---")
    for i, comment in enumerate(test_comments):
        print(f"\nComment {i+1}: \"{comment}\"")
        label, score = classify_fatigue_comment(comment)
        print(f"  Predicted Label: '{label}' (Confidence: {score:.2f})")