import json

def clean_json(input_file, output_file):
    """
    Remove 'raw_text' entries from a JSON file containing QA data.
    
    Args:
        input_file (str): Path to input JSON file
        output_file (str): Path to save cleaned JSON file
    """
    # Read the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Remove raw_text from each entry
    for entry in data:
        if 'raw_text' in entry:
            del entry['raw_text']
    
    # Write the cleaned data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Print stats
    print(f"Processed {len(data)} entries")
    print(f"Cleaned data saved to {output_file}")

# Usage
if __name__ == "__main__":
    input_file = "Train and Val/train.json"  # Change this to your input file name
    output_file = "train_cleaned.json"  # Change this to your desired output file name
    clean_json(input_file, output_file)