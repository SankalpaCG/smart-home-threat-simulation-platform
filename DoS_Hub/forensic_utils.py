import json
import csv
import os
import time
from datetime import datetime

class DualLogger:
    """
    Sovereignty Framework Forensic Utility
    Automatically synchronizes research telemetry into both JSON and CSV formats.
    """
    @staticmethod
    def log_session(data, folder, base_name):
        """Saves a session summary/report in both JSON and CSV."""
        os.makedirs(folder, exist_ok=True)
        
        # 1. Save JSON (Standard Indented)
        json_path = os.path.join(folder, f"{base_name}.json")
        with open(json_path, 'w') as f:
            json.dump(data, f, indent=4)
            
        # 2. Save CSV (Flattened)
        csv_path = os.path.join(folder, f"{base_name}.csv")
        try:
            # Flatten nested dictionaries for CSV compatibility
            flat_data = DualLogger._flatten_dict(data)
            headers = list(flat_data.keys())
            
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerow(flat_data)
        except Exception as e:
            print(f"⚠️  CSV Logging Warning: {e}")

        return json_path, csv_path

    @staticmethod
    def append_raw(data, folder, base_name, headers=None):
        """Appends streaming data to both CSV and JSON Lines (.jsonl)."""
        os.makedirs(folder, exist_ok=True)
        
        # 1. Append JSON Lines
        json_path = os.path.join(folder, f"{base_name}.json")
        with open(json_path, 'a') as f:
            f.write(json.dumps(data) + "\n")
            
        # 2. Append CSV
        csv_path = os.path.join(folder, f"{base_name}.csv")
        file_exists = os.path.isfile(csv_path)
        
        if not headers:
            headers = list(data.keys())
            
        with open(csv_path, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            if not file_exists:
                writer.writeheader()
            # Only write keys that are in headers to avoid errors
            row = {k: data.get(k, "") for k in headers}
            writer.writerow(row)

    @staticmethod
    def _flatten_dict(d, parent_key='', sep='_'):
        """Flattens a nested dictionary for CSV representation."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(DualLogger._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

def get_timestamp():
    return int(time.time())

def get_iso_now():
    return datetime.now().isoformat()
