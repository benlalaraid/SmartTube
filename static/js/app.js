document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const videoUrlInput = document.getElementById('videoUrl');
    const searchBtn = document.getElementById('searchBtn');
    const loading = document.getElementById('loading');
    const content = document.getElementById('content');
    const toast = document.getElementById('toast');

    // Video Elements
    const videoTitle = document.getElementById('videoTitle');
    const videoDuration = document.getElementById('videoDuration').querySelector('span');
    const thumbnail = document.getElementById('thumbnail');
    const formatList = document.getElementById('formatList');

    // Chat Elements
    const analyzeBtn = document.getElementById('analyzeBtn');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');

    let currentVideoId = null;

    // Event Listeners
    searchBtn.addEventListener('click', handleSearch);
    videoUrlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });

    analyzeBtn.addEventListener('click', handleAnalyze);
    sendBtn.addEventListener('click', handleSendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSendMessage();
    });

    // Tab Switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(`${btn.dataset.tab}Tab`).classList.add('active');
        });
    });

    async function handleSearch() {
        const url = videoUrlInput.value.trim();
        if (!url) return showToast('Please enter a YouTube URL');

        loading.classList.remove('hidden');
        content.classList.add('hidden');

        try {
            const response = await fetch('/api/v1/info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            if (!response.ok) throw new Error('Failed to fetch video info');

            const data = await response.json();
            displayVideoInfo(data);
        } catch (error) {
            showToast(error.message);
        } finally {
            loading.classList.add('hidden');
        }
    }

    function displayVideoInfo(data) {
        currentVideoId = data.id;
        videoTitle.textContent = data.title;
        videoDuration.textContent = formatDuration(data.duration);
        thumbnail.src = data.thumbnail;

        // Populate formats
        formatList.innerHTML = '';
        data.formats.forEach(fmt => {
            const div = document.createElement('div');
            div.className = 'format-item';
            div.innerHTML = `
                <span>${fmt.ext.toUpperCase()} - ${fmt.resolution} (${formatBytes(fmt.filesize)})</span>
                <button class="download-btn" onclick="startDownload('${data.id}', '${fmt.format_id}')">
                    Download
                </button>
            `;
            formatList.appendChild(div);
        });

        content.classList.remove('hidden');
        // Reset chat
        chatMessages.innerHTML = '<div class="message system"><p>Click "Analyze Video" to start chatting about the content.</p></div>';
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analyze Video";
        chatInput.disabled = true;
        sendBtn.disabled = true;
    }

    async function handleAnalyze() {
        if (!currentVideoId) return;

        analyzeBtn.disabled = true;
        analyzeBtn.textContent = "Analyzing...";

        try {
            const response = await fetch('/api/v1/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: videoUrlInput.value.trim() })
            });

            const data = await response.json();

            if (data.status.includes('started')) {
                showToast('Analysis started. You can chat shortly.');
                chatInput.disabled = false;
                sendBtn.disabled = false;
                analyzeBtn.textContent = "Analysis In Progress";
                appendMessage('system', 'Video is being analyzed. You can ask questions now.');
            } else {
                showToast(data.status); // e.g. "No subtitles found"
                analyzeBtn.textContent = "Analysis Failed";
            }
        } catch (error) {
            showToast('Analysis failed: ' + error.message);
            analyzeBtn.textContent = "Analyze Video";
            analyzeBtn.disabled = false;
        }
    }

    async function handleSendMessage() {
        const text = chatInput.value.trim();
        if (!text || !currentVideoId) return;

        appendMessage('user', text);
        chatInput.value = '';

        try {
            const response = await fetch('/api/v1/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video_id: currentVideoId, question: text })
            });

            const data = await response.json();
            appendMessage('ai', data.answer);
        } catch (error) {
            appendMessage('system', 'Error: ' + error.message);
        }
    }

    function appendMessage(type, text) {
        const div = document.createElement('div');
        div.className = `message ${type}`;
        div.innerHTML = `<p>${text}</p>`;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Window global for onclick
    window.startDownload = async (videoId, formatId) => {
        const progressContainer = document.getElementById('progressContainer');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');

        progressContainer.classList.remove('hidden');
        progressBar.style.width = '0%';
        progressText.textContent = 'Starting...';

        try {
            await fetch('/api/v1/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: videoUrlInput.value.trim(),
                    format_id: formatId,
                    video_id: videoId
                })
            });

            // Start polling
            pollProgress(videoId);

        } catch (e) {
            showToast('Download request failed');
        }
    };

    function pollProgress(videoId) {
        const intervalId = setInterval(async () => {
            try {
                const res = await fetch(`/api/v1/progress/${videoId}`);
                const data = await res.json();

                const progressBar = document.getElementById('progressBar');
                const progressText = document.getElementById('progressText');

                if (data.status === 'downloading') {
                    progressBar.style.width = data.progress + '%';
                    progressText.textContent = `${data.progress}%`;
                } else if (data.status === 'completed') {
                    progressBar.style.width = '100%';
                    progressText.textContent = 'Completed!';
                    clearInterval(intervalId);
                    showToast('Download Completed Successfully!');
                    setTimeout(() => {
                        document.getElementById('progressContainer').classList.add('hidden');
                    }, 3000);
                } else if (data.status === 'error') {
                    progressText.textContent = 'Error!';
                    clearInterval(intervalId);
                    showToast('Download Error: ' + (data.error || 'Unknown'));
                }
            } catch (e) {
                console.error("Polling error", e);
            }
        }, 1000);
    }

    function showToast(msg) {
        toast.textContent = msg;
        toast.classList.remove('hidden');
        setTimeout(() => toast.classList.add('hidden'), 3000);
    }

    function formatDuration(seconds) {
        const date = new Date(null);
        date.setSeconds(seconds);
        return date.toISOString().substr(11, 8).replace(/^00:/, '');
    }

    function formatBytes(bytes, decimals = 2) {
        if (!+bytes) return 'N/A';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
    }
});
