import sys
import json

# Initialize an empty list to hold the parsed records
records = []

# Read from stdin line by line
first_line = True
for line in sys.stdin:
    # Skip the header line
    if first_line:
        first_line = False
        continue
    # Split the line into components based on multiple spaces
    parts = line.split(maxsplit=3)
    # Append a dictionary for each record to the records list
    records.append({
        "title": parts[0],
        "type": parts[1] if len(parts) > 3 else "",
        "tag_name": parts[2] if len(parts) > 3 else parts[1],
        "published": parts[3].strip() if len(parts) > 3 else parts[2].strip()
    })

# Convert the list of records to JSON
json_output = json.dumps(records, indent=4)

# Print the JSON output
print(json_output)
