import json
from pathlib import Path
from typing import Dict, List, Union, Set
import sys
from copy import deepcopy
import re

class JSONValidationError(Exception):
    """Custom exception for JSON validation errors."""
    pass

def normalize_entry(entry: Dict) -> Dict:
    """Normalizes an entry for comparison by sorting arrays and standardizing format."""
    entry = deepcopy(entry)
    # Sort arrays in spans
    for category in entry['spans']:
        if isinstance(entry['spans'][category], list):
            entry['spans'][category] = sorted(entry['spans'][category])
    return entry

def entries_are_equal(entry1: Dict, entry2: Dict) -> bool:
    """Compares two entries after normalization."""
    return normalize_entry(entry1) == normalize_entry(entry2)

def validate_and_fix_entry(entry: Dict, file_name: str, entry_index: int) -> Dict:
    """Validates and fixes a single JSON entry."""
    
    # Create a fixed entry
    fixed_entry = {}
    
    # Fix URI - convert to integer
    if 'uri' not in entry:
        raise JSONValidationError(f"Missing required field 'uri' in file {file_name}, entry {entry_index}")
    try:
        fixed_entry['uri'] = int(str(entry['uri']).strip('"'))
    except ValueError:
        raise JSONValidationError(f"Invalid URI format: {entry['uri']} in file {file_name}, entry {entry_index}")
    
    # Validate spans
    if 'spans' not in entry:
        raise JSONValidationError(f"Missing required field 'spans' in file {file_name}, entry {entry_index}")
        
    required_categories = ['EXPERIENCE', 'INFORMATION', 'CAUSE', 'SUGGESTION', 'QUESTION']
    fixed_entry['spans'] = {}
    
    for category in required_categories:
        if category not in entry['spans']:
            fixed_entry['spans'][category] = []
        else:
            spans = entry['spans'][category]
            if not isinstance(spans, list):
                raise JSONValidationError(
                    f"Spans category {category} must be an array in file {file_name}, entry {entry_index}"
                )
            fixed_entry['spans'][category] = [str(span) for span in spans]
            
    # Validate summaries
    if 'summaries' not in entry:
        raise JSONValidationError(f"Missing required field 'summaries' in file {file_name}, entry {entry_index}")
        
    fixed_entry['summaries'] = {}
    for category in required_categories:
        if category not in entry['summaries']:
            fixed_entry['summaries'][category] = ""
        else:
            summary = entry['summaries'][category]
            if not isinstance(summary, str):
                raise JSONValidationError(
                    f"Summary category {category} must be a string in file {file_name}, entry {entry_index}"
                )
            fixed_entry['summaries'][category] = str(summary)
            
    return fixed_entry

def extract_file_number(filename: str) -> int:
    """Extracts the number from a filename like 'output_1.json'."""
    match = re.search(r'output_(\d+)\.json', filename)
    if match:
        return int(match.group(1))
    return 0

def merge_json_files(directory_path: str, output_file: str = "merged_output.json") -> None:
    """
    Merges all JSON files from a directory, validates their content, and outputs a single merged file.
    Processes files sequentially, maintaining order within each file.
    """
    directory = Path(directory_path)
    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory_path}")
    
    # Find and sort JSON files by number
    json_files = list(directory.glob("output_*.json"))
    json_files.sort(key=lambda x: extract_file_number(x.name))
    
    if not json_files:
        raise FileNotFoundError(f"No JSON files found in {directory_path}")
    
    # Track all entries and URIs
    merged_entries = []
    seen_uris = set()
    errors = []
    
    # Process each file sequentially
    for json_file in json_files:
        print(f"Processing {json_file.name}...")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON in file {json_file.name}: {str(e)}")
                continue
            
            if not isinstance(data, list):
                errors.append(f"File {json_file.name} must contain a JSON array")
                continue
            
            # Process all entries in this file
            for i, entry in enumerate(data, 1):
                try:
                    fixed_entry = validate_and_fix_entry(entry, json_file.name, i)
                    uri = fixed_entry['uri']
                    
                    # Skip if we've seen this URI before
                    if uri in seen_uris:
                        errors.append(f"Skipping duplicate URI {uri} in {json_file.name}, entry {i}")
                        continue
                    
                    seen_uris.add(uri)
                    merged_entries.append(fixed_entry)
                    
                except JSONValidationError as e:
                    errors.append(str(e))
    
    # Write the merged and fixed output
    output_path = directory / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_entries, f, indent=2, ensure_ascii=False)
    
    # Report results
    print("\nProcessing complete!")
    print(f"Total unique entries processed: {len(merged_entries)}")
    print(f"Output written to: {output_path}")
    
    if errors:
        print("\nWarnings/Errors encountered:")
        for error in errors:
            print(f"- {error}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)
    
    try:
        merge_json_files(sys.argv[1])
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    merge_json_files("claude_answers/spans")