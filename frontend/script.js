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
        pigeon.style.transform = `translate(${e.clientX}px, ${e.clientY}px)`;
    });

    // --- Dark Mode Logic ---
    function enableDarkMode(isDark) {
        body.classList.toggle('dark-mode', isDark);
        localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
    }
    
    darkModeToggle.addEventListener('change', () => {
        enableDarkMode(darkModeToggle.checked);
    });

    // Check for saved dark mode preference on page load
    if (localStorage.getItem('darkMode') === 'enabled') {
        darkModeToggle.checked = true;
        enableDarkMode(true);
    }
    
    // --- Chart Logic ---
    let commentsChart = null;
    async function fetchAndRenderChart() {
        try {
            const response = await fetch(`/.netlify/functions/get-comments?mode=summary`);
            const data = await response.json();
            const labels = ['Cognitive', 'Physical', 'Emotional', 'General', 'Other Fatigue', 'Irrelevant'];
            const counts = [
                data.cognitive, data.physical, data.emotional, data.general, data['fatigue-not-peptides'], data.irrelevant
            ];

            const ctx = document.getElementById('comments-chart').getContext('2d');
            
            if(commentsChart) {
                commentsChart.destroy(); // Clear previous chart if it exists
            }

            commentsChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Number of High-Confidence Comments',
                        data: counts,
                        backgroundColor: [
                            'rgba(236, 64, 122, 0.6)',
                            'rgba(77, 182, 172, 0.6)',
                            'rgba(66, 165, 245, 0.6)',
                            'rgba(156, 39, 176, 0.6)',
                            'rgba(255, 167, 38, 0.6)',
                            'rgba(158, 158, 158, 0.6)'
                        ],
                        borderColor: [
                            'rgba(236, 64, 122, 1)',
                            'rgba(77, 182, 172, 1)',
                            'rgba(66, 165, 245, 1)',
                            'rgba(156, 39, 176, 1)',
                            'rgba(255, 167, 38, 1)',
                            'rgba(158, 158, 158, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1 // Ensure y-axis shows whole numbers
                            }
                        }
                    },
                    plugins: {
                        legend: {
                           display: false
                        }
                    }
                }
            });

        } catch (error) {
            console.error("Failed to load chart data:", error);
        }
    }
    
    // --- Fetch Logic ---
    fetchButton.addEventListener('click', () => {
        const selectedCategory = categorySelect.value;
        fetchComments(selectedCategory);
    });

    async function fetchComments(category) {
        resultsContainer.innerHTML = '';
        loadingArea.classList.remove('hidden');
        try {
            const response = await fetch(`/.netlify/functions/get-comments?category=${category}`);
            const comments = await response.json();
            displayComments(comments);
        } catch (error) {
            resultsContainer.innerHTML = `<p class="error-message">Failed to fetch comments.</p>`;
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
            card.innerHTML = `
                <p class="comment-body">${comment.comment_text_cleaned}</p>
                <div class="comment-meta">
                    <span class="post-title">From post: "${comment.post_title}"</span>
                    <span class="meta-item">Confidence: ${confidence}%</span>
                </div>`;
            
            resultsContainer.appendChild(card);
            
            // Trigger the animation with a slight delay for a cascade effect
            setTimeout(() => {
                card.classList.add('show');
            }, 100 * index);
        });
    }
    
    // --- Initial Load ---
    fetchAndRenderChart(); // Load the chart as soon as the page loads
});