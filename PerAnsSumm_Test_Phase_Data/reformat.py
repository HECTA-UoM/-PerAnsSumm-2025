import json
import os
from pathlib import Path

def format_qa_pairs(input_file, output_file):
    """
    Formats multiple medical Q&A pairs and writes them to a file.
    
    Args:
        input_file (str): Path to input JSON file
        output_file (str): Path to output file
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Validate input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found")
        return False

    output_path = Path(output_file)
    
    # Create backup if file exists
    if output_path.exists():
        backup_path = output_path.with_suffix('.json.bak')
        try:
            output_path.rename(backup_path)
            print(f"Created backup at {backup_path}")
        except Exception as e:
            print(f"Warning: Could not create backup: {str(e)}")
    
    try:
        # Read input file with UTF-8 encoding
        with open(input_file, 'r', encoding='utf-8') as f:
            qa_json_list = json.load(f)
            
        if not isinstance(qa_json_list, list):
            qa_json_list = [qa_json_list]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write opening tag
            f.write("<examples>\n\n")
            
            total = len(qa_json_list)
            successful = 0
            
            # Process each QA pair
            for i, qa_json in enumerate(qa_json_list, 1):
                try:
                    # Extract input components
                    input_format = {
                        "uri": qa_json["uri"],
                        "question": qa_json["question"].replace('"', '\\"'),
                        "context": qa_json["context"].replace('"', '\\"'),
                        "answers": qa_json["answers"]
                    }
                    
                    # Initialize spans
                    spans = {
                        "EXPERIENCE": [],
                        "INFORMATION": [],
                        "CAUSE": [],
                        "SUGGESTION": [],
                        "QUESTION": []
                    }
                    
                    # Extract spans
                    for category in qa_json.get("labelled_answer_spans", {}):
                        spans[category] = [item["txt"] for item in qa_json["labelled_answer_spans"][category]]
                    
                    # Extract summaries
                    summaries = {
                        "EXPERIENCE": qa_json.get("labelled_summaries", {}).get("EXPERIENCE_SUMMARY", ""),
                        "INFORMATION": qa_json.get("labelled_summaries", {}).get("INFORMATION_SUMMARY", ""),
                        "CAUSE": qa_json.get("labelled_summaries", {}).get("CAUSE_SUMMARY", ""),
                        "SUGGESTION": qa_json.get("labelled_summaries", {}).get("SUGGESTION_SUMMARY", ""),
                        "QUESTION": qa_json.get("labelled_summaries", {}).get("QUESTION_SUMMARY", "")
                    }
                    
                    # Create output format
                    output_format = {
                        "uri": int(qa_json["uri"]),
                        "spans": spans,
                        "summaries": summaries
                    }
                    
                    # Write example with proper formatting
                    example = f"""<example>
<input>
    "uri": {input_format['uri']},
    "question": "{input_format['question']}",
    "context": "{input_format['context']}",
    "answers": {json.dumps(input_format['answers'], indent=6)}
</input>

<output>
{json.dumps(output_format, indent=4)}
</output>
</example>

"""
                    f.write(example)
                    successful += 1
                    
                    # Progress update
                    print(f"Processed {i}/{total} examples ({successful} successful)")
                    
                except Exception as e:
                    print(f"Error processing QA pair {qa_json.get('uri', 'unknown')}: {str(e)}")
                    continue
            
            # Write closing tag
            f.write("</examples>")
            
            print(f"\nComplete! Processed {successful}/{total} examples successfully")
            return True
            
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return False

# Usage example - now takes input file path
input_file = 'Train and Val/train_cleaned.json'  # Update this to your input file path
output_file = 'reformatted_answers.json'
success = format_qa_pairs(input_file, output_file)
if success:
    print("File written successfully!")