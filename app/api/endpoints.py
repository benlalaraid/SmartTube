from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from app.services.downloader import YouTubeService
from app.services.rag import rag_service, RAGService # Fix import if needed, assuming instantiated in rag.py or here
import os

router = APIRouter()
yt_service = YouTubeService()

class VideoRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    format_id: str
    video_id: str

class ChatRequest(BaseModel):
    video_id: str
    question: str

@router.post("/info")
async def get_video_info(request: VideoRequest):
    info = yt_service.get_video_info(request.url)
    if not info:
        raise HTTPException(status_code=400, detail="Could not fetch video info")
    return info

@router.post("/download")
async def download_video(request: DownloadRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(yt_service.download_video, request.url, request.format_id, request.video_id)
    return {"status": "Download started", "video_id": request.video_id}

@router.get("/progress/{video_id}")
async def get_progress(video_id: str):
    return yt_service.get_progress(video_id)

@router.post("/analyze")
async def analyze_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """
    Download subtitles and ingest into RAG.
    """
    info = yt_service.get_video_info(request.url)
    if not info:
         raise HTTPException(status_code=400, detail="Video invalid")
         
    video_id = info['id']
    
    # Try to download subtitles
    # We need to know which lang to pick. Default to 'en'.
    # Warning: this is synchronous for the subtitle DL part in helper, but lightweight usually.
    sub_path = yt_service.download_subtitles(request.url, lang='en')
    
    if not sub_path:
        # Try auto-subs if no manual subs
        sub_path = yt_service.download_subtitles(request.url, lang='en') # logic in downloader needs to handle auto
        # Actually my downloader.py handles both via writesubtitles/writeautomaticsub
        pass

    if sub_path and os.path.exists(sub_path):
        background_tasks.add_task(rag_service.process_subtitles, sub_path, video_id)
        return {"status": "Analysis started", "video_id": video_id}
    else:
        return {"status": "No subtitles found to analyze", "video_id": video_id}

@router.post("/chat")
async def chat_about_video(request: ChatRequest):
    try:
        answer = rag_service.get_answer(request.video_id, request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
