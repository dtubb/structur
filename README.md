## Structur: Structure Research Notes

- **Flexible Input**: Extract coded text from individual files, folders, and subdirectories.
- **Markdown Output**: Extracted snippets of text are saved as individual markdown files.
- **Custom Code Filters**: Extract only specific codes.
- **Linking to Sources**: Links to the original source files.

**Structur** is a Python-based command-line tool designed to extract coded text from notes. It is inspired by John McPhee's description of structuring his writing in the *Structure* chapter of *Draft No. 4*. McPhee describes how **Structur**, written in the 1980s by Howard J. Strauss at Princeton’s Office of Information Technology, revolutionized his method of writing that used scissors, slivers of paper, manila folders, and three-by-five index cards, along with an Underwood 5 typewriter, until **Structur**:

> Structur exploded my notes. It read the codes by which each note was given a destination or destinations (including the dustbin). It created and named as many new Kedit files as there were codes, and, of course, it preserved intact the original set. In my first I.B.M. computer, Structur took about four minutes to sift and separate fifty thousand words. My first computer cost five thousand dollars. I called it a five-thousand-dollar pair of scissors.

Not knowing much about how McPhee and Strauss' **Structur** worked, this Python **Structur** extracts coded text from files and folders.

## Version Information

**Current Version**: 0.0.1.dev2

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and changes.

## Installation Instructions

### Requirements
- **Python 3.8 or later**: Ensure you have Python installed. You can check your version by running `python --version` or `python3 --version` in your terminal.

### Testing
The project includes comprehensive unit tests. To run the tests:

```bash
# Run all tests
./test.sh

# Or run tests directly
python tests/run_tests.py

# Or use unittest
python -m unittest tests.test_structur -v
```

### Installation Steps

1. **Clone the Repository**:
   Open your terminal and run the following command to clone the Structur repository:

   ```bash
   git clone https://github.com/dtubb/structur.git
   cd structur
   ```

2. **Create a Virtual Environment**:
   It is recommended to create a virtual environment to manage dependencies. You can create one using the following command:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

3. **Install Required Packages**:
   Install the required packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Tool**:
   You can now run Structur using the command line. Use the following command to get a list of available options:

   ```bash
   python structur.py --help
   ```

   To check the current version:

   ```bash
   python structur.py version
   ```

## Usage

### Command Line Interface

To use **Structur**, run the command line interface with the following syntax:

```bash
python structur.py input_folder --output_folder output --code_filters "theme,climate" --extensions ".txt,.md" --link_to_source
```

Or, simply you can use the script to run structur with just the file or directory path.

```bash
python structur.py input_file_or_folder
```

### Programmatic Usage

You can also use **Structur** as a Python function in your own scripts:

```python
import structur

# Basic usage
result = structur.process_structur("input_file.md")

# With custom settings
result = structur.process_structur(
    input_path="input_folder/",
    output_folder="custom_output",
    code_filters="workflow,productivity",
    link_to_source=True,
    verbose=False
)

# Access the results
print(f"Output folder: {result['output_folder']}")
print(f"Files processed: {result['processed_count']}")
print(f"Operations: {result['operations']}")
print(f"Extracted codes: {result['extracted_codes']}")
print(f"Word counts: {result['word_counts']}")
```

The `process_structur()` function returns a dictionary with:
- `output_folder`: Path to the output folder
- `processed_count`: Number of files processed
- `operations`: Dictionary with operation counts (created_new, appended, duplicates_skipped)
- `extracted_codes`: List of extracted code names
- `word_counts`: Dictionary with word count statistics (original, coded, uncoded, duplicates)

See `example_usage.py` for more examples.

### Arguments
- **input_path** (str): Path to the input file or folder.
  
### Options
- **--output-folder** (str, optional): Path to the output folder. Defaults to None.
- **--code-filters** (str, optional): Comma-separated list of code filters. Defaults to None.
- **--extensions** (str, optional): Comma-separated list of file extensions to process. Defaults to an empty string.
- **--link-to-source** (bool, optional): Whether to include a link to the source file in the output. Defaults to False.
- **--code-format** (str, optional): The format for codes (e.g., "{{ }}" or "[[ ]]"). Defaults to "{{ }}".
- **--codes-file** (str, optional): Path to codes.txt file to read master codes list. Defaults to None.
- **--regenerate-codes** (bool, optional): Whether to regenerate empty files for all codes in codes.txt. Defaults to False.
- **--auto-codes-file** (bool, optional): Whether to automatically create/update codes.txt with extracted codes. Defaults to False.
- **--uncoded-folder** (str, optional): Path to folder for uncoded text. If specified, extracts all text without codes to separate files. Defaults to None.
- **--duplicate-folder** (str, optional): Path to folder for duplicate text. If specified, saves duplicate text instances to separate files. Defaults to None.
- **--install-completion**: Install completion for the current shell.
- **--show-completion**: Show completion for the current shell, to copy it or customize the installation.
- **--help**: Show this message and exit.

## Format for Text Codes 

Structur supports two code formats: `{{code}}` and `[[code]]` (double curly braces or double square brackets).

