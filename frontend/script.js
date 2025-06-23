document.addEventListener('DOMContentLoaded', () => {
    // --- Element Selectors ---
    const fetchButton = document.getElementById('fetch-button');
    const categorySelect = document.getElementById('category-select');
    const resultsContainer = document.getElementById('results-container');
    const loadingArea = document.querySelector('.loading-area');
    const pigeon = document.getElementById('pigeon-cursor');
    const darkModeToggle = document.getElementById('dark-mode-checkbox');
    const body = document.body;

    // --- Pigeon Cursor Logic ---
    document.addEventListener('mousemove', (e) => {
        window.requestAnimationFrame(() => {
            pigeon.style.transform = `translate(${e.clientX}px, ${e.clientY}px) translate(-50%, -50%)`;
        });
    });

    // --- Dark Mode Logic ---
    function setDarkMode(isDark) {
        body.classList.toggle('dark-mode', isDark);
        localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
    }
    darkModeToggle.addEventListener('change', () => {
        setDarkMode(darkModeToggle.checked);
    });
    // On page load, check for saved preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        darkModeToggle.checked = true;
        setDarkMode(true);
    }
    
    // --- Chart Logic ---
    let commentsChart = null;
    async function fetchAndRenderChart() {
        try {
            const response = await fetch(`/.netlify/functions/get-comments?mode=summary`);
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            
            const labels = ['Cognitive', 'Physical', 'Emotional', 'General', 'Other Fatigue', 'Irrelevant'];
            const counts = [
                data.cognitive, data.physical, data.emotional, data.general, data['fatigue-not-peptides'], data.irrelevant
            ];

            const ctx = document.getElementById('comments-chart').getContext('2d');
            if(commentsChart) commentsChart.destroy();

            commentsChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Number of High-Confidence Comments',
                        data: counts,
                        backgroundColor: [ '#EC407A', '#4DB6AC', '#42A5F5', '#AB47BC', '#FFA726', '#9E9E9E' ],
                        borderColor: [ '#d81b60', '#00796B', '#1E88E5', '#8E24AA', '#FB8C00', '#616161' ],
                        borderWidth: 1,
                        borderRadius: 5,
                    }]
                },
                options: { scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }, plugins: { legend: { display: false } } }
            });

        } catch (error) { console.error("Failed to load chart data:", error); }
    }
    
    // --- Comments Fetch Logic ---
    fetchButton.addEventListener('click', () => fetchComments(categorySelect.value));

    async function fetchComments(category) {
        resultsContainer.innerHTML = '';
        loadingArea.classList.remove('hidden');
        try {
            const response = await fetch(`/.netlify/functions/get-comments?category=${category}`);
            const comments = await response.json();
            displayComments(comments);
        } catch (error) {
            resultsContainer.innerHTML = `<p class="info-message">Failed to fetch comments.</p>`;
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
            
            // Create a paragraph element and set its text content to avoid HTML injection
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
            
            // Trigger the fade-in animation with a cascade effect
            setTimeout(() => { card.classList.add('show'); }, 100 * index);
        });
    }
    
    // --- Initial Page Load ---
    fetchAndRenderChart();
});