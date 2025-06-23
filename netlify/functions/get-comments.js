// netlify/functions/get-comments.js (Verified and Complete Version)

const allComments = require('./comments.json');

exports.handler = async (event) => {
  const category = event.queryStringParameters.category;

  if (!category) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'A "category" parameter is required.' }),
    };
  }
  
  // This map MUST exactly match the strings in your comments.json file
  const classificationMap = {
    'cognitive': 'cognitive fatigue related to peptides',
    'physical': 'physical fatigue related to peptides', // <-- This is the key one
    'emotional': 'emotional fatigue related to peptides',
    'general': 'general peptide discussion, no fatigue mentioned',
    
    // It's a good idea to add mappings for the other categories your model found too
    'fatigue-not-peptides': 'fatigue mentioned, but not related to peptides',
    'irrelevant': 'irrelevant or other topic'
  };

  const targetClassification = classificationMap[category.toLowerCase()];

  // If the category doesn't exist in our map, return an empty array
  if (!targetClassification) {
    return {
        statusCode: 200,
        body: JSON.stringify([]),
    };
  }

  const filteredComments = allComments.filter(comment => 
    comment.fatigue_classification === targetClassification
  );

  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(filteredComments),
  };
};