import json
import csv
import os
import time
import threading
from datetime import datetime

class DualLogger:
    """
    Unified Forensic Telemetry Logger.
    Synchronizes telemetry into both JSON Lines (.jsonl) and CSV formats.
    """
    
    # Class-level lock to ensure thread-safe disk I/O across concurrent attack threads.
    _io_lock = threading.Lock()

    @staticmethod
    def log_session(data: dict, folder: str, base_name: str) -> tuple:
        """
        Saves a session summary/report in both JSON and CSV.
        """
        os.makedirs(folder, exist_ok=True)
        
        json_path = os.path.join(folder, f"{base_name}.json")
        csv_path = os.path.join(folder, f"{base_name}.csv")
        
        with DualLogger._io_lock:
            # 1. Save JSON (Standard Indented)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
                
            # 2. Save CSV (Flattened)
            try:
                # Flatten nested dictionaries for CSV compatibility
                flat_data = DualLogger._flatten_dict(data)
                headers = list(flat_data.keys())
                
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerow(flat_data)
            except Exception as e:
                print(f"CSV Logging Warning: {e}")
                
        return json_path, csv_path

    @staticmethod
    def append_raw(data: dict, folder: str, base_name: str, headers: list = None):
        """
        Appends streaming data to both CSV and JSON Lines (.jsonl).
        """
        os.makedirs(folder, exist_ok=True)
        
        json_path = os.path.join(folder, f"{base_name}.json")
        csv_path = os.path.join(folder, f"{base_name}.csv")
        
        with DualLogger._io_lock:
            # 1. Append JSON Lines
            with open(json_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data) + "\n")
                
            # 2. Append CSV
            file_exists = os.path.isfile(csv_path)
            
            if not headers:
                headers = list(data.keys())
                
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                
                if not file_exists:
                    writer.writeheader()
                    
                # Only write keys that are in headers to avoid errors
                row = {k: data.get(k, 0.0) for k in headers}
                writer.writerow(row)

    @staticmethod
    def _flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
        """Flattens a nested dictionary for CSV representation."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(DualLogger._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

def get_timestamp() -> int:
    return int(time.time())

def get_iso_now() -> str:
    return datetime.now().isoformat()
