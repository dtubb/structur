import os
import re
import shutil
import typer

app = typer.Typer()

def process_file(file_path, output_folder, code_filters, link_to_source, code_dict):
    """
    Process a single file and extract coded text.

    Args:
        file_path (str): Path to the file to process.
        output_folder (str): Path to the output folder.
        code_filters (list): List of code filters (regex patterns).
        link_to_source (bool): Whether to include a link to the source file in the output.
        code_dict (dict): Dictionary to store the extracted codes and their associated text.

    The function supports two code formats:
    1. Multiline code format: [[code]] == text == [[code]]
    2. Single line code format: == text == [[code]] ^id-[identifier]

    The extracted codes and their associated text are stored in the code_dict dictionary.
    """
    print(f"Processing file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        print(f"File content length: {len(content)}")
        
        multiline_codes = re.findall(r'\[\[(.*?)\]\]\s*==\s*(.*?)\s*==\s*\[\[\1\]\]', content, re.DOTALL)
        print(f"Found {len(multiline_codes)} multiline codes")
        
        single_line_codes = re.findall(r'==\s*(.*?)\s*==\s*\[\[(.*?)\]\](?:\s*\^id-[^\s]+)?', content, re.DOTALL)
        print(f"Found {len(single_line_codes)} single line codes")
        
        # Process multiline codes
        for code, text in multiline_codes:
            print(f"Processing multiline code: {code}")
            if not code_filters or any(re.match(pattern, code, re.IGNORECASE) for pattern in code_filters):
                if code not in code_dict:
                    code_dict[code] = []
                code_dict[code].append((text.strip(), file_path))
        
        # Process single line codes
        for text, code in single_line_codes:
            print(f"Processing single line code: {code}")
            if code not in code_dict:
                if not code_filters or any(re.match(pattern, code, re.IGNORECASE) for pattern in code_filters):
                    code_dict[code] = [(text.strip(), file_path)]
            else:
                existing_texts = [t[0] for t in code_dict[code]]
                if text.strip() not in existing_texts:
                    if not code_filters or any(re.match(pattern, code, re.IGNORECASE) for pattern in code_filters):
                        code_dict[code].append((text.strip(), file_path))
    
    print(f"Processed codes: {list(code_dict.keys())}") 

def write_code_files(code_dict, output_folder, link_to_source):
    """
    Write the extracted codes and their associated text to individual files.

    Args:
        code_dict (dict): Dictionary containing the extracted codes and their associated text.
        output_folder (str): Path to the output folder.
        link_to_source (bool): Whether to include a link to the source file in the output.

    The function creates a separate file for each code in the output folder.
    If link_to_source is True, it includes a link to the source file in the output.
    """
    for code, text_list in code_dict.items():
        code_file = os.path.join(output_folder, f"{code}.md")
        os.makedirs(os.path.dirname(code_file), exist_ok=True)
        with open(code_file, 'w', encoding='utf-8') as out_file:
            for text, file_path in text_list:
                if link_to_source:
                    relative_path = os.path.relpath(file_path, output_folder)
                    out_file.write(f"## [{relative_path}]({relative_path})\n\n")
                out_file.write(text + "\n\n")

def process_folder(folder_path, output_folder, code_filters, extensions, link_to_source):
    """
    Process all files in a folder and its subfolders.

    Args:
        folder_path (str): Path to the folder to process.
        output_folder (str): Path to the output folder.
        code_filters (list): List of code filters (regex patterns).
        extensions (list): List of file extensions to process.
        link_to_source (bool): Whether to include a link to the source file in the output.

    Returns:
        int: Count of processed files.

    The function recursively processes all files with the specified extensions in the folder and its subfolders.
    It calls the process_file function for each file and stores the extracted codes and their associated text in a dictionary.
    Finally, it calls the write_code_files function to write the extracted codes to individual files.
    """
    count = 0
    code_dict = {}

    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist.")
        return count

    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory.")
        return count

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            _, ext = os.path.splitext(file)
            
            if ext.lower() in extensions:
                file_path = os.path.join(root, file)
                process_file(file_path, output_folder, code_filters, link_to_source, code_dict)
                count += 1

    write_code_files(code_dict, output_folder, link_to_source)
    return count
    
@app.command()
def main(input_path: str, 
         output_folder: str = None, 
         code_filters: str = None, 
         extensions: str = '', 
         link_to_source: bool = False):
    """
    Main function to process files and extract coded text.

    Args:
        input_path (str): Path to the input file or folder.
        output_folder (str, optional): Path to the output folder. Defaults to None.
        code_filters (str, optional): Comma-separated list of code filters. Defaults to None.
        extensions (str, optional): Comma-separated list of file extensions to process. Defaults to an empty string.
        link_to_source (bool, optional): Whether to include a link to the source file in the output. Defaults to False.

    The function processes the input file or folder and extracts coded text based on the specified code formats.
    It applies code filters (if provided) to filter the extracted codes.
    The extracted codes and their associated text are written to individual files in the output folder.
    """
    # Process code filters
    if code_filters:
        # Split code_filters if it's a string of comma-separated values
        code_filters = code_filters.split(',')
        # Convert wildcards to regex format
        code_filters_regex = [re.escape(f).replace("\\*", ".*") for f in code_filters]
        # Create a string with filters for the folder name
        filter_folder_suffix = '_' + '_'.join(code_filters)
    else:
        # If code_filters is None, use an empty list and no folder suffix
        code_filters_regex = []
        filter_folder_suffix = ''
        code_filters = []  # Ensure code_filters is a list

    # Determine the base output folder name based on the input path and filters
    base_name = os.path.basename(os.path.splitext(input_path)[0])
    default_output_folder = base_name + '_structur' + filter_folder_suffix

    if not output_folder:
        output_folder = default_output_folder
    else:
        # Normalize the provided output folder name
        output_folder = re.sub(r'\W+', '_', output_folder)

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Process extensions
    if not extensions:
        extensions = ['.txt', '.md']
    elif isinstance(extensions, str):
        extensions = [ext.strip().lower() for ext in extensions.split(',') if ext.strip()]
    else:
        extensions = [ext.strip().lower() for ext in extensions]

    # Process the input path
    if os.path.isfile(input_path):
        code_dict = {}
        process_file(input_path, output_folder, code_filters_regex, link_to_source, code_dict)
        write_code_files(code_dict, output_folder, link_to_source)
        processed_count = 1
    else:
        processed_count = process_folder(input_path, output_folder, code_filters_regex, extensions, link_to_source)

    # Output results
    print(f"Structur completed. Output files are in the '{output_folder}' folder.")
    if code_filters:  # Only print extracted codes if there are any
        print("Extracted codes:")
        for filter in code_filters:
            print(f"- {filter}")

    print(f"\nTotal files processed: {processed_count}")    

if __name__ == "__main__":
    app()