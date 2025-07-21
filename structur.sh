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

# Process each input
for input in "${input_paths[@]}"; do
  # Get the directory of the input
  input_dir=$(dirname "$input")
  codes_file="${input_dir}/codes.txt"
  
  # Check if there's already a coded folder in the same directory as the input
  existing_coded_folder="${input_dir}/coded"
  if [[ -d "$existing_coded_folder" ]]; then
    echo "Found existing coded folder: $existing_coded_folder"
    output_folder="$input_dir"
  else
    echo "No existing coded folder found, creating new output folder"
    output_folder="${input}_structur"
  fi
  
  # Check if codes.txt exists in the same directory as input
  if [[ -f "$codes_file" ]]; then
    echo "Using existing codes.txt: $codes_file"
    python structur.py main "$input" --output-folder "$output_folder" --codes-file "$codes_file" --auto-codes-file
  else
    echo "No codes.txt found in $(dirname "$input"), using auto-codes-file only"
    python structur.py main "$input" --output-folder "$output_folder" --auto-codes-file
  fi
done

# Deactivate environment
deactivate
