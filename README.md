# # Structur 📚✨: Structure Research Notes

- **Flexible Input**: Extract coded text from individual files, folders, and subdirectories.
- **Markdown Output**: Extracted snippets of text are saved as individual markdown files.
- **Custom Code Filters**: Extract only specific codes.
- **Linking to Sources**: Links to the original source files.

**Structur** is a Python-based command-line tool designed to extract coded text from notes. It is inspired by John McPhee's description of structuring his writing in the *Structure* chapter of *Draft No. 4*. McPhee describes how **Structur**, written in the 1980s by Howard J. Strauss at Princeton’s Office of Information Technology, revolutionized his method of writing that used scissors, slivers of paper, manila folders, and three-by-five index cards, along with an Underwood 5 typewriter, until **Structur**:

> Structur exploded my notes. It read the codes by which each note was given a destination or destinations (including the dustbin). It created and named as many new Kedit files as there were codes, and, of course, it preserved intact the original set. In my first I.B.M. computer, Structur took about four minutes to sift and separate fifty thousand words. My first computer cost five thousand dollars. I called it a five-thousand-dollar pair of scissors.

Not knowing much about how McPhee and Strauss' **Structur** worked, this Python **Structur** extracts coded text from files and folders.

## Installation Instructions

### Requirements
- **Python 3.7 or later**: Ensure you have Python installed. You can check your version by running `python --version` or `python3 --version` in your terminal.

### Installation Steps

1. **Clone the Repository**:
   Open your terminal and run the following command to clone the Structur repository:

   ```bash
   git clone https://github.com/dtubb/structur.git
   cd structur
   ```

2. **Create a Conda Environment**:
   It is recommended to create a Conda environment to manage dependencies. You can create one using the following command:

   ```bash
   conda create --name structur python=3.8
   conda activate structur
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

## Usage

To use **Structur**, run the command line interface with the following syntax:

```bash
python structur.py input_folder --output_folder output --code_filters "theme,climate" --extensions ".txt,.md" --link_to_source
```

Or, simply you can use the script to run structur with just the file or directory path.

```bash
python structur.py input_file_or_folder
```

### Arguments
- **input_path** (str): Path to the input file or folder.
  
### Options
- **--output-folder** (str, optional): Path to the output folder. Defaults to None.
- **--code-filters** (str, optional): Comma-separated list of code filters. Defaults to None.
- **--extensions** (str, optional): Comma-separated list of file extensions to process. Defaults to an empty string.
- **--link-to-source** (bool, optional): Whether to include a link to the source file in the output. Defaults to False.
- **--install-completion**: Install completion for the current shell.
- **--show-completion**: Show completion for the current shell, to copy it or customize the installation.
- **--help**: Show this message and exit.

## Format for Text Codes 

### 1. **Multiline Code Format**
   - **Pattern**: `[[code]]==text==[[code]]`
   - **Example**:
     ```
     [[theme]]==The significance of the landscape in literature. This theme explores how various authors depict natural settings to
     reflect their characters' emotional states and thematic concerns.

     However, the actual coded text is multiple lines.==[[theme]]
     ```
   - **Explanation**: This pattern identifies sections where a code is enclosed in double square brackets and followed by `==` to separate it from the corresponding text. This format allows for multiline text.

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