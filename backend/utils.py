import re
import json
import os

def read_maritime_data(file_path):
    """Read maritime data from a markdown file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    with open(file_path, 'r') as file:
        return file.read()

def parse_maritime_data(data):
    # Initialize the structured data dictionary
    parsed_data = {
        "maritime_reports": [],
        "reconnaissance_notes": [],
        "communication_messages": [],
        "geographical_data": [{
            "maritime_zones": [],
            "shipping_lanes": []
        }]
    }

    # Split the data into sections based on known headings
    sections = data.split("###")
    for section in sections:
        section = section.strip()
        if section.startswith("1.1"):
            # Maritime Reports
            reports = re.findall(r"Date: (.+?)\nTime: (.+?)\nLocation: (.+?)\nReport: (.+?)(?=\n\n|\Z)", section, re.DOTALL)
            for report in reports:
                parsed_data["maritime_reports"].append({
                    "date": report[0].strip(),
                    "time": report[1].strip(),
                    "location": report[2].strip(),
                    "report": report[3].strip()
                })
        
        elif section.startswith("1.2"):
            # Reconnaissance Notes
            notes = re.findall(r"(.+) - (.+)\n(.+): (.+?)(?=\n\n|\Z)", section, re.DOTALL)
            for note in notes:
                parsed_data["reconnaissance_notes"].append({
                    "date": note[0].strip(),
                    "time": note[1].strip(),
                    "note": note[3].strip()
                })

        elif section.startswith("1.3"):
            # Communication Messages
            messages = re.findall(r"FROM: (.+?)\nTO: (.+?)\nPRIORITY: (.+?)\nDTG: (.+?)\n(.*?)(?=\n\n|\Z)", section, re.DOTALL)
            for message in messages:
                details = re.findall(r"\d+\.\s*(.+)", message[4])
                parsed_data["communication_messages"].append({
                    "from": message[0].strip(),
                    "to": message[1].strip(),
                    "priority": message[2].strip(),
                    "dtg": message[3].strip(),
                    "details": [detail.strip() for detail in details]
                })

        elif section.startswith("1.4"):
            # Geographical Data
            geo_data_match = re.search(r"(\{.*?\})", section, re.DOTALL)  # Adjusted regex to match JSON object
            if geo_data_match:
                geo_data_json = geo_data_match.group(1)
                try:
                    geo_data = json.loads(geo_data_json)
                    parsed_data["geographical_data"]["maritime_zones"] = geo_data["maritime_zones"]
                    parsed_data["geographical_data"]["shipping_lanes"] = geo_data["shipping_lanes"]
                except json.JSONDecodeError as e:
                    print(f"JSON decoding error: {e}")
                    print("Geo Data JSON:", geo_data_json)  # Debugging line

    return parsed_data

# Main execution
if __name__ == "__main__":
    file_path = '/home/agnij/Desktop/maritime-situational-awareness/data/Maritime Situational Awareness/maritime-dataset-v1.md'
    data = read_maritime_data(file_path)
    parsed_data = parse_maritime_data(data)

    # Print the parsed data for verification
    print(json.dumps(parsed_data, indent=4))