### **Unified Code Format**
   - **Pattern**: `{{code}}==text=={{code}}` or `[[code]]==text==[[code]]`
   - **Example**:
     ```
     {{theme}}==The significance of the landscape in literature. This theme explores how various authors depict natural settings to
     reflect their characters' emotional states and thematic concerns.

     However, the actual coded text is multiple lines.=={{theme}}
     ```
   - **Single Line Example**:
     ```
     {{character}}==The importance of character development in storytelling=={{character}} ^id-12345
     ```
   - **Explanation**: This unified pattern identifies sections where a code is enclosed in double brackets/braces, followed by `==` to separate it from the corresponding text, and ending with the same code. The text can be single line or multiline. An optional identifier `^id-[identifier]` can be added at the end, as used by the Obsidian plugin [Quadro](https://github.com/chrisgrieser/obsidian-quadro), which allows for coding text in [Obsidian](https://obsidian.md).

<<<<<<< HEAD
### 2. **Single Line Code Format**
   - **Pattern**: `[[code]]==text==[[code]] ^id-[identifier]`
   - **Example**:
     ```
     [[character]]==The importance of character development in storytelling==[[character]] ^id-12345
     ```
   - **Explanation**: This pattern captures sections where the text is prefixed by `==` and suffixed by a code enclosed in double square brackets. Additionally, it can include an optional identifier denoted by `^id-[identifier]` at the end, as used by the Obsidian plugin [Quadro](https://github.com/chrisgrieser/obsidian-quadro), which allows for coding text in [Obsidian](https://obsidian.md).

## Using Structur on Mac OS X

## Packaging

To create a standalone executable of **Structur**, use the `package_structur.py` script. This bundles the (`structur.py`) and necessary dependencies into a single executable file, making it easy to run from the Terminal, without requiring Python or additional libraries.

Add export PATH="/path/to/packeged/script:$PATH" to `~/.zshrc`

## Automator

Now, you can use an Automator workflow on Mac OS X to run **Structur** on a selected file or directories directly from the Finder's Quick Actions menu.

 Save the workflow in the ~/Library/Services folder.

 ## Citation

 Please [cite](./citation.cff) as: 
> Tubb, Daniel. *Structur.py*. GitHub, 2024. https://github.com/dtubb/structur.
=======
## Iterative Workflow with Codes.txt

Structur supports an iterative workflow where you can continuously add new material to existing coded files. This is perfect for research and writing projects where you want to build up your coded content over time.

### Master Codes List

Create a `codes.txt` file to define your master list of codes:

```
# Master codes list for structur.py
# Lines starting with # are comments and will be ignored
# Empty lines are also ignored

workflow
productivity
writing
ideas
research
notes
projects
tasks
inspiration
reflection
```

### Workflow Examples

**1. Set up your coded folder with empty files:**
```bash
python structur.py . --output-folder my_coded_notes --regenerate-codes
```

**2. Process new material into existing coded folder:**
```bash
python structur.py input_file.md --auto-codes-file
```

**3. Extract uncoded text to separate folder:**
```bash
python structur.py input_file.md --uncoded-folder uncoded_text
```

This will create a separate folder containing all text that doesn't have any codes, preserving the original filenames.

**4. Extract duplicate text to separate folder:**
```bash
python structur.py input_file.md --duplicate-folder duplicate_text
```

This will create a separate folder containing all duplicate text instances, helping you identify and analyze duplicate content.
```bash
python structur.py to-code/ --output-folder my_coded_notes
```

**3. Add more material later (appends to existing files):**
```bash
python structur.py more-input/ --output-folder my_coded_notes
```

**4. Automatically manage codes.txt (new feature):**
```bash
python structur.py input_file.md --auto-codes-file
```

This will automatically create or update a `codes.txt` file in the same directory as your input file, adding any new codes that were extracted.

### Key Features

- **No Duplication**: Automatically skips duplicate content
- **Iterative Processing**: Can run multiple times on same output folder
- **Master Control**: codes.txt acts as the source of truth
- **Clear Logging**: See exactly what happened during processing
- **Manual Control**: You decide when to archive/delete source files
- **Auto Codes Management**: Automatically create and update codes.txt files with new codes

### Recommended Folder Structure

```
inbox/           # Raw notebooks and sources
to-code/         # Raw uncoded text files ready for processing  
coded/           # Text organized by code (structur.py output)
codes.txt        # Master list of codes
synthesis/       # Developed ideas from coded content
```

### Example File

See `example.md` in this repository for a complete example showing all the supported code formats.

### Operation Logging

Structur provides detailed logging of all operations:

- **Created**: New files created with content
- **Appended**: Content added to existing files
- **Duplicates Skipped**: Content that was already present
- **Regenerated**: Empty files created from codes.txt

Example output:
```
Read 10 codes from codes.txt
Created empty file: workflow.md
Created empty file: productivity.md
...
Regenerated files: 10 created, 0 already existed
Processing file: example_input.md
...
Appended 2 entries to existing file: workflow.md
Appended 1 entries to existing file: productivity.md
...
Structur completed. Output files are in the 'my_coded_notes' folder.
Total files processed: 1
Operations: 0 new files created, 3 files appended to, 0 duplicates skipped

Word Count Summary:
Original text: 15,234 words
Coded text: 8,456 words
Uncoded text: 5,123 words
Duplicate text: 1,234 words
Total accounted: 14,813 words
Difference: 421 words
Note: 421 words missing - this may be due to:
  - Headers, footers, and structural text
  - Whitespace and formatting differences
  - Code markers and syntax
```

### Logging System

**Structur** uses a built-in logging system that provides better control over output:

- **Verbose Mode (`verbose=True`)**: Shows detailed progress messages, file processing info, and operation summaries
- **Silent Mode (`verbose=False`)**: Suppresses most output, only showing error messages
- **Log Levels**: The system uses standard Python logging levels (DEBUG, INFO, WARNING, ERROR)
- **Consistent Output**: Works the same whether called from CLI or programmatically

The logging system automatically handles output formatting and ensures consistent behavior across different usage patterns.
>>>>>>> fe22ae5 (Enhance README.md with version information, installation instructions, and usage examples. Update requirements.txt to use typer==0.16.0. Refactor structur.py for improved logging and modular processing. Modify workflow scripts for better environment handling and input processing.)
