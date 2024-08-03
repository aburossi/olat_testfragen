import json
import random

def clean_json_string(s):
    # Remove any leading/trailing whitespace and special characters
    s = s.strip()
    s = s.lstrip('```json').rstrip('```')
    return s

def convert_json_to_text_format(json_input):
    if isinstance(json_input, str):
        data = json.loads(json_input)
    else:
        data = json_input

    fib_output = []
    ic_output = []

    for item in data:
        page_number = item.get('page_number', 'N/A')
        subject = item.get('subject', 'N/A')
        bloom_level = item.get('bloom_level', 'N/A')
        text = item.get('text', '')
        blanks = item.get('blanks', [])
        wrong_substitutes = item.get('wrong_substitutes', [])

        num_blanks = len(blanks)

        common_header = [
            f"Keywords\tSeite {page_number}",
            "Coverage\tLehrmittel Allgemeinbildung",
            f"Subject\t/Allgemeinbildung/{subject}",
            f"Level\t{bloom_level}"
        ]

        # Fill-in-the-Blanks format
        fib_lines = [
            "Type\tFIB",
            *common_header,
            "Title\t✏✏Vervollständigen Sie die Lücken mit dem korrekten Begriff.✏✏",
            f"Points\t{num_blanks}"
        ]

        for blank in blanks:
            text = text.replace(blank, f"{{blank}}", 1)

        parts = text.split("{blank}")
        for index, part in enumerate(parts):
            fib_lines.append(f"Text\t{part.strip()}")
            if index < len(blanks):
                fib_lines.append(f"1\t{blanks[index]}\t20")

        fib_output.append('\n'.join(fib_lines))

        # Inline Choice format
        ic_lines = [
            "Type\tInlinechoice",
            *common_header,
            "Title\tWörter einordnen",
            "Question\t✏✏Wählen Sie die richtigen Wörter.✏✏",
            f"Points\t{num_blanks}"
        ]

        all_options = blanks + wrong_substitutes
        random.shuffle(all_options)

        for index, part in enumerate(parts):
            ic_lines.append(f"Text\t{part.strip()}")
            if index < len(blanks):
                options_str = '|'.join(all_options)
                ic_lines.append(f"1\t{options_str}\t{blanks[index]}\t|")

        ic_output.append('\n'.join(ic_lines))

    return '\n\n'.join(fib_output), '\n\n'.join(ic_output)

def transform_output(json_string):
    try:
        # Clean the JSON string
        cleaned_json_string = clean_json_string(json_string)
        
        # Parse the cleaned JSON string
        json_data = json.loads(cleaned_json_string)
        
        # Convert to text format
        fib_output, ic_output = convert_json_to_text_format(json_data)
        
        return f"{ic_output}\n---\n{fib_output}"
    except json.JSONDecodeError as e:
        return f"Error parsing JSON: {e}\n\nCleaned input:\n{cleaned_json_string}\n\nOriginal input:\n{json_string}"
    except Exception as e:
        return f"Error processing input: {e}\n\nOriginal input:\n{json_string}"
