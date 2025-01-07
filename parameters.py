import os

# 
# Initialize some automated variables
#
# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Get Windows user profile path
import subprocess
windows_user = subprocess.check_output(['cmd.exe', '/c', 'echo %USERNAME%'], text=True).strip()

# 
# User parameters
#
# Location of input and output files
MARKDOWN_FOLDER="/home/jelle/.config/fabric/patterns"
YAML_OUTPUT_FOLDER=f"/mnt/c/Users/{windows_user}/AppData/Roaming/espanso/match"
OBSIDIAN_OUTPUT_FOLDER=f"/mnt/c/Obsidian/BrainCave/Extra/textgenerator/templates/fabric"

# Headings to extract from markdown files
BASE_WORDS = ['Identity', 'Purpose', 'Task', 'Goal']

# Model parameters
USE_FASTEMBED = True
EMBED_MODEL = "fast-bge-small-en" 
COLLECTION_NAME = "markdown_files"

#
# Checks
#
# Ensure required directories exist
def check_path(path):
    if not os.path.exists(path):
        raise Exception(f"Path {path} does not exist")

for path in [MARKDOWN_FOLDER, YAML_OUTPUT_FOLDER]:
    check_path(path)        