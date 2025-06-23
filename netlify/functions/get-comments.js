// This function now has two modes:
// 1. ?category=... : Fetches comments for one category.
// 2. ?mode=summary : Counts all comments and returns a summary for the chart.

const allComments = require('./comments.json');

// --- This map MUST exactly match the strings in your comments.json file ---
const classificationMap = {
    'cognitive': 'cognitive fatigue related to peptides',
    'physical': 'physical fatigue related to peptides',
    'emotional': 'emotional fatigue related to peptides',
    'general': 'general peptide discussion, no fatigue mentioned',
    'fatigue-not-peptides': 'fatigue mentioned, but not related to peptides',
    'irrelevant': 'irrelevant or other topic'
};

exports.handler = async (event) => {
    const { category, mode } = event.queryStringParameters;

    // --- NEW: Handle request for summary data for the chart ---
    if (mode === 'summary') {
        const counts = {};
        // Initialize counts for all categories in the map to 0
        for (const key in classificationMap) {
            counts[key] = 0;
        }

        // Count occurrences of each classification in the data
        for (const comment of allComments) {
            for (const key in classificationMap) {
                if (comment.fatigue_classification === classificationMap[key]) {
                    counts[key]++;
                    break; // Move to the next comment once matched
                }
            }
        }
        
        return {
            statusCode: 200,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(counts),
        };
    }

    // --- Original logic for fetching comments by category ---
    if (!category) {
        return {
            statusCode: 400,
            body: JSON.stringify({ error: 'A "category" or "mode" parameter is required.' }),
        };
    }

    const targetClassification = classificationMap[category.toLowerCase()];

    if (!targetClassification) {
        return { statusCode: 200, body: JSON.stringify([]) };
    }

    const filteredComments = allComments.filter(comment => 
        comment.fatigue_classification === targetClassification
    );

    return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(filteredComments),
    };
};