"""Checks on input data are done in config.py
These parameters must be loaded in the script using config.py"""
import os

# 
# Initialize some automated variables
# only needed for updating the database and writing the YAML espanso file
# and the markdown Obsidian files
# So not necessary for running the streamlit app with query only
# These automated variables don't work in the cloud obviously
# because the cloud doesn't have a local filesystem
# Therefore we first check if we are running in a local WSL environment
# 
# Project root directory
is_wsl = os.environ.get('WSL_DISTRO_NAME') is not None

if is_wsl:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

    # Get Windows user profile path
    import subprocess
    windows_user = subprocess.check_output(['cmd.exe', '/c', 'echo %USERNAME%'], text=True).strip()
    # 
    # User parameters
    #
    # Location of input and output files
    # TODO: make us of ~ possible in setting of path
    FABRIC_PATTERNS_FOLDER="/home/jelle/.config/fabric/patterns"
    OBSIDIAN_OUTPUT_FOLDER="/mnt/c/Obsidian/BrainCave/Extra/textgenerator/templates/fabric"
    OBSIDIAN_INPUT_FOLDER="/mnt/c/Obsidian/BrainCave/d5 WDODelta/50-59 Programmeren en development/56 Generative AI en LLM/56.15 PromptsLibrary"
    YAML_OUTPUT_FOLDER=f"/mnt/c/Users/{windows_user}/AppData/Roaming/espanso/match"
else:
    windows_user = "cloud_dummy"
    FABRIC_PATTERNS_FOLDER="cloud_dummy"
    OBSIDIAN_OUTPUT_FOLDER="cloud_dummy"
    OBSIDIAN_INPUT_FOLDER="cloud_dummy"
    YAML_OUTPUT_FOLDER="cloud_dummy"

# Headings to extract from markdown files
BASE_WORDS = ['Identity', 'Purpose', 'Task', 'Goal']


# Qdrant database parameters
# TODO: deze paramater wordt nu niet in het script gebruikt, is nu hard coded, dit moet wel gebruikt worden
# Local:
# QDRANT_URL = "http://localhost:6333"
# COLLECTION_NAME = "fabric_patterns"
# Cloud:
QDRANT_URL = "https://91ed3a93-6135-4951-a624-1c8c2878240d.europe-west3-0.gcp.cloud.qdrant.io:6333"
COLLECTION_NAME = "fabric_patterns"

# Required fields for database points
# TODO: default trigger wordt nu twee keer gedefinieerd, oplossen
DEFAULT_TRIGGER = ";;fab"
REQUIRED_FIELDS = ['filename', 'content', 'purpose', 'filesize', 'trigger']
REQUIRED_FIELDS_DEFAULTS = {
    'trigger': ';;fab',
    'filesize': 0,
    'purpose': None  # Will be set to content if missing
}

# Embedding Model parameters voor Qdrant
USE_FASTEMBED = True
EMBED_MODEL = "fast-bge-small-en" 