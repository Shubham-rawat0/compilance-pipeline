from fastapi import FastAPI , HTTPException
import uuid
import logging
from pydantic import BaseModel
from typing import List , Optional
from dotenv import load_dotenv
from fastapi.concurrency import run_in_threadpool
from backend.src.api.telemetry import setup_telemetry
from backend.src.graph.workflow import app as compliance_graph

load_dotenv(override= True)
setup_telemetry()

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("api-server")

app=FastAPI(
    title=" Compliance api",
    description = "API for auditiong video content against the brand compliance rules",
    version = "1.0.0" 
)

class AuditRequest(BaseModel):
    video_url : str

class ComplianceIssue(BaseModel):
    category : str
    severity : str
    description : str

class AuditResponse(BaseModel):
    session_id : str
    video_id : str
    final_report : str
    status : str
    compliance_results : List[ComplianceIssue]


@app.post("/audit", response_model = AuditResponse)

async def audit_video(request : AuditRequest): 
    
    session_id  = str(uuid.uuid4())
    video_id_short = f"vid_{session_id[:8]}"

    logger.info(f"Received the audit request : {request.video_url}")

    initial_inputs = {
        "video_url" : request.video_url,
        "video_id" : video_id_short,
        "compliance_results" : [],
        "errors" : []
    }

    try :
        final_state = await run_in_threadpool(compliance_graph.invoke, initial_inputs)

        return AuditResponse(
            session_id = session_id,
            video_id= final_state.get("video_id"),
            status=  final_state.get("final_status","UNKOWN"),
            final_report= final_state.get("final_report","No report generated"),
            compliance_results= final_state.get("compliance_results",[])
        )
    
    except Exception as e:
        logger.error(f"Audit failed {str(e)}")
        raise HTTPException(
            status_code= 500 ,
            detail = f"Workflow execution failed : {str(e)}"
        )
    

@app.get("/health")

def health_check():

    return {"status":"healthy",
            "service":"Brand Guardian"}