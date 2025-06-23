const allComments = require('./comments.json');

const classificationMap = {
    'cognitive': 'cognitive fatigue related to peptides',
    'physical': 'physical fatigue related to peptides',
    'emotional': 'emotional fatigue related to peptides',
    'general': 'general peptide discussion, no fatigue mentioned',
    'fatigue-not-peptides': 'fatigue mentioned, but not related to peptides',
    'irrelevant': 'irrelevant or other topic'
};

// --- Helper function to calculate word frequencies ---
function getWordFrequencies(comments) {
    const wordCounts = {};
    const stopWords = new Set([
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 
        'he', 'him', 'his', 'she', 'her', 'it', 'its', 'they', 'them', 'their', 'theirs',
        'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
        'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'to', 'from',
        'in', 'out', 'on', 'off', 'over', 'under', 'again', 'then', 'once', 'here', 'there', 'when',
        'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
        'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
        'just', 'don', 'should', 'now'
    ]);

    comments.forEach(comment => {
        // Simple word tokenization and cleaning
        const words = comment.comment_text_cleaned.toLowerCase().match(/\b\w{3,}\b/g) || [];
        words.forEach(word => {
            if (!stopWords.has(word) && isNaN(word)) { // Exclude stop words and pure numbers
                wordCounts[word] = (wordCounts[word] || 0) + 1;
            }
        });
    });

    // Convert to an array format the word cloud library can use
    return Object.entries(wordCounts).map(([text, value]) => ({ text, value }));
}

exports.handler = async (event) => {
    const { category, mode } = event.queryStringParameters;

    if (mode === 'summary') {
        // Same summary logic as before
        const counts = {};
        for (const key in classificationMap) { counts[key] = 0; }
        for (const comment of allComments) {
            for (const key in classificationMap) {
                if (comment.fatigue_classification === classificationMap[key]) {
                    counts[key]++;
                    break;
                }
            }
        }
        return { statusCode: 200, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(counts) };
    }

    if (!category) {
        return { statusCode: 400, body: JSON.stringify({ error: 'Category or mode is required.' }) };
    }

    const targetClassification = classificationMap[category.toLowerCase()];
    if (!targetClassification) return { statusCode: 200, body: JSON.stringify({ comments: [], words: [] }) };

    const filteredComments = allComments.filter(comment => 
        comment.fatigue_classification === targetClassification
    );

    // --- NEW: Calculate word frequencies for the filtered comments ---
    const wordFrequencies = getWordFrequencies(filteredComments);
    
    // --- NEW: Return both comments and words ---
    const responsePayload = {
        comments: filteredComments,
        words: wordFrequencies
    };

    return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(responsePayload),
    };
};