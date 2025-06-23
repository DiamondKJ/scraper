document.addEventListener('DOMContentLoaded', () => {
    // --- Element Selectors ---
    const resultsContainer = document.getElementById('results-container');
    const loadingArea = document.querySelector('.loading-area');
    const chartCanvas = document.getElementById('comments-chart');
    const pigeon = document.getElementById('pigeon-cursor');
    const darkModeToggle = document.getElementById('dark-mode-checkbox');
    const bgVideo = document.getElementById('bg-video');
    const wordcloudContainer = document.getElementById('wordcloud-container');
    const wordcloudDiv = document.getElementById('wordcloud');

    // --- Asset Map for Thematic Backgrounds ---
    const themeAssets = {
        cognitive: 'https://cdn.pixabay.com/video/2023/10/24/184131-878508112_large.mp4',
        physical: 'https://cdn.pixabay.com/video/2020/03/03/32955-402484080_large.mp4',
        emotional: 'https://cdn.pixabay.com/video/2024/02/21/200611-917711904_large.mp4',
    };

    // --- Pigeon Cursor Logic ---
    document.addEventListener('mousemove', (e) => {
        // Use requestAnimationFrame for smoother, more efficient animations
        window.requestAnimationFrame(() => {
            pigeon.style.transform = `translate(${e.clientX}px, ${e.clientY}px) translate(-50%, -50%)`;
        });
    });

    // --- Dark Mode Logic ---
    function setDarkMode(isDark) {
        document.body.classList.toggle('dark-mode', isDark);
        localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
    }
    darkModeToggle.addEventListener('change', () => setDarkMode(darkModeToggle.checked));
    // Check for saved preference on page load
    if (localStorage.getItem('darkMode') === 'enabled') {
        darkModeToggle.checked = true;
        setDarkMode(true);
    }
    
    // --- Chart Logic ---
    let commentsChart = null;
    const chartLabels = ['Cognitive', 'Physical', 'Emotional', 'General', 'Other Fatigue', 'Irrelevant'];
    const chartCategoryKeys = ['cognitive', 'physical', 'emotional', 'general', 'fatigue-not-peptides', 'irrelevant'];

    async function fetchAndRenderChart() {
        try {
            const response = await fetch(`/.netlify/functions/get-comments?mode=summary`);
            if (!response.ok) throw new Error(`Chart data fetch failed: ${response.statusText}`);
            const data = await response.json();
            
            const counts = chartCategoryKeys.map(key => data[key] || 0);

            const ctx = chartCanvas.getContext('2d');
            if(commentsChart) commentsChart.destroy();

            commentsChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: chartLabels,
                    datasets: [{
                        label: 'Number of High-Confidence Comments',
                        data: counts,
                        backgroundColor: [ '#EC407A', '#4DB6AC', '#42A5F5', '#AB47BC', '#FFA726', '#9E9E9E' ],
                        borderColor: [ '#d81b60', '#00796B', '#1E88E5', '#8E24AA', '#FB8C00', '#616161' ],
                        borderWidth: 1,
                        borderRadius: 5,
                    }]
                },
                options: {
                    onClick: (event, elements) => {
                        if (elements.length > 0) {
                            const chartElement = elements[0];
                            const index = chartElement.index;
                            const categoryKey = chartCategoryKeys[index];
                            fetchComments(categoryKey); // Fetch data for the clicked bar
                        }
                    },
                    scales: { y: { beginAtZero: true, ticks: { stepSize: 1, color: document.body.classList.contains('dark-mode') ? '#c9d1d9' : '#444' } }, x: { ticks: { color: document.body.classList.contains('dark-mode') ? '#c9d1d9' : '#444' } } },
                    plugins: { legend: { display: false } },
                    onHover: (event, chartElement) => {
                        event.native.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
                    }
                }
            });

        } catch (error) { console.error("Failed to load chart data:", error); }
    }
    
    // --- Comments Fetch & Display Logic ---
    async function fetchComments(category) {
        // Clear previous results and set theme
        resultsContainer.innerHTML = '';
        wordcloudContainer.classList.add('hidden');
        loadingArea.classList.remove('hidden');
        setTheme(category);

        try {
            const response = await fetch(`/.netlify/functions/get-comments?category=${category}`);
            const payload = await response.json(); // Payload now contains { comments: [], words: [] }
            
            displayWordCloud(payload.words);
            displayComments(payload.comments);

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
            setTimeout(() => { card.classList.add('show'); }, 100 * index);
        });
    }

    // --- Word Cloud Logic ---
    function displayWordCloud(words) {
        if (!words || words.length === 0) {
            wordcloudContainer.classList.add('hidden');
            return;
        }

        wordcloudContainer.classList.remove('hidden');
        wordcloudDiv.innerHTML = ''; // Clear previous cloud

        const maxFontSize = 60;
        const minFontSize = 14;
        const maxFreq = words.length > 0 ? Math.max(...words.map(w => w.value)) : 1;
        
        // Scale font size based on frequency
        const fontScale = d3.scaleLinear()
                            .domain([0, maxFreq])
                            .range([minFontSize, maxFontSize]);

        const layout = d3.layout.cloud()
            .size([wordcloudDiv.clientWidth, wordcloudDiv.clientHeight])
            .words(words)
            .padding(5)
            .rotate(() => (Math.random() > 0.7) ? 90 : 0)
            .font("Poppins")
            .fontSize(d => fontScale(d.value))
            .on("end", draw);

        layout.start();

        function draw(words) {
            d3.select("#wordcloud").append("svg")
                .attr("width", layout.size()[0])
                .attr("height", layout.size()[1])
                .append("g")
                .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
                .selectAll("text")
                .data(words)
                .enter().append("text")
                .attr("class", "word")
                .style("font-size", d => d.size + "px")
                .style("fill", (d, i) => d3.schemeCategory10[i % 10])
                .attr("text-anchor", "middle")
                .attr("transform", d => "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")")
                .text(d => d.text);
        }
    }

    // --- Thematic Visuals Logic ---
    function setTheme(category) {
        // Reset all theme classes first
        document.body.classList.remove('theme-cognitive', 'theme-physical', 'theme-emotional');

        if (themeAssets[category]) {
            bgVideo.src = themeAssets[category];
            document.body.classList.add(`theme-${category}`);
        } else {
            bgVideo.src = ''; // Clear video source for default themes
        }
    }
    
    // --- Initial Page Load ---
    fetchAndRenderChart();
});