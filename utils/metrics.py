import os
import time

class IngestionMetrics:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def file_size_kb(self):
        return round(os.path.getsize(self.file_path) / 1024, 2)

    def duration_seconds(self):
        return round(self.end_time - self.start_time, 3)