document.addEventListener('DOMContentLoaded', () => {
    const fetchButton = document.getElementById('fetch-button');
    const categorySelect = document.getElementById('category-select');
    const resultsContainer = document.getElementById('results-container');
    const loadingArea = document.querySelector('.loading-area');

    fetchButton.addEventListener('click', () => {
        const selectedCategory = categorySelect.value;
        fetchComments(selectedCategory);
    });

    async function fetchComments(category) {
        // Clear previous results and show spinner
        resultsContainer.innerHTML = '';
        loadingArea.classList.remove('hidden');

        try {
            // This is the endpoint for your Netlify Function
            const response = await fetch(`/.netlify/functions/get-comments?category=${category}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const comments = await response.json();
            displayComments(comments);

        } catch (error) {
            console.error('Error fetching comments:', error);
            resultsContainer.innerHTML = `<p class="error-message">Failed to fetch comments. Please check the console for details.</p>`;
        } finally {
            // Hide spinner
            loadingArea.classList.add('hidden');
        }
    }

    function displayComments(comments) {
        if (comments.length === 0) {
            resultsContainer.innerHTML = `<p class="info-message">No high-confidence comments found for this category.</p>`;
            return;
        }

        comments.forEach(comment => {
            const card = document.createElement('div');
            card.className = 'comment-card';

            // Sanitize comment body to prevent HTML injection
            const commentBody = document.createElement('p');
            commentBody.className = 'comment-body';
            commentBody.textContent = comment.comment_text_cleaned;

            const confidence = (comment.classification_confidence * 100).toFixed(1);

            card.innerHTML = `
                ${commentBody.outerHTML}
                <div class="comment-meta">
                    <span class="post-title">From post: "${comment.post_title}"</span>
                    <span class="meta-item">Confidence: ${confidence}%</span>
                </div>
            `;
            resultsContainer.appendChild(card);
        });
    }
});