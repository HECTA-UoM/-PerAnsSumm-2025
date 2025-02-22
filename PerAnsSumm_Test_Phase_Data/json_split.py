import json
from pathlib import Path
from typing import Union, Tuple, Set, Dict, Any

def load_json_file(file_path: Path) -> Union[list, dict]:
    """Helper function to load a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_items_set(data: Union[list, dict]) -> Set[str]:
    """
    Convert JSON data to a set of string representations for comparison.
    Handles both lists and dictionaries.
    """
    if isinstance(data, list):
        # For lists, convert each item to a sorted JSON string
        return {json.dumps(item, sort_keys=True) for item in data}
    elif isinstance(data, dict):
        # For dicts, convert each key-value pair to a sorted JSON string
        return {json.dumps([k, v], sort_keys=True) for k, v in data.items()}
    else:
        raise ValueError("Data must be either a list or dictionary")

def split_and_validate_json(file_path_str: str, n_splits: int) -> Tuple[Path, dict]:
    """
    Splits a JSON file into n parts and validates the split.
    
    Args:
        file_path_str (str): Path to the input JSON file
        n_splits (int): Number of parts to split the file into
        
    Returns:
        Tuple[Path, dict]: Output directory path and validation results
    """
    # Convert input path to Path object
    input_path = Path(file_path_str)
    
    # Validate input file exists
    if not input_path.exists():
        raise FileNotFoundError(f"Input file {file_path_str} not found")
    
    # Validate n_splits
    if not isinstance(n_splits, int):
        raise ValueError("n_splits must be an integer")
    if n_splits <= 0:
        raise ValueError("n_splits must be positive")
    
    # Create output directory
    output_dir = input_path.parent / f"{input_path.stem}_split"
    output_dir.mkdir(exist_ok=True)
    
    # Read and parse original JSON file
    original_data = load_json_file(input_path)
    
    # Handle both arrays and objects
    if isinstance(original_data, list):
        items = original_data
    elif isinstance(original_data, dict):
        items = list(original_data.items())
    else:
        raise ValueError("JSON root must be an array or object")
    
    # Validate n_splits against data size
    total_items = len(items)
    if n_splits > total_items:
        raise ValueError(f"Cannot split {total_items} items into {n_splits} parts")
    
    # Calculate chunk size and generate split points
    chunk_size = total_items // n_splits
    split_points = []
    for i in range(n_splits):
        start = i * chunk_size
        # For the last chunk, take all remaining items
        end = total_items if i == n_splits - 1 else (i + 1) * chunk_size
        split_points.append((start, end))
    
    # Create split files
    for i, (start, end) in enumerate(split_points, 1):
        chunk = items[start:end]
        
        # Convert back to dict if original was dict
        if isinstance(original_data, dict):
            chunk = dict(chunk)
            
        output_path = output_dir / f"{input_path.stem}_part{i}.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunk, f, indent=2, ensure_ascii=False)
    
    # Validation phase
    original_items = get_items_set(original_data)
    
    # Load and combine all split files
    split_items = set()
    split_files = list(output_dir.glob(f"{input_path.stem}_part*.json"))
    
    for split_file in split_files:
        split_data = load_json_file(split_file)
        split_items.update(get_items_set(split_data))
    
    # Compute validation results
    missing_items = original_items - split_items
    extra_items = split_items - original_items
    
    validation_results = {
        "total_items_original": len(original_items),
        "total_items_split": len(split_items),
        "missing_items_count": len(missing_items),
        "extra_items_count": len(extra_items),
        "is_valid": len(missing_items) == 0 and len(extra_items) == 0,
        "split_files_created": len(split_files)
    }
    
    if not validation_results["is_valid"]:
        raise ValueError(
            f"Validation failed!\n"
            f"Missing items: {len(missing_items)}\n"
            f"Extra items: {len(extra_items)}"
        )
    
    return output_dir, validation_results

# Example usage:
try:
    output_dir, validation = split_and_validate_json("test_no_label.json", 10)
    print(f"Successfully split and validated JSON file.")
    print(f"Output files are in: {output_dir}")
    print("\nValidation results:")
    for key, value in validation.items():
        print(f"{key}: {value}")
except Exception as e:
    print(f"Error: {e}")