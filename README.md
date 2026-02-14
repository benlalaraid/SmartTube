# Smart YouTube Downloader & AI Assistant

A modern, full-featured web application that allows you to download YouTube videos and interact with them using Artificial Intelligence. Built with FastAPI, LangChain, and modern web technologies.

![App Preview](https://via.placeholder.com/800x400.png?text=Smart+YouTube+Downloader+Preview)

## 🚀 Features

- **🎥 Smart Downloader**: Download videos or audio in various formats/resolutions.
- **📊 Real-time Progress**: Track your downloads with a visual progress bar.
- **🤖 AI Chat (RAG)**: Chat with the video! The app analyzes subtitles and lets you ask questions about the content (e.g., "Summarize the key points").
- **⚡ Lazy AI Loading**: AI models load only when needed to ensure fast application startup.
- **🎨 Modern UI**: A clean, Google-inspired interface with a responsive design.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Uvicorn
- **Core Logic**: `yt-dlp` (Downloads), `LangChain`, `ChromaDB` (Vector Store), `HuggingFace` (LLM & Embeddings)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI Models**: `all-MiniLM-L6-v2` (Embeddings), `Mistral-7B` (Inference)

## 📦 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/smart-youtube-downloader.git
    cd smart-youtube-downloader
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install fastapi uvicorn yt-dlp chromadb sentence-transformers langchain-huggingface jinja2 python-multipart
    ```

4.  **Optional Configuration**:
    Create a `.env` file if you face rate limits with HuggingFace:
    ```env
    HF_API_TOKEN=your_huggingface_token
    ```

## 🚀 Usage

1.  **Run the application**:
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    ```

2.  **Open in Browser**:
    Visit `http://localhost:8000`

3.  **Enjoy**: Paste a YouTube link, download it, or click "Analyze Video" to start chatting with it!

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).
