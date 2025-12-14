import json, uuid, os

class ArtifactLogger:
    def __init__(self, run_dir="runs"):
        os.makedirs(run_dir, exist_ok=True)
        self.file = open(f"{run_dir}/{uuid.uuid4()}.jsonl", "w", encoding="utf8")

    def write(self, record: dict):
        json.dump(record, self.file)
        self.file.write("\n")
        self.file.flush()
