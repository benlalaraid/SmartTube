# Smart YouTube Downloader & AI Assistant

A modern web application for downloading YouTube videos and interacting with their content using AI. Built with FastAPI and LangChain, it enables video/audio downloads and intelligent chat based on subtitle analysis (RAG).

## Key Features
- Download YouTube videos or audio in multiple formats and resolutions  
- Real-time download progress tracking  
- AI-powered chat with videos using subtitle-based retrieval  
- Lazy loading of AI models for fast startup  

## Tech Stack
- **Backend**: FastAPI, Uvicorn, Python  
- **Core**: yt-dlp, LangChain, ChromaDB, HuggingFace  
- **Frontend**: HTML, CSS, JavaScript  
- **Models**: all-MiniLM-L6-v2 (embeddings), Mistral-7B (LLM)  

## Usage
Run the application with Uvicorn and open `http://localhost:8000` in your browser.  
Paste a YouTube link to download the content or analyze the video and chat with it.
