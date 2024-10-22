import re
import json

def parse_maritime_reports(md_file_path):
    reports = []
    with open(md_file_path, 'r') as file:
        data = file.read()

    # Use regex to find JSON blocks in the markdown file
    json_blocks = re.findall(r'```json(.*?)```', data, re.DOTALL)

    for block in json_blocks:
        try:
            report = json.loads(block.strip())
            reports.append(report)
        except json.JSONDecodeError:
            continue

    return reports
