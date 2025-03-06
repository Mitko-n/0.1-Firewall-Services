import json
import csv

# Utility to print data in various formats
def print_data(data, format="plain", numbering=False):
    def format_item(item, index=None):
        prefix = f"{index:03}: " if numbering and index is not None else ""
        if format == "json":
            formatted = json.dumps(item, indent=4).replace("\n", "\n" + " " * len(prefix))
            return f"{prefix}{formatted}"
        return f"{prefix}{item}"

    if isinstance(data, list):
        for i, item in enumerate(data, start=1):
            print(format_item(item, i))
    else:
        print(format_item(data))

# Utility to read data from a CSV file and return it as a list of dictionaries
def read_csv_to_list_of_dict(csv_file_path):
    try:
        with open(csv_file_path, mode="r", encoding="UTF8", newline="") as file:
            return list(csv.DictReader(file, skipinitialspace=True))
    except Exception as e:
        return {"status": "error", "message": f"Failed to read data from CSV: {str(e)}", "data": None}

# Utility to write a list of dictionaries to a CSV file
def write_list_of_dict_to_csv(list_of_dict, csv_file_path):
    try:
        if not list_of_dict:
            raise ValueError("list_of_dict cannot be empty or None.")

        fieldnames = list({key for dictionary in list_of_dict for key in dictionary.keys()})

        with open(csv_file_path, mode="w", encoding="UTF8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, restval="...")
            writer.writeheader()
            writer.writerows(list_of_dict)
    except Exception as e:
        return {"status": "error", "message": f"Failed to write data to CSV: {str(e)}", "data": None}
