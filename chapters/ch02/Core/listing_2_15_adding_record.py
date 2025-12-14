from core.logger import ArtifactLogger
from datetime import datetime

logger = ArtifactLogger()

run_id = "1234567890"
timestamp = datetime.now().isoformat()
input_data = "Check reachability of example.com"
output_data = "example.com is reachable."
user_email = "user@example.com"

record = {
    "run_id": run_id,
    "agent": "triage",
    "stage": "recon",
    "timestamp": timestamp,
    "input": input_data,
    "output": output_data,
    "approved_by": user_email,
    "status": "success"
}
logger.write(record)
