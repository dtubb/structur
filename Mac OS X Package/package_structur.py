import PyInstaller.__main__
import os
import sys

print("Starting packaging process...")

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Script directory: {script_dir}")

# Path to your main script
main_script = os.path.join(script_dir, 'structur.py')
print(f"Main script path: {main_script}")

if not os.path.exists(main_script):
    print(f"Error: Main script '{main_script}' not found!")
    sys.exit(1)

# Check if LICENSE file exists
license_file = os.path.join(script_dir, 'LICENSE')
add_data_option = f'--add-data={license_file}:.' if os.path.exists(license_file) else ''

print(f"LICENSE file {'found' if add_data_option else 'not found'}")

# Prepare PyInstaller arguments
pyinstaller_args = [
    main_script,
    '--onefile',
    '--name=structur',
    '--hidden-import=typer',
    '--hidden-import=typing_extensions',
]

# Add the --add-data option only if LICENSE file exists
if add_data_option:
    pyinstaller_args.append(add_data_option)

print("PyInstaller arguments:")
for arg in pyinstaller_args:
    print(f"  {arg}")

print("\nStarting PyInstaller...")

try:
    # Run PyInstaller
    PyInstaller.__main__.run(pyinstaller_args)
    print("\nPackaging completed successfully!")
except Exception as e:
    print(f"\nAn error occurred during packaging: {str(e)}")

print("\nProcess finished. Check the 'dist' folder for the executable.")
