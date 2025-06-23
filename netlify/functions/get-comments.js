// This is the correct, simple version that matches your frontend script.
// It just finds the comments and sends them back in a simple array.

const allComments = require('./comments.json');

exports.handler = async (event) => {
  const category = event.queryStringParameters.category;

  if (!category) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'A "category" parameter is required.' }),
    };
  }
  
  const classificationMap = {
    'cognitive': 'cognitive fatigue related to peptides',
    'physical': 'physical fatigue related to peptides',
    'emotional': 'emotional fatigue related to peptides',
    'general': 'general peptide discussion, no fatigue mentioned',
    'fatigue-not-peptides': 'fatigue mentioned, but not related to peptides',
    'irrelevant': 'irrelevant or other topic'
  };

  const targetClassification = classificationMap[category.toLowerCase()];

  if (!targetClassification) {
    return { statusCode: 200, body: JSON.stringify([]) }; // Return empty array if no match
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