# Structur

**Structur** is a Python-based command-line tool designed to extract and organize coded text from notes. It is inspired by John McPhee's description of structuring his writing in the *Structure* chapter of *Draft No. 4*. McPhee describes how **Structur**, written in the 1980s by Howard J. Strauss at Princeton’s Office of Information Technology, revolutionized his method of writing that used scissors, slivers of paper, manila folders, and three-by-five index cards, along with an Underwood 5 typewriter. McPhee wrote:

> Structur exploded my notes. It read the codes by which each note was given a destination or destinations (including the dustbin). It created and named as many new Kedit files as there were codes, and, of course, it preserved intact the original set. In my first I.B.M. computer, Structur took about four minutes to sift and separate fifty thousand words. My first computer cost five thousand dollars. I called it a five-thousand-dollar pair of scissors.

Not knowing much about how McPhee's **Structur** actually worked, this Python **Structur** works with coded text from individual files or entire folders of files.

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

## How It Works

- **Flexible Input**: Process individual files or entire folders, recursively scanning subdirectories for text files.
- **Markdown Output**: Extracted codes and their associated text are saved as individual markdown files for easy access and organization.
- **Custom Code Filters**: OptionallysSpecify specific codes to extract.
- **Linking to Sources**: Optionally include links to the original source files in the output.

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
