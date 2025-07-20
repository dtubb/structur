#!/bin/zsh
set -euo pipefail

# Load your shell rc (for PATH)
source ~/.zshrc

# Grab Automator inputs
input_paths=("$@")

# Add Homebrew tools if needed
export PATH="/opt/homebrew/bin:$PATH"

# Change into your structur project folder
cd "$HOME/code/structur" || { echo "Missing $HOME/code/structur" >&2; exit 1; }

# Activate virtual environment
source .venv/bin/activate || { echo "Failed to activate virtual environment" >&2; exit 1; }

# Process each input, appending _structur for the output folder
for input in "${input_paths[@]}"; do
  output_folder="${input}_structur"
  python structur.py main "$input" --output-folder "$output_folder" --auto-codes-file
done

# Deactivate environment
deactivate
