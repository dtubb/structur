# Examples

This folder contains example files to help you understand how to use structur.

## Files

### `example.md`
A sample markdown file with coded content that demonstrates the various code formats that structur can process:

- `{{workflow}}==content=={{workflow}}` - Curly brace format
- `[[productivity]]==content==[[productivity]]` - Square bracket format
- Mixed content with both coded and uncoded text

Use this file to test structur processing:
```bash
python structur.py single examples/example.md output_folder
```

### `codes.txt`
A sample codes.txt file that demonstrates the format for managing your master codes list:

- Lines starting with `#` are comments and will be ignored
- Empty lines are also ignored
- Each code should be on its own line
- Codes are used to organize extracted content into separate files

Use this file with the `--codes-file` option:
```bash
python structur.py process input_folder output_folder --codes-file examples/codes.txt
```

## Usage Examples

### Basic Processing
```bash
# Process a single example file
python structur.py single examples/example.md my_output

# Process a folder with the example codes file
python structur.py process input_folder output_folder --codes-file examples/codes.txt

# Auto-create codes.txt from extracted codes
python structur.py process input_folder output_folder --auto-codes-file

# Regenerate empty files for all codes
python structur.py process input_folder output_folder --regenerate-codes
```

### Shell Script Usage
```bash
# Process using the shell script
./structur.sh examples/example.md my_output
``` 