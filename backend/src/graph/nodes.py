from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from backend.src.graph.state import VideoAuditState , ComplianceIssue
from backend.src.services.video_indexer import VideoIndexerService
import logging
import os
from typing import Dict, Any

logger = logging.getLogger("brand-guardian")
logging.basicConfig(level=logging.INFO)

def index_video_node(state:VideoAuditState)->Dict[str,Any]:
    video_url = state.get("video_url")
    video_id_input = state.get("video_id","vid_demo")
    logger.info(f"---------[node:indexer] processing : {video_url}")

    local_filename = "temp_audio_video.mp4"

    try:
        vi_service = VideoIndexerService()
        if "youtube.com" in video_url or "youtu.be" in video_url:
            local_path = vi_service.download_youtube_video(video_url , output_path=local_filename)
        else:
            raise Exception("Please provide a valid Youtube URL for this test.")
        
        azure_video_id = vi_service.upload_video(local_path,video_name=video_id_input)

        logger.info(f"Upload sucees: Azure ID: {azure_video_id}")

        if os.path.exists(local_path):
            os.remove(local_path)
        
        raw_insights= vi_service.wait_for_processing(azure_video_id)
        clean_data = vi_service.extract_data(raw_insights)
        logger.info("-------[node:indexer] extraction complete------")
        return clean_data
    except Exception as e:
        logger.error(f"Video indexer failed : {e}")
        return {
            "errors":[str(e)],
            "final_status":"FAIL",
            "transccript" :"",
            "ocr_text":[],           
        }