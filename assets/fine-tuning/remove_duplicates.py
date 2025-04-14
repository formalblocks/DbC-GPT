#!/usr/bin/env python3
import sys
import json

def remove_duplicate_lines(input_file, output_file):
    seen = set()
    count_total = 0
    count_unique = 0

    with open(input_file, 'r', encoding='utf-8') as fin, \
         open(output_file, 'w', encoding='utf-8') as fout:
        for line in fin:
            count_total += 1
            # Remove any trailing whitespace
            normalized_line = line.strip()
            if normalized_line not in seen:
                seen.add(normalized_line)
                fout.write(normalized_line + "\n")
                count_unique += 1

    print(f"Processed {count_total} lines.")
    print(f"Found {count_unique} unique lines.")

def remove_duplicate_json_entries(input_file, output_file):
    """
    Alternative approach:
    This function demonstrates how to remove duplicates by loading the JSON
    objects and using a canonical representation. This is useful if you want to
    ignore differences in spacing or key order.
    """
    seen = set()
    count_total = 0
    count_unique = 0

    with open(input_file, 'r', encoding='utf-8') as fin, \
         open(output_file, 'w', encoding='utf-8') as fout:
        for line in fin:
            count_total += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON: {line.strip()}")
                continue

            # Create a canonical string representation (sorted keys)
            canonical = json.dumps(obj, sort_keys=True)
            if canonical not in seen:
                seen.add(canonical)
                fout.write(canonical + "\n")
                count_unique += 1

    print(f"Processed {count_total} JSON lines.")
    print(f"Found {count_unique} unique JSON entries.")

def usage():
    print("Usage:")
    print("    python remove_duplicates.py <input_file.jsonl> <output_file.jsonl>")
    print("Options:")
    print("    --canonical    Use canonical JSON comparison to ignore key order and formatting differences.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Check for optional flag "--canonical"
    if len(sys.argv) > 3 and sys.argv[3] == '--canonical':
        remove_duplicate_json_entries(input_file, output_file)
    else:
        remove_duplicate_lines(input_file, output_file)
