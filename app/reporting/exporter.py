import json
import csv
import io
from typing import List, Dict, Any

class ReportExporter:
    """Exports generated reports to JSON or CSV formats."""
    
    @staticmethod
    def to_json(data: Dict[str, Any], indent: int = 2) -> str:
        return json.dumps(data, indent=indent)

    @staticmethod
    def to_csv(records: List[Dict[str, Any]]) -> str:
        if not records:
            return ""
        output = io.StringIO()
        fieldnames = list(records[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record)
        return output.getvalue()
