// This file reads your pre-processed JSON data and sends the relevant comments to the frontend.
// It acts as a simple, serverless API endpoint for your project.

// The 'require' function is the easiest way for a Netlify Function to load a local JSON file.
// It automatically parses the JSON into a JavaScript array of objects.
// This requires the 'comments.json' file to be in this same /functions directory.
const allComments = require('./comments.json');

exports.handler = async (event) => {
  // --- Step 1: Get the category requested by the user ---
  // The frontend will make a request like: `/.netlify/functions/get-comments?category=cognitive`
  // 'event.queryStringParameters' gives us access to the part after the '?'.
  const category = event.queryStringParameters.category;

  // --- Step 2: Handle cases where no category is provided ---
  if (!category) {
    return {
      statusCode: 400, // 400 means "Bad Request"
      body: JSON.stringify({ error: 'A "category" parameter is required.' }),
    };
  }

  // --- Step 3: Map the simple category from the dropdown to the full classification text in your data ---
  // This allows the frontend to use simple words like "cognitive", while the data has the full text.
  const classificationMap = {
    'cognitive': 'cognitive fatigue related to peptides',
    'physical': 'physical fatigue related to peptides',
    'emotional': 'emotional fatigue related to peptides',
    'general': 'general peptide discussion, no fatigue mentioned'
    // You can add more mappings here if you classify other fatigue types in the future.
  };

  const targetClassification = classificationMap[category.toLowerCase()];

  // --- Step 4: Filter the full list of comments ---
  // The .filter() method creates a new array containing only the comments
  // where the 'fatigue_classification' property matches our target.
  const filteredComments = allComments.filter(comment =>
    comment.fatigue_classification === targetClassification
  );

  // --- Step 5: Send the filtered data back to the frontend ---
  // A successful response must have a statusCode of 200.
  // The body must be a JSON string, which is why we use JSON.stringify().
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json', // Lets the browser know it's receiving JSON data
    },
    body: JSON.stringify(filteredComments),
  };
};