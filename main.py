import uuid
import json
import logging
from pprint import pprint
from dotenv import load_dotenv
load_dotenv()
from backend.src.graph.workflow import app

logging.basicConfig(
    level = logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("compliance-runner")

def run_cli_simulation():

    session_id = str(uuid.uuid4())
    logger.info(f"starting Audit session : {session_id}")

    initial_inputs = {
        "video_url" : "",
        "video_id" : f"vid_{session_id[:8]}",
        "compliance_results" : [],
        "errors" : []
    }

    print("initializing workflow------------------------------")
    print(f"Input Payload : {json.dumps(initial_inputs,indent=2)}")

    try:
        final_state = app.invoke(initial_inputs)
        print("workflow execution complete")

        print("compliance audit report----------------------------")
        print(f"video id : {final_state.get("video_id")}")
        print(f"status : {final_state.get("final_status")}")
        results = final_state.get("compliance_results",[])

        if results:
            for issue in results:
                print(f"-[{issue.get("severity")}] [{issue.get("category")}] : [{issue.get("description")}]")

        else:
            print("No voilations detected")
        
    except Exception as e:
        logger.error(f"workflow execution failed : {e}")

if __name__ == "__main__":
    run_cli_simulation()
