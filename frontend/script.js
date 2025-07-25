// --- Initial Page Load Screen ---
window.addEventListener('load', () => {
    // We add a short delay just to ensure everything is rendered, then start the exit animation
    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 500); // 0.5 second delay after page fully loads
});

document.addEventListener('DOMContentLoaded', () => {
    // --- Element Selectors ---
    const fetchButton = document.getElementById('fetch-button');
    const categorySelect = document.getElementById('category-select');
    const resultsContainer = document.getElementById('results-container');
    const loadingArea = document.querySelector('.loading-area');
    const pigeon = document.getElementById('pigeon-cursor');

    // --- Pigeon Cursor Logic ---
    document.addEventListener('mousemove', (e) => {
        window.requestAnimationFrame(() => {
            pigeon.style.transform = `translate(${e.clientX}px, ${e.clientY}px) translate(-50%, -50%)`;
        });
    });
    
    // --- Main Fetch Logic ---
    if (fetchButton) {
        fetchButton.addEventListener('click', () => {
            fetchComments(categorySelect.value);
        });
    }

    async function fetchComments(category) {
        resultsContainer.innerHTML = '';
        loadingArea.classList.remove('hidden');

        try {
            const response = await fetch(`/.netlify/functions/get-comments?category=${category}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const comments = await response.json(); 
            displayComments(comments);

        } catch (error) {
            console.error('Error fetching comments:', error);
            resultsContainer.innerHTML = `<p class="info-message">Failed to fetch comments. Check the console.</p>`;
        } finally {
            loadingArea.classList.add('hidden');
        }
    }

    function displayComments(comments) {
        if (comments.length === 0) {
            resultsContainer.innerHTML = `<p class="info-message">No high-confidence comments found for this category.</p>`;
            return;
        }

        comments.forEach((comment, index) => {
            const card = document.createElement('div');
            card.className = 'comment-card';
            const confidence = (comment.classification_confidence * 100).toFixed(1);
            
            const commentBody = document.createElement('p');
            commentBody.className = 'comment-body';
            commentBody.textContent = comment.comment_text_cleaned;
            
            card.innerHTML = `
                ${commentBody.outerHTML}
                <div class="comment-meta">
                    <span class="post-title">From post: "${comment.post_title}"</span>
                    <span class="meta-item">Confidence: ${confidence}%</span>
                </div>`;
            
            resultsContainer.appendChild(card);
            
            setTimeout(() => card.classList.add('show'), 100 * index);
        });
    }
